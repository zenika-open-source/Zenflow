"""Tests for guidelines_context — verifies correct paths are returned per tool."""

from __future__ import annotations

import pytest

from zenflow.core.guidelines import guidelines_context

EXPECTED_KEYS = {
    "backend_arch",
    "frontend_arch",
    "review_backend",
    "review_frontend",
    "documentation_backend",
    "documentation_frontend",
    "conventions",
    "project_context",
}


@pytest.mark.parametrize("tool", ["copilot", "opencode", "claude"])
def test_guidelines_context_returns_all_keys(tool: str) -> None:
    """All tools must return the full set of expected guideline keys."""
    ctx = guidelines_context(tool)
    assert ctx.keys() == EXPECTED_KEYS


@pytest.mark.parametrize(
    "key,expected",
    [
        ("backend_arch", ".github/skills/backend/references/architecture.md"),
        ("frontend_arch", ".github/skills/frontend/references/architecture.md"),
        ("review_backend", ".github/skills/reviewer/references/review-backend.md"),
        ("review_frontend", ".github/skills/reviewer/references/review-frontend.md"),
        ("documentation_backend", ".github/skills/documentation/references/documentation-backend.md"),
        ("documentation_frontend", ".github/skills/documentation/references/documentation-frontend.md"),
        ("conventions", ".github/skills/git/references/conventions.md"),
        ("project_context", ".github/copilot-instructions.md"),
    ],
)
def test_copilot_paths(key: str, expected: str) -> None:
    """Copilot paths reference .github/skills/<skill>/references/, same shape as OpenCode/Claude."""
    assert guidelines_context("copilot")[key] == expected


@pytest.mark.parametrize(
    "key,expected",
    [
        ("backend_arch", ".opencode/skills/backend/references/architecture.md"),
        ("frontend_arch", ".opencode/skills/frontend/references/architecture.md"),
        ("review_backend", ".opencode/skills/reviewer/references/review-backend.md"),
        ("review_frontend", ".opencode/skills/reviewer/references/review-frontend.md"),
        ("documentation_backend", ".opencode/skills/documentation/references/documentation-backend.md"),
        ("documentation_frontend", ".opencode/skills/documentation/references/documentation-frontend.md"),
        ("conventions", ".opencode/skills/git/references/conventions.md"),
    ],
)
def test_opencode_paths(key: str, expected: str) -> None:
    """OpenCode paths reference .opencode/skills/<skill>/references/."""
    assert guidelines_context("opencode")[key] == expected


@pytest.mark.parametrize(
    "key,expected",
    [
        ("backend_arch", ".claude/skills/backend/references/architecture.md"),
        ("frontend_arch", ".claude/skills/frontend/references/architecture.md"),
        ("review_backend", ".claude/skills/reviewer/references/review-backend.md"),
        ("review_frontend", ".claude/skills/reviewer/references/review-frontend.md"),
        ("documentation_backend", ".claude/skills/documentation/references/documentation-backend.md"),
        ("documentation_frontend", ".claude/skills/documentation/references/documentation-frontend.md"),
        ("conventions", ".claude/skills/git/references/conventions.md"),
    ],
)
def test_claude_paths(key: str, expected: str) -> None:
    """Claude paths reference .claude/skills/<skill>/references/."""
    assert guidelines_context("claude")[key] == expected


def test_unknown_tool_raises() -> None:
    """An unrecognised tool name must raise ValueError."""
    with pytest.raises(ValueError, match="Unknown tool"):
        guidelines_context("vscode")
