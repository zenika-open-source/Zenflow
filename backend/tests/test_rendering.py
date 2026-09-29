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
    "tech-migration",
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


@pytest.mark.parametrize("tool", ALL_TOOLS)
@pytest.mark.parametrize("skill_mode", [True, False])
def test_retrodoc_prompts_for_gortex_and_uses_architect_outputs(
    repo_root: str, tool: str, skill_mode: bool
) -> None:
    result = _render_agent(make_env(repo_root), "retrodoc-architecture", tool, skill_mode=skill_mode)
    normalized = " ".join(result.split())

    assert "Install gortex (recommended)" in result
    assert "Skip gortex and continue without graph" in normalized
    assert "Do not silently choose the fallback" in result
    assert "Run `gortex version` again to verify" in result
    assert "If they choose to skip, go to **Step 6**" in result
    assert "**Hard cap: 30 components.**" in result
    assert "single source of truth" in result
    assert "Same outputs via `Glob`/`Grep`/`Read`" in result
    assert "scale. Load" not in result
    for artifact in ("architecture.json", "architecture.html", "architecture.drawio", "architecture.mmd", "RETRODOC.md"):
        assert artifact in result
    assert "same model" in result
    assert "## Step 6 — Fallback without gortex" in result
    if skill_mode:
        assert "handoffs:" not in result
    else:
        assert "vscode/askQuestions" in result
        assert "handoffs:" in result


@pytest.mark.parametrize(
    "tool,expected_context",
    [
        ("copilot", ".github/copilot-instructions.md"),
        ("opencode", "AGENTS.md"),
        ("claude", "CLAUDE.md"),
    ],
)
@pytest.mark.parametrize("skill_mode", [True, False])
def test_tech_migration_preserves_planning_contract(
    repo_root: str, tool: str, expected_context: str, skill_mode: bool
) -> None:
    result = _render_agent(make_env(repo_root), "tech-migration", tool, skill_mode=skill_mode)

    assert "name: Tech Migration" in result
    assert "docs/plans/[migration-slug].md" in result
    assert f"Read `{expected_context}` if present" in result
    assert "do not require either to exist" in result
    for gate in range(8):
        assert f"### G{gate} -" in result
    assert "do not execute them" in result
    assert "neither establishes implementation or release" in result
    assert "tech-migration-planner" not in result
    if skill_mode:
        assert "## Next Steps" in result
        assert "tools:" not in result
    else:
        assert "## Next Steps" not in result
        assert "agent: Tech Migration" in result


@pytest.mark.parametrize("skill_mode", [True, False])
def test_orchestrator_routes_migrations_without_implementing(repo_root: str, skill_mode: bool) -> None:
    result = _render_agent(make_env(repo_root), "orchestrator", "copilot", skill_mode=skill_mode)

    assert "Tech Migration was installed" in result
    assert "Stop here" in result
    assert "G2 and later require their own owners" in result
    assert "### STEP 0 — Create Feature Plan" in result
    if skill_mode:
        assert "Load the installed **Tech Migration** skill" in result
    else:
        assert "agents: [Backend, Frontend, Documentation, Reviewer, Tech Migration]" in result
        assert "do not try to call a nonexistent custom agent" in result


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
