"""Accessibility affordances that must not silently disappear.

These are source-level checks, not a substitute for a screen-reader pass. They
exist because this exact class of regression already happened once: the focus
ring was written correctly, referenced `theme('colors.accent')` — which is an
object, not a colour — and Tailwind dropped the entire rule from the built
stylesheet with nothing but a vague warning. The product shipped a keyboard
focus indicator that did not exist.
"""

from __future__ import annotations

import json
import pathlib
import re

import pytest

FRONTEND = pathlib.Path(__file__).resolve().parents[2] / "frontend"
CSS = (FRONTEND / "src" / "index.css").read_text()
CONFIG = (FRONTEND / "tailwind.config.js").read_text()


def source(*parts: str) -> str:
    return (FRONTEND / "src" / pathlib.Path(*parts)).read_text()


@pytest.mark.parametrize(
    "affordance,pattern",
    [
        ("visible keyboard focus", r":focus-visible\s*\{[^}]*outline:"),
        ("screen-reader-only text", r"\.sr-only\s*\{"),
        ("skip link", r"\.skip-link\s*\{"),
        ("reduced-motion support", r"@media \(prefers-reduced-motion: reduce\)"),
    ],
)
def test_global_affordance_is_present(affordance, pattern):
    assert re.search(pattern, CSS), f"{affordance} is missing from index.css"


def test_theme_lookups_resolve_to_a_value_not_an_object():
    """The bug that shipped a focus ring nobody could see.

    `theme('colors.accent')` where `accent` is `{DEFAULT, dim, glow}` yields an
    object; Tailwind then discards the whole declaration block. Every colour
    lookup must name a leaf.
    """
    for lookup in re.findall(r"theme\(['\"]colors\.([a-zA-Z0-9_.-]+)['\"]\)", CSS):
        leaf = lookup.split(".")[-1]
        assert leaf == "DEFAULT" or re.search(rf"\b{re.escape(leaf)}\s*:\s*['\"]#", CONFIG), (
            f"theme('colors.{lookup}') does not resolve to a colour value; "
            "Tailwind will drop the rule silently"
        )


def test_the_transcript_announces_new_replies():
    """A chat that does not announce its replies is unusable non-visually."""
    chat = source("components", "Chat.jsx")
    assert 'role="log"' in chat
    assert 'aria-live="polite"' in chat
    assert "tabIndex={0}" in chat, "the scrollable transcript is not keyboard-reachable"


def test_speaker_is_identified_without_relying_on_position():
    """Left vs right is the only visual cue for who said what."""
    assert "PathFinder said: " in source("components", "Chat.jsx")


def test_state_glyphs_are_hidden_and_spelled_out():
    """'✓' and '○' carry meaning that a screen reader cannot infer."""
    chat = source("components", "Chat.jsx")
    assert 'aria-hidden="true"' in chat
    assert "still needed" in chat and "answered" in chat


def test_the_icon_only_complete_button_says_what_it_does():
    roadmap = source("components", "Roadmap.jsx")
    assert "aria-label={done ?" in roadmap
    assert "aria-pressed={done}" in roadmap


def test_the_message_input_has_a_label():
    assert 'htmlFor="chat-input"' in source("components", "Chat.jsx")


def test_there_is_a_way_past_the_conversation():
    app = source("App.jsx")
    assert 'className="skip-link"' in app
    assert 'href="#roadmap"' in app and 'id="roadmap"' in app
