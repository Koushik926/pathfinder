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
# Only exact agreement counts. Nothing else survived contact with the data.
#
# Three progressively cleverer scoring rules were tried here, and each one
# produced a fresh crop of confident nonsense:
#
#   character similarity      "Bash & Shell"      -> "airport terminal standards"
#   token overlap             "Computer Vision"   -> "computer programming"
#   overlap after stopwords   "BI Tools"          -> "follow reporting procedures"
#                             "UX Research"       -> "perform interviews"
#
# The last is the most instructive. Stripping filler words from an ESCO label
# shrinks "follow reporting procedures" to "reporting", at which point a short
# generic alias matches it exactly and scores 1.0. Every rule that tried to
# recognise *approximate* meaning through string overlap ended up recognising
# coincidence instead.
#
# So this does the one thing string comparison can actually justify: it claims
# an alignment only when the two names are the same name. That yields far fewer
# matches, and every one of them survives being read aloud to a skeptic — which
# is the only property that matters for a credibility claim.
ACCEPT = 1.0


def normalise(text: str) -> str:
    for symbol in ("-", "/", "&", ",", "(", ")", "."):
        text = text.replace(symbol, " ")
    return " ".join(text.lower().split())


def similarity(ours: str, theirs: str) -> float:
    return 1.0 if normalise(ours) == normalise(theirs) else 0.0


def candidate_names(skill: dict) -> list[str]:
    """The names we are willing to claim an alignment on.

    The skill's own name, plus any alias specific enough to stand alone. A
    one-word alias like "logic", "reporting" or "interviews" is a nickname in
    our catalog and a whole different concept in ESCO's, so aliases must carry
    at least two words to be trusted. The skill's own name is exempt, because
    "SQL", "C++" and "JavaScript" are unambiguous.
    """
    names = [skill["name"]]
    names += [alias for alias in skill.get("aliases", []) if len(normalise(alias).split()) >= 2]
    return names


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
    """Try each name we are willing to claim on, and keep the strongest hit."""
    queries = candidate_names(skill)
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
