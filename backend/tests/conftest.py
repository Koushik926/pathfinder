import warnings

import pytest

# See app/main.py — spurious Accelerate/BLAS warnings on macOS + numpy 2.x.
warnings.filterwarnings("ignore", message=".*encountered in matmul.*", category=RuntimeWarning)

from app.ml.profiler import Completion, LearnerProfile


@pytest.fixture
def novice():
    return LearnerProfile(
        id="novice", role_id="data-scientist", goal_text="become a data scientist",
        experience_level=1, hours_per_week=8,
    )


@pytest.fixture
def intermediate():
    return LearnerProfile(
        id="mid", role_id="data-scientist",
        goal_text="become a data scientist working on business problems",
        experience_level=2, hours_per_week=10,
        preferred_modalities=["interactive"],
        completed=[
            Completion("py-101", 20), Completion("py-103", 14),
            Completion("da-101", 8), Completion("da-102", 4),
            Completion("sql-101", 2, 0.9),
        ],
    )
