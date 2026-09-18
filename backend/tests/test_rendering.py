"""Tests for Jinja2 template rendering — agents and guidelines."""

from __future__ import annotations

import pytest
from jinja2 import Environment

from zenflow.core.guidelines import guidelines_context
from zenflow.core.rendering import make_env, render_template

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

ALL_AGENTS = [
    "backend",
    "frontend",
    "reviewer",
    "documentation",
    "orchestrator",
    "product-requirements",
    "static-prototyping",
    "dynamic-prototyping",
    "retrodoc-architecture",
]

ALL_TOOLS = ["copilot", "opencode", "claude"]


def _render_agent(
    env: Environment,
    agent_name: str,
    tool: str,
    *,
    skill_mode: bool,
) -> str:
    """Render an agent template and return the output string."""
    ctx = {
        "guidelines": guidelines_context(tool),
        "skill_mode": skill_mode,
    }
    return render_template(env, f"agents/{agent_name}.md.j2", ctx)


# ---------------------------------------------------------------------------
# No unrendered Jinja tags in any output
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("agent", ALL_AGENTS)
@pytest.mark.parametrize("tool", ALL_TOOLS)
@pytest.mark.parametrize("skill_mode", [True, False])
def test_no_unrendered_jinja(
    repo_root: str,
    agent: str,
    tool: str,
    skill_mode: bool,
) -> None:
    """Rendered output must contain no leftover {{ }} or {% %} tags."""
    env = make_env(repo_root)
    result = _render_agent(env, agent, tool, skill_mode=skill_mode)
    assert "{{" not in result, f"Unrendered {{{{ in {agent}/{tool}/skill_mode={skill_mode}"
    assert "{%" not in result, f"Unrendered {{%  in {agent}/{tool}/skill_mode={skill_mode}"


# ---------------------------------------------------------------------------
# Handoffs block — present for Copilot, absent for skills
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("agent", ALL_AGENTS)
def test_copilot_agent_has_handoffs(repo_root: str, agent: str) -> None:
    """Copilot agent output (skill_mode=False) must include the handoffs: block."""
    env = make_env(repo_root)
    result = _render_agent(env, agent, "copilot", skill_mode=False)
    assert "handoffs:" in result


@pytest.mark.parametrize("agent", ALL_AGENTS)
@pytest.mark.parametrize("tool", ALL_TOOLS)
def test_skill_has_no_handoffs_block(repo_root: str, agent: str, tool: str) -> None:
    """Skill output (skill_mode=True) must not contain the handoffs: YAML block."""
    env = make_env(repo_root)
    result = _render_agent(env, agent, tool, skill_mode=True)
    assert "handoffs:" not in result


# ---------------------------------------------------------------------------
# Next Steps footer — present in skills, absent for Copilot agents
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("agent", ALL_AGENTS)
@pytest.mark.parametrize("tool", ALL_TOOLS)
def test_skill_has_next_steps(repo_root: str, agent: str, tool: str) -> None:
    """Skill output (skill_mode=True) must include a ## Next Steps section."""
    env = make_env(repo_root)
    result = _render_agent(env, agent, tool, skill_mode=True)
    assert "## Next Steps" in result


@pytest.mark.parametrize("agent", ALL_AGENTS)
def test_copilot_agent_has_no_next_steps(repo_root: str, agent: str) -> None:
    """Copilot agent output (skill_mode=False) must not include ## Next Steps."""
    env = make_env(repo_root)
    result = _render_agent(env, agent, "copilot", skill_mode=False)
    assert "## Next Steps" not in result


# ---------------------------------------------------------------------------
# tools / user-invocable only for Copilot
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("agent", ALL_AGENTS)
def test_copilot_agent_has_tools_and_user_invocable(repo_root: str, agent: str) -> None:
    """Copilot agent output must include argument-hint, tools: and user-invocable: frontmatter."""
    env = make_env(repo_root)
    result = _render_agent(env, agent, "copilot", skill_mode=False)
    assert "argument-hint:" in result
    assert "tools:" in result
    assert "user-invocable:" in result


@pytest.mark.parametrize("agent", ALL_AGENTS)
@pytest.mark.parametrize("tool", ["opencode", "claude"])
def test_skill_agent_has_no_tools_or_user_invocable(repo_root: str, agent: str, tool: str) -> None:
    """Skill agent output must not include argument-hint, tools: or user-invocable: frontmatter."""
    env = make_env(repo_root)
    result = _render_agent(env, agent, tool, skill_mode=True)
    assert "argument-hint:" not in result
    assert "tools:" not in result
    assert "user-invocable:" not in result


# ---------------------------------------------------------------------------
# Guideline paths resolve to the correct tool-specific values
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "tool,expected_arch",
    [
        ("copilot", ".github/skills/backend/references/architecture.md"),
        ("opencode", ".opencode/skills/backend/references/architecture.md"),
        ("claude", ".claude/skills/backend/references/architecture.md"),
    ],
)
def test_backend_agent_arch_path(repo_root: str, tool: str, expected_arch: str) -> None:
    """Backend agent must reference the correct architecture guideline per tool."""
    env = make_env(repo_root)
    result = _render_agent(env, "backend", tool, skill_mode=False)
    assert expected_arch in result


@pytest.mark.parametrize(
    "tool,expected_arch",
    [
        ("copilot", ".github/skills/frontend/references/architecture.md"),
        ("opencode", ".opencode/skills/frontend/references/architecture.md"),
        ("claude", ".claude/skills/frontend/references/architecture.md"),
    ],
)
def test_frontend_agent_arch_path(repo_root: str, tool: str, expected_arch: str) -> None:
    """Frontend agent must reference the correct architecture guideline per tool."""
    env = make_env(repo_root)
    result = _render_agent(env, "frontend", tool, skill_mode=False)
    assert expected_arch in result


@pytest.mark.parametrize(
    "tool,expected_review",
    [
        ("copilot", ".github/skills/reviewer/references/review-backend.md"),
        ("opencode", ".opencode/skills/reviewer/references/review-backend.md"),
        ("claude", ".claude/skills/reviewer/references/review-backend.md"),
    ],
)
def test_reviewer_agent_review_path(repo_root: str, tool: str, expected_review: str) -> None:
    """Reviewer agent must reference the correct review guideline per tool."""
    env = make_env(repo_root)
    result = _render_agent(env, "reviewer", tool, skill_mode=False)
    assert expected_review in result


@pytest.mark.parametrize(
    "tool,expected_ctx",
    [
        ("copilot", ".github/copilot-instructions.md"),
        ("opencode", "AGENTS.md"),
        ("claude", "CLAUDE.md"),
    ],
)
def test_documentation_agent_project_context(repo_root: str, tool: str, expected_ctx: str) -> None:
    """Documentation agent must reference the correct project context file per tool."""
    env = make_env(repo_root)
    result = _render_agent(env, "documentation", tool, skill_mode=False)
    assert expected_ctx in result


# ---------------------------------------------------------------------------
# Guideline template rendering
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "template,expected_partial_content",
    [
        ("guidelines/backend/java-spring-boot.md.j2", "Backend Implementation Checklist"),
        ("guidelines/backend/python-fastapi.md.j2", "Backend Implementation Checklist"),
        ("guidelines/backend/golang-gin.md.j2", "Backend Implementation Checklist"),
        ("guidelines/backend/python.md.j2", "Backend Implementation Checklist"),
        ("guidelines/backend/java.md.j2", "Backend Implementation Checklist"),
        ("guidelines/backend/golang.md.j2", "Backend Implementation Checklist"),
        ("guidelines/frontend/react-typescript.md.j2", "Frontend Implementation Checklist"),
        ("guidelines/frontend/nextjs-app-router.md.j2", "Frontend Implementation Checklist"),
    ],
)
def test_guideline_templates_include_partials(
    base_env: Environment, template: str, expected_partial_content: str
) -> None:
    """Guideline templates must inline their partials."""
    ctx = {"guidelines": guidelines_context("copilot")}
    result = render_template(base_env, template, ctx)
    assert expected_partial_content in result
    assert "{%" not in result


@pytest.mark.parametrize(
    "tool,expected_arch",
    [
        ("copilot", ".github/skills/backend/references/architecture.md"),
        ("opencode", ".opencode/skills/backend/references/architecture.md"),
        ("claude", ".claude/skills/backend/references/architecture.md"),
    ],
)
def test_review_backend_guideline_arch_path(base_env: Environment, tool: str, expected_arch: str) -> None:
    """Review backend guideline must reference the correct architecture path per tool."""
    ctx = {"guidelines": guidelines_context(tool)}
    result = render_template(base_env, "guidelines/review/backend.md.j2", ctx)
    assert expected_arch in result
    assert "{{" not in result
