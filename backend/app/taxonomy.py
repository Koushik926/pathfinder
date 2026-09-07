"""Where PathFinder's skills sit relative to a public standard.

116 hand-authored skills is a defensible size for a demo catalog and an
indefensible answer to "where did these come from?". ESCO — the European
Skills, Competences, Qualifications and Occupations classification — is the
EU's public standard, with a stable URI per concept.

Aligning to it turns our taxonomy from an invention into a *view* of a
standard one, and makes ingesting more of ESCO a data load rather than a
rewrite.

The alignment is computed offline by ``scripts/map_esco.py`` and committed as
data. Nothing here touches the network: the service keeps working, the build
stays byte-reproducible, and the demo never waits on Brussels.

The gaps are as informative as the matches. ESCO classifies occupational
competences, so it has concepts for statistics, natural language processing
and cyber security — and none at all for Next.js, RAG or diffusion models.
That is the standard's coverage boundary, not a defect in either taxonomy, and
it is the honest answer to how far a public standard gets you.
"""

from __future__ import annotations

import json
import pathlib

_PATH = pathlib.Path(__file__).parent / "data" / "skills_esco.json"


def _load() -> dict:
    try:
        return json.loads(_PATH.read_text())
    except (OSError, ValueError):
        # An absent or unreadable mapping is a missing annotation, never a
        # reason for the service to fail to start.
        return {"mapping": {}, "unmapped": [], "taxonomy": None, "source": None}


_DOC = _load()
MAPPING: dict[str, dict] = _DOC.get("mapping", {})
UNMAPPED: list[str] = _DOC.get("unmapped", [])


def concept_for(skill_id: str) -> dict | None:
    """The ESCO concept this skill was aligned to, if any."""
    return MAPPING.get(skill_id)


def summary(total_skills: int) -> dict:
    """Alignment coverage, for /meta — reported with its own gaps."""
    aligned = len(MAPPING)
    return {
        "standard": _DOC.get("taxonomy"),
        "source": _DOC.get("source"),
        "aligned": aligned,
        "total": total_skills,
        "coverage": round(aligned / total_skills, 3) if total_skills else 0.0,
        # Named, not hidden: these are the skills that move faster than the
        # standard does.
        "no_esco_concept": UNMAPPED,
    }
