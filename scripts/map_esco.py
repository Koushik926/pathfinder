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

# Below this label similarity we record no alignment rather than a bad one.
# An honest gap is worth more than a confident mismatch.
ACCEPT = 0.62


def normalise(text: str) -> str:
    return " ".join(text.lower().replace("-", " ").replace("/", " ").split())


def similarity(a: str, b: str) -> float:
    a, b = normalise(a), normalise(b)
    if a == b:
        return 1.0
    ratio = SequenceMatcher(None, a, b).ratio()
    # Whole-word containment ("python" inside "python programming") is a much
    # stronger signal than character overlap suggests.
    aw, bw = set(a.split()), set(b.split())
    if aw and bw and (aw <= bw or bw <= aw):
        ratio = max(ratio, 0.80)
    return ratio


def search(text: str, limit: int = 8) -> list[dict]:
    query = urllib.parse.urlencode(
        {"text": text, "language": "en", "type": "skill", "limit": limit, "full": "false"}
    )
    request = urllib.request.Request(
        f"{API}?{query}", headers={"Accept": "application/json", "User-Agent": "PathFinder/1.0"}
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.load(response)
    return payload.get("_embedded", {}).get("results", [])


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
            score = max(similarity(label, candidate) for candidate in queries)
            if best is None or score > best["similarity"]:
                best = {
                    "uri": result["uri"],
                    "esco_label": label,
                    "similarity": round(score, 4),
                    "matched_on": query,
                }
        time.sleep(0.15)                        # be a good citizen
        if best and best["similarity"] >= 0.95:
            break                               # exact hit; stop asking
    return best


def main() -> int:
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
    print(f"\n{len(aligned)}/{len(skills)} aligned -> {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
