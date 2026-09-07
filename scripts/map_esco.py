"""Align PathFinder's skill taxonomy to ESCO, the EU occupational standard.

PathFinder ships 116 hand-authored skills. That is a defensible size for a
demo catalog and an indefensible answer to "where did these come from?".

ESCO (European Skills, Competences, Qualifications and Occupations) is the
EU's public standard: 13,890 level-4 skills, each with a stable URI. Aligning
to it turns our taxonomy from an invention into a *view* of a standard one —
and makes ingesting the full taxonomy a data load rather than a rewrite.

This script runs once, offline, and commits its output. Nothing calls ESCO at
request time: the mapping is a file, so the build stays reproducible and the
service keeps working when Europe is asleep.

    python scripts/map_esco.py
"""

from __future__ import annotations

import json
import pathlib
import sys
import time
import urllib.parse
import urllib.request
from difflib import SequenceMatcher

API = "https://ec.europa.eu/esco/api/search"
ROOT = pathlib.Path(__file__).resolve().parents[1]
SKILLS = ROOT / "backend" / "app" / "data" / "skills.json"
OUT = ROOT / "backend" / "app" / "data" / "skills_esco.json"
# Raw ESCO responses, kept so the scoring rule can be retuned offline. The
# first pass of this script shipped nonsense matches; being able to re-score
# without re-querying is what made fixing that cheap.
CACHE = ROOT / "scripts" / ".esco-cache.json"
_cache: dict[str, list[dict]] = {}

# Below this label similarity we record no alignment rather than a bad one.
# An honest gap is worth more than a confident mismatch.
# Below this score we record no alignment rather than a bad one. An honest gap
# is worth far more than a confident mismatch — and the first version of this
# script proved it, cheerfully aligning "Bash & Shell" to "airport terminal
# standards" because one alias word appeared inside a longer label.
ACCEPT = 0.62

# Words that carry no discriminating meaning in an ESCO label. ESCO phrases
# skills as actions ("manage manufacturing documentation"), so leaving these in
# lets a shared verb masquerade as a topic match.
STOPWORDS = {
    "a", "an", "the", "and", "or", "of", "for", "in", "on", "to", "with",
    "manage", "prepare", "follow", "use", "using", "develop", "plan", "perform",
    "apply", "carry", "out", "provide", "ensure", "maintain", "conduct", "create",
    "work", "process", "processes", "procedures", "standards", "systems", "system",
    "principles", "methods", "techniques", "tools", "types", "skills",
}


def normalise(text: str) -> str:
    for symbol in ("-", "/", "&", ",", "(", ")", "."):
        text = text.replace(symbol, " ")
    return " ".join(text.lower().split())


def tokens(text: str) -> set[str]:
    return {word for word in normalise(text).split() if word not in STOPWORDS}


def similarity(ours: str, theirs: str) -> float:
    """How confident are we that these name the same competence?

    Token overlap, not character overlap. Character similarity is what produced
    the airport-terminal match: "bash shell" and "airport terminal standards"
    share a lot of letters and nothing else.
    """
    a, b = normalise(ours), normalise(theirs)
    if a == b:
        return 1.0

    ours_tokens, theirs_tokens = tokens(ours), tokens(theirs)
    if not ours_tokens or not theirs_tokens:
        return 0.0

    overlap = ours_tokens & theirs_tokens
    if not overlap:
        return 0.0

    # One shared word is not a match. "reinforcement learning" and "insert
    # reinforcement in mould" share a token; "computer vision" and "computer
    # programming" share a token; "cloud security" and "Parrot Security OS"
    # share a token. None of them share a meaning. Where either side is a
    # single concept word, only exact agreement counts.
    if len(ours_tokens) == 1 or len(theirs_tokens) == 1:
        return 1.0 if ours_tokens == theirs_tokens else 0.0

    # Jaccard over meaningful tokens: rewards agreement, penalises the extra
    # words that make a broad ESCO concept a poor fit for a specific skill.
    jaccard = len(overlap) / len(ours_tokens | theirs_tokens)

    # A multi-word name appearing as a contiguous phrase is strong evidence
    # ("machine learning" inside "machine learning algorithms"). A single word
    # inside a longer label is not evidence at all, which is the whole lesson
    # of the first two runs.
    if a in b:
        jaccard = max(jaccard, 0.85)

    # Two words in common out of three is still only one distinguishing word.
    # Require the overlap to carry most of *our* meaning, not just some of it.
    if len(overlap) / len(ours_tokens) < 0.5:
        return 0.0

    return jaccard

def search(text: str, limit: int = 8) -> list[dict]:
    if text in _cache:
        return _cache[text]
    query = urllib.parse.urlencode(
        {"text": text, "language": "en", "type": "skill", "limit": limit, "full": "false"}
    )
    request = urllib.request.Request(
        f"{API}?{query}", headers={"Accept": "application/json", "User-Agent": "PathFinder/1.0"}
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.load(response)
    results = payload.get("_embedded", {}).get("results", [])
    _cache[text] = [
        {"uri": r["uri"], "title": r.get("title", ""), "preferredLabel": r.get("preferredLabel")}
        for r in results
    ]
    return _cache[text]


def english(label) -> str:
    if isinstance(label, dict):
        value = label.get("en") or label.get("en-us") or ""
        return value[0] if isinstance(value, list) else value
    return label or ""


def best_match(skill: dict) -> dict | None:
    """Try the skill name, then each alias, and keep the strongest hit."""
    queries = [skill["name"], *skill.get("aliases", [])]
    best: dict | None = None

    for query in queries:
        try:
            results = search(query)
        except Exception as error:              # network is allowed to fail
            print(f"    ! {query}: {error}", file=sys.stderr)
            continue
        for result in results:
            label = english(result.get("preferredLabel")) or result.get("title", "")
            if not label:
                continue
            # Score the ESCO label against every name we know this skill by.
            score = max(similarity(candidate, label) for candidate in queries)
            if best is None or score > best["similarity"]:
                best = {
                    "uri": result["uri"],
                    "esco_label": label,
                    "similarity": round(score, 4),
                    "matched_on": query,
                }
        if query not in _cache:
            time.sleep(0.15)                    # be a good citizen
        if best and best["similarity"] >= 0.95:
            break                               # exact hit; stop asking
    return best


def main() -> int:
    global _cache
    if CACHE.exists():
        _cache = json.loads(CACHE.read_text())
        print(f"re-scoring {len(_cache)} cached ESCO queries — no network needed\n")
    skills = json.loads(SKILLS.read_text())
    aligned: dict[str, dict] = {}
    unmapped: list[str] = []

    for index, skill in enumerate(skills, 1):
        print(f"[{index:3d}/{len(skills)}] {skill['name']}")
        match = best_match(skill)
        if match and match["similarity"] >= ACCEPT:
            aligned[skill["id"]] = match
            print(f"          -> {match['esco_label']}  ({match['similarity']})")
        else:
            unmapped.append(skill["id"])
            shown = f" (best {match['similarity']}: {match['esco_label']})" if match else ""
            print(f"          -> no confident ESCO concept{shown}")

    document = {
        "taxonomy": "ESCO v1.2",
        "source": "https://ec.europa.eu/esco/api",
        "accept_threshold": ACCEPT,
        "total_skills": len(skills),
        "aligned": len(aligned),
        "unmapped": unmapped,
        "mapping": dict(sorted(aligned.items())),
    }
    OUT.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
    CACHE.write_text(json.dumps(_cache, indent=0, sort_keys=True))
    print(f"\n{len(aligned)}/{len(skills)} aligned -> {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
