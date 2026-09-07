"""Where PathFinder's skills sit relative to a public standard.

116 hand-authored skills is a defensible size for a demo catalog and an
indefensible answer to "where did these come from?". ESCO — the European
Skills, Competences, Qualifications and Occupations classification — is the
EU's public standard, with a stable URI per concept.

So we checked ours against it, and the honest result is that **10 of 116
skills have an unambiguous ESCO concept**. ESCO classifies occupational
competences: it has entries for statistics, natural language processing and
cyber security, and none at all for PyTorch, RAG, Kubernetes, React or
Next.js.

That is the finding, not a failure of the mapping. It is the coverage boundary
of a public standard against fast-moving technical skills, and it is also why
this project had to author its own prerequisite edges — no public dataset
carries them either.

Getting to an honest 10 took discarding three scoring rules that each produced
confident nonsense; ``scripts/map_esco.py`` records what they were and why
they failed. The rule that survived claims an alignment only when the two
names are the same name.

The alignment is computed offline and committed as data. Nothing here touches
the network: the service keeps working, the build stays byte-reproducible, and
the demo never waits on Brussels.
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
