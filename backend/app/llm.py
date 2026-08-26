"""Optional Claude integration.

PathFinder is designed to be fully functional with no API key: the ML layer
does the reasoning, and a deterministic template layer does the talking. This
module is a *quality upgrade*, not a dependency. Every entry point returns
``None`` on any failure — no key, package not installed, network down, rate
limited, malformed response — and every caller has a template fallback.

Claude is given two jobs, both chosen because they play to a language model's
strengths without letting it invent facts:

  parse_goal   read a messy sentence and fill in the profile slots. This is
               extraction, and it is checked against the catalog afterwards —
               a role or skill Claude returns that does not exist is dropped.
  narrate      rewrite facts the ML layer already computed into warmer prose.
               It is given the numbers and told not to add any others, so the
               explanation stays faithful to the actual ranking arithmetic.

Deliberately *not* given to Claude: choosing what to recommend, or ordering
the path. Those stay in the deterministic engines so results are reproducible
and defensible.
"""

from __future__ import annotations

import logging
import os
from typing import Literal

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "claude-opus-5"
# Keep the conversation responsive; these are short extraction/rewrite calls.
EFFORT = "low"
MAX_TOKENS = 2048


class GoalExtraction(BaseModel):
    """Profile slots Claude can fill from one free-text message."""

    role_hint: str = Field(description="Career role the learner is aiming at, in their own words. Empty string if not stated.")
    skills: list[str] = Field(default_factory=list, description="Specific technologies or skills the learner named.")
    experience_level: Literal["beginner", "intermediate", "advanced", "unknown"] = Field(description="Their self-described level.")
    hours_per_week: int = Field(description="Hours per week they can study. 0 if not stated.")
    known_topics: list[str] = Field(default_factory=list, description="Topics or tools they said they already know.")
    timeline_weeks: int = Field(description="Deadline in weeks, if they gave one. 0 otherwise.")
    clarification_needed: bool = Field(description="True if the message is too vague to plan from.")


PARSE_SYSTEM = """You extract structured learning-profile fields from a message a learner typed.

Rules:
- Only record what the learner actually said or clearly implied. Never invent a level, a deadline, or a skill.
- If they did not state something, use the empty/zero value for that field.
- `skills` and `known_topics` should be short canonical names ("PyTorch", "SQL", "React"), not sentences.
- Set clarification_needed to true only when the message gives you nothing to plan from at all."""

NARRATE_SYSTEM = """You are the voice of PathFinder, a learning-path assistant, writing for a student.

You will be given FACTS computed by PathFinder's recommendation engine. Your job is to express those facts naturally and encouragingly.

Absolute rules:
- Use only the numbers and names in the FACTS. Never introduce a course, skill, percentage, or duration that is not there.
- Never claim something is "proven" or "guaranteed".
- Be warm but brief: at most 4 short sentences, no headings, no bullet lists unless asked.
- Write in second person, present tense. No preamble like "Certainly" or "Here is"."""


class LLMClient:
    """Thin wrapper that fails soft in every direction."""

    def __init__(self) -> None:
        self.model = os.environ.get("ANTHROPIC_MODEL", DEFAULT_MODEL)
        self._client = None
        self._reason = ""

        api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
        if not api_key:
            self._reason = "ANTHROPIC_API_KEY is not set"
            return
        try:
            import anthropic
        except ImportError:
            self._reason = "the 'anthropic' package is not installed (pip install -e '.[llm]')"
            return
        try:
            self._client = anthropic.Anthropic(api_key=api_key)
        except Exception as exc:                     # noqa: BLE001 - never fatal
            self._reason = f"client init failed: {exc}"

    @property
    def available(self) -> bool:
        return self._client is not None

    @property
    def status(self) -> dict:
        return {
            "enabled": self.available,
            "model": self.model if self.available else None,
            "reason": "" if self.available else self._reason,
            "note": "PathFinder runs fully offline; Claude only enriches wording.",
        }

    # -- extraction ---------------------------------------------------------

    def parse_goal(self, message: str) -> GoalExtraction | None:
        """Fill profile slots from a free-text message, or None if unavailable."""
        if not self.available:
            return None
        try:
            response = self._client.messages.parse(
                model=self.model,
                max_tokens=MAX_TOKENS,
                system=PARSE_SYSTEM,
                output_config={"effort": EFFORT},
                output_format=GoalExtraction,
                messages=[{"role": "user", "content": message}],
            )
            return response.parsed_output
        except Exception as exc:                     # noqa: BLE001
            logger.warning("Claude goal parse failed, using local parser: %s", exc)
            return None

    # -- narration ----------------------------------------------------------

    def narrate(self, facts: str, instruction: str) -> str | None:
        """Rewrite computed facts as prose, or None if unavailable."""
        if not self.available:
            return None
        try:
            response = self._client.messages.create(
                model=self.model,
                max_tokens=MAX_TOKENS,
                system=NARRATE_SYSTEM,
                output_config={"effort": EFFORT},
                messages=[{
                    "role": "user",
                    "content": f"{instruction}\n\nFACTS:\n{facts}",
                }],
            )
            if response.stop_reason == "refusal":
                logger.warning("Claude declined to narrate; using template.")
                return None
            text = "".join(
                block.text for block in response.content if block.type == "text"
            ).strip()
            return text or None
        except Exception as exc:                     # noqa: BLE001
            logger.warning("Claude narration failed, using template: %s", exc)
            return None


LLM = LLMClient()
