"""Request and response models for the HTTP API."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class CompletionIn(BaseModel):
    item_id: str
    months_ago: float = 6.0
    score: float | None = Field(default=None, ge=0.0, le=1.0)


class ProfileIn(BaseModel):
    """Direct profile edit, used by the profile form as an alternative to chat."""

    name: str | None = None
    goal_text: str | None = None
    role_id: str | None = None
    experience_level: int | None = Field(default=None, ge=1, le=3)
    hours_per_week: float | None = Field(default=None, ge=1, le=60)
    preferred_modalities: list[str] | None = None
    interests: list[str] | None = None
    completed: list[CompletionIn] | None = None
    declared_skills: dict[str, float] | None = None
    goal_skills: dict[str, float] | None = None


class ChatIn(BaseModel):
    message: str = Field(min_length=1, max_length=2000)


class FeedbackIn(BaseModel):
    kind: Literal["completion", "reaction", "pace"]
    item_id: str | None = None
    score: float | None = Field(default=None, ge=0.0, le=1.0)
    reaction: Literal["too_easy", "too_hard", "not_interested", "loved"] | None = None
    hours_per_week: float | None = Field(default=None, ge=1, le=60)


class SessionOut(BaseModel):
    session_id: str
    profile: dict[str, Any]
    llm_enabled: bool


class ChatOut(BaseModel):
    reply: str
    intent: str
    options: list[dict[str, Any]]
    ready: bool
    missing_slots: list[str]
    profile_preview: dict[str, Any]
    llm_enabled: bool


class FeedbackOut(BaseModel):
    changes: list[str]
    regenerated: bool
    path: dict[str, Any] | None = None
