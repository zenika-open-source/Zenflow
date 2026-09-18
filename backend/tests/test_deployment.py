"""Integration tests for deploy_agents and deploy_guidelines — full file output."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from zenflow.core.deployment import (
    deploy_agents,
    deploy_guidelines_to_skills,
    resolve_agent_ids,
)

BACKEND_ARCH = "java-spring-boot.md.j2"
FRONTEND_ARCH = "react-typescript.md.j2"
BACKEND_DOC = "java-spring-boot.md.j2"
FRONTEND_DOC = "react-typescript.md.j2"

ALL_AGENT_NAMES = {
    "backend",
    "frontend",
    "reviewer",
    "documentation",
    "orchestrator",
    "product-requirements",
    "static-prototyping",
    "dynamic-prototyping",
    "retrodoc-architecture",
}


# ---------------------------------------------------------------------------
# deploy_agents — Copilot (skill_mode=False)
# ---------------------------------------------------------------------------


def test_copilot_agents_creates_all_agent_files(repo_root: str, tmp_target: Path) -> None:
    """deploy_agents for Copilot must produce one .agent.md file per agent."""
    agents_src = os.path.join(repo_root, "templates", "agents")
    target_dir = tmp_target / ".github" / "agents"
    deploy_agents(agents_src, str(target_dir), repo_root, tool="copilot", skill_mode=False)

    produced = {f.stem.replace(".agent", "") for f in target_dir.glob("*.agent.md")}
    assert produced == ALL_AGENT_NAMES


def test_copilot_agents_contain_handoffs(repo_root: str, tmp_target: Path) -> None:
    """Copilot agent files must retain the handoffs: YAML block."""
    agents_src = os.path.join(repo_root, "templates", "agents")
    target_dir = tmp_target / ".github" / "agents"
    deploy_agents(agents_src, str(target_dir), repo_root, tool="copilot", skill_mode=False)

    for agent_file in target_dir.glob("*.agent.md"):
        assert "handoffs:" in agent_file.read_text(), f"Missing handoffs in {agent_file.name}"


def test_copilot_agents_have_no_jinja_tags(repo_root: str, tmp_target: Path) -> None:
    """Copilot agent files must contain no raw Jinja tags."""
    agents_src = os.path.join(repo_root, "templates", "agents")
    target_dir = tmp_target / ".github" / "agents"
    deploy_agents(agents_src, str(target_dir), repo_root, tool="copilot", skill_mode=False)

    for agent_file in target_dir.glob("*.agent.md"):
        content = agent_file.read_text()
        assert "{{" not in content, f"Unrendered {{{{ in {agent_file.name}"
        assert "{%" not in content, f"Unrendered {{%  in {agent_file.name}"


# ---------------------------------------------------------------------------
# deploy_agents — OpenCode skills (skill_mode=True)
# ---------------------------------------------------------------------------


def test_opencode_skills_creates_skill_dirs(repo_root: str, tmp_target: Path) -> None:
    """deploy_agents for OpenCode must create one SKILL.md per agent under skills/."""
    agents_src = os.path.join(repo_root, "templates", "agents")
    skills_dir = tmp_target / ".opencode" / "skills"
    deploy_agents(agents_src, str(skills_dir), repo_root, tool="opencode", skill_mode=True)

    produced = {d.name for d in skills_dir.iterdir() if d.is_dir()}
    assert produced == ALL_AGENT_NAMES

    for name in ALL_AGENT_NAMES:
        assert (skills_dir / name / "SKILL.md").exists(), f"Missing SKILL.md for {name}"


def test_opencode_skills_have_no_handoffs_block(repo_root: str, tmp_target: Path) -> None:
    """OpenCode SKILL.md files must not contain the handoffs: YAML block."""
    agents_src = os.path.join(repo_root, "templates", "agents")
    skills_dir = tmp_target / ".opencode" / "skills"
    deploy_agents(agents_src, str(skills_dir), repo_root, tool="opencode", skill_mode=True)

    for name in ALL_AGENT_NAMES:
        content = (skills_dir / name / "SKILL.md").read_text()
        assert "handoffs:" not in content, f"handoffs: found in {name}/SKILL.md"


def test_opencode_skills_have_next_steps(repo_root: str, tmp_target: Path) -> None:
    """OpenCode SKILL.md files must include a ## Next Steps section."""
    agents_src = os.path.join(repo_root, "templates", "agents")
    skills_dir = tmp_target / ".opencode" / "skills"
    deploy_agents(agents_src, str(skills_dir), repo_root, tool="opencode", skill_mode=True)

    for name in ALL_AGENT_NAMES:
        content = (skills_dir / name / "SKILL.md").read_text()
        assert "## Next Steps" in content, f"Missing Next Steps in {name}/SKILL.md"


def test_opencode_skills_use_correct_guideline_paths(repo_root: str, tmp_target: Path) -> None:
    """OpenCode backend skill must reference .opencode/skills/ guideline paths."""
    agents_src = os.path.join(repo_root, "templates", "agents")
    skills_dir = tmp_target / ".opencode" / "skills"
    deploy_agents(agents_src, str(skills_dir), repo_root, tool="opencode", skill_mode=True)

    backend = (skills_dir / "backend" / "SKILL.md").read_text()
    assert ".opencode/skills/backend/references/architecture.md" in backend
    assert ".github/guidelines" not in backend


def test_claude_skills_use_correct_guideline_paths(repo_root: str, tmp_target: Path) -> None:
    """Claude Code backend skill must reference .claude/skills/ guideline paths."""
    agents_src = os.path.join(repo_root, "templates", "agents")
    skills_dir = tmp_target / ".claude" / "skills"
    deploy_agents(agents_src, str(skills_dir), repo_root, tool="claude", skill_mode=True)

    backend = (skills_dir / "backend" / "SKILL.md").read_text()
    assert ".claude/skills/backend/references/architecture.md" in backend
    assert ".github/guidelines" not in backend


def test_copilot_skills_use_correct_guideline_paths(repo_root: str, tmp_target: Path) -> None:
    """Copilot backend skill must reference .github/skills/ guideline paths, not .github/guidelines/."""
    agents_src = os.path.join(repo_root, "templates", "agents")
    skills_dir = tmp_target / ".github" / "skills"
    deploy_agents(agents_src, str(skills_dir), repo_root, tool="copilot", skill_mode=True)

    backend = (skills_dir / "backend" / "SKILL.md").read_text()
    assert ".github/skills/backend/references/architecture.md" in backend
    assert ".github/guidelines" not in backend


# ---------------------------------------------------------------------------
# deploy_agents — agent_ids filtering
# ---------------------------------------------------------------------------


def test_deploy_agents_filters_to_selected_ids(repo_root: str, tmp_target: Path) -> None:
    """Only the selected agent ids are deployed — nothing else is force-included."""
    agents_src = os.path.join(repo_root, "templates", "agents")
    target_dir = tmp_target / ".github" / "agents"
    deploy_agents(
        agents_src,
        str(target_dir),
        repo_root,
        tool="copilot",
        skill_mode=False,
        agent_ids=frozenset({"product-requirements", "static-prototyping"}),
    )

    produced = {f.stem.replace(".agent", "") for f in target_dir.glob("*.agent.md")}
    assert produced == {"product-requirements", "static-prototyping"}


def test_deploy_agents_empty_selection_deploys_nothing(repo_root: str, tmp_target: Path) -> None:
    """An empty agent_ids selection deploys no agents at all."""
    agents_src = os.path.join(repo_root, "templates", "agents")
    target_dir = tmp_target / ".github" / "agents"
    deploy_agents(
        agents_src, str(target_dir), repo_root, tool="copilot", skill_mode=False, agent_ids=frozenset()
    )

    produced = {f.stem.replace(".agent", "") for f in target_dir.glob("*.agent.md")}
    assert produced == set()


def test_deploy_agents_none_deploys_all(repo_root: str, tmp_target: Path) -> None:
    """agent_ids=None (the default) preserves the old deploy-everything behavior."""
    agents_src = os.path.join(repo_root, "templates", "agents")
    target_dir = tmp_target / ".github" / "agents"
    deploy_agents(agents_src, str(target_dir), repo_root, tool="copilot", skill_mode=False, agent_ids=None)

    produced = {f.stem.replace(".agent", "") for f in target_dir.glob("*.agent.md")}
    assert produced == ALL_AGENT_NAMES


def test_resolve_agent_ids_maps_code_review_to_reviewer() -> None:
    """The 'code-review' skill id maps to the 'reviewer' agent id."""
    assert resolve_agent_ids(["code-review", "backend"]) == frozenset({"reviewer", "backend"})


# ---------------------------------------------------------------------------
# deploy_guidelines_to_skills
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "tool,base",
    [
        ("copilot", ".github/skills"),
        ("opencode", ".opencode/skills"),
        ("claude", ".claude/skills"),
    ],
)
def test_deploy_guidelines_to_skills_creates_references(repo_root: str, tmp_target: Path, tool: str, base: str) -> None:
    """deploy_guidelines_to_skills must produce references/ files under each skill."""
    skills_dir = tmp_target / base.lstrip("./").replace("/", os.sep)

    deploy_guidelines_to_skills(
        str(skills_dir),
        repo_root,
        BACKEND_ARCH,
        FRONTEND_ARCH,
        BACKEND_DOC,
        FRONTEND_DOC,
        include_conventions=True,
        tool=tool,
    )

    expected = [
        skills_dir / "backend" / "references" / "architecture.md",
        skills_dir / "frontend" / "references" / "architecture.md",
        skills_dir / "reviewer" / "references" / "review-backend.md",
        skills_dir / "reviewer" / "references" / "review-frontend.md",
        skills_dir / "documentation" / "references" / "documentation-backend.md",
        skills_dir / "documentation" / "references" / "documentation-frontend.md",
        skills_dir / "git" / "references" / "conventions.md",
    ]
    for path in expected:
        assert path.exists(), f"Missing: {path.relative_to(tmp_target)}"


@pytest.mark.parametrize("tool", ["copilot", "opencode", "claude"])
def test_deploy_guidelines_to_skills_no_github_paths(repo_root: str, tmp_target: Path, tool: str) -> None:
    """Skill reference files must not contain any .github/guidelines paths."""
    base = {"copilot": ".github/skills", "opencode": ".opencode/skills", "claude": ".claude/skills"}[tool]
    skills_dir = tmp_target / base.lstrip("./").replace("/", os.sep)

    deploy_guidelines_to_skills(
        str(skills_dir),
        repo_root,
        BACKEND_ARCH,
        FRONTEND_ARCH,
        "",
        "",
        include_conventions=False,
        tool=tool,
    )

    for ref_file in skills_dir.rglob("*.md"):
        content = ref_file.read_text()
        assert ".github/guidelines" not in content, f".github/guidelines found in {ref_file.relative_to(tmp_target)}"


@pytest.mark.parametrize("tool", ["copilot", "opencode", "claude"])
def test_deploy_guidelines_to_skills_no_jinja_tags(repo_root: str, tmp_target: Path, tool: str) -> None:
    """Skill reference files must contain no raw Jinja tags."""
    base = {"copilot": ".github/skills", "opencode": ".opencode/skills", "claude": ".claude/skills"}[tool]
    skills_dir = tmp_target / base.lstrip("./").replace("/", os.sep)

    deploy_guidelines_to_skills(
        str(skills_dir),
        repo_root,
        BACKEND_ARCH,
        FRONTEND_ARCH,
        BACKEND_DOC,
        FRONTEND_DOC,
        include_conventions=True,
        tool=tool,
    )

    for ref_file in skills_dir.rglob("*.md"):
        content = ref_file.read_text()
        assert "{{" not in content, f"Unrendered {{{{ in {ref_file.name}"
        assert "{%" not in content, f"Unrendered {{%  in {ref_file.name}"


@pytest.mark.parametrize(
    "tool,base",
    [
        ("copilot", ".github/skills"),
        ("opencode", ".opencode/skills"),
        ("claude", ".claude/skills"),
    ],
)
def test_deploy_guidelines_to_skills_omits_backend_when_skipped(
    repo_root: str, tmp_target: Path, tool: str, base: str
) -> None:
    """deploy_guidelines_to_skills must omit backend references when arch file is empty."""
    skills_dir = tmp_target / base.lstrip("./").replace("/", os.sep)

    deploy_guidelines_to_skills(
        str(skills_dir),
        repo_root,
        backend_arch_file="",
        frontend_arch_file=FRONTEND_ARCH,
        backend_doc_file="",
        frontend_doc_file="",
        include_conventions=False,
        tool=tool,
    )

    assert not (skills_dir / "backend" / "references" / "architecture.md").exists()
    assert not (skills_dir / "reviewer" / "references" / "review-backend.md").exists()
    assert (skills_dir / "frontend" / "references" / "architecture.md").exists()
    assert (skills_dir / "reviewer" / "references" / "review-frontend.md").exists()


@pytest.mark.parametrize(
    "tool,base",
    [
        ("copilot", ".github/skills"),
        ("opencode", ".opencode/skills"),
        ("claude", ".claude/skills"),
    ],
)
def test_deploy_guidelines_to_skills_omits_frontend_when_skipped(
    repo_root: str, tmp_target: Path, tool: str, base: str
) -> None:
    """deploy_guidelines_to_skills must omit frontend references when arch file is empty."""
    skills_dir = tmp_target / base.lstrip("./").replace("/", os.sep)

    deploy_guidelines_to_skills(
        str(skills_dir),
        repo_root,
        backend_arch_file=BACKEND_ARCH,
        frontend_arch_file="",
        backend_doc_file="",
        frontend_doc_file="",
        include_conventions=False,
        tool=tool,
    )

    assert not (skills_dir / "frontend" / "references" / "architecture.md").exists()
    assert not (skills_dir / "reviewer" / "references" / "review-frontend.md").exists()
    assert (skills_dir / "backend" / "references" / "architecture.md").exists()
    assert (skills_dir / "reviewer" / "references" / "review-backend.md").exists()


def test_deploy_guidelines_to_skills_respects_agent_ids(repo_root: str, tmp_target: Path) -> None:
    """References must only be written into skill folders selected via agent_ids."""
    skills_dir = tmp_target / ".github" / "skills"

    deploy_guidelines_to_skills(
        str(skills_dir),
        repo_root,
        BACKEND_ARCH,
        FRONTEND_ARCH,
        BACKEND_DOC,
        FRONTEND_DOC,
        include_conventions=True,
        tool="copilot",
        agent_ids=frozenset({"product-requirements"}),
    )

    assert not (skills_dir / "backend").exists()
    assert not (skills_dir / "frontend").exists()
    assert not (skills_dir / "reviewer").exists()
    assert not (skills_dir / "documentation").exists()
    assert not (skills_dir / "git").exists()
