"""The committed catalog must match a fresh rebuild.

This guards a claim the README and the submission documentation both make:
rebuilding from source produces byte-identical artefacts. It caught a real
defect — CPython 3.12 switched sum() over floats to compensated summation, so
role-overlap scores differed in their last bits between interpreters, flipping
near-ties in a sort and changing which items survived a cutoff. The build now
uses math.fsum with rounding and a deterministic tie-break; this test fails if
that ever regresses, or if someone edits a seed without rebuilding.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

DATA_DIR = Path(__file__).resolve().parent.parent / "app" / "data"
ARTEFACTS = ("skills.json", "catalog.json", "roles.json", "interactions.json")


@pytest.fixture(scope="module")
def rebuilt(tmp_path_factory):
    """Rebuild the artefacts into a scratch directory and return their bytes."""
    committed = {name: (DATA_DIR / name).read_bytes() for name in ARTEFACTS}
    backup = tmp_path_factory.mktemp("backup")
    for name, payload in committed.items():
        (backup / name).write_bytes(payload)

    subprocess.run(
        [sys.executable, "-m", "app.seed.build"],
        cwd=DATA_DIR.parent.parent,
        check=True,
        capture_output=True,
    )
    fresh = {name: (DATA_DIR / name).read_bytes() for name in ARTEFACTS}

    # Restore, so a rebuild during testing never leaves the tree dirty.
    for name, payload in committed.items():
        (DATA_DIR / name).write_bytes(payload)

    return committed, fresh


@pytest.mark.parametrize("name", ARTEFACTS)
def test_committed_artefact_matches_fresh_rebuild(rebuilt, name):
    committed, fresh = rebuilt
    assert committed[name] == fresh[name], (
        f"{name} differs from a fresh build — rerun `python -m app.seed.build` "
        f"and commit the result, or the build has become non-deterministic."
    )


def test_interaction_log_is_internally_consistent():
    """Co-occurrence counts must never exceed the items' own session counts."""
    data = json.loads((DATA_DIR / "interactions.json").read_text())
    counts, co_counts = data["item_counts"], data["co_counts"]
    for a, partners in co_counts.items():
        for b, co in partners.items():
            assert co <= min(counts[a], counts[b]), f"{a}/{b}: co={co} exceeds item counts"
            assert co_counts[b][a] == co, f"{a}/{b} co-occurrence is not symmetric"
