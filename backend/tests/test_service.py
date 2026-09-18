"""Tests for core.service.init_project — the shared orchestration used by CLI and API."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from zenflow.core.errors import ZenflowError
from zenflow.core.models import GuidelineSelection, ToolSelection
from zenflow.core.service import init_project

NO_GUIDELINES = GuidelineSelection(
    backend_arch_file="",
    backend_doc_file="",
    frontend_arch_file="",
    frontend_doc_file="",
    include_conventions=False,
)


def test_no_tool_selected_raises(repo_root: str, tmp_target: Path) -> None:
    tools = ToolSelection(copilot=False, opencode=False, claude=False)
    with pytest.raises(ZenflowError, match="at least one tool"):
        init_project(repo_root, str(tmp_target), tools, NO_GUIDELINES)


def test_missing_source_dir_raises(tmp_target: Path) -> None:
    tools = ToolSelection(copilot=True, opencode=False, claude=False)
    with pytest.raises(ZenflowError, match="missing source directory"):
        init_project(str(tmp_target), str(tmp_target / "target"), tools, NO_GUIDELINES)


def test_deploys_selected_tools_and_reports_result(repo_root: str, tmp_target: Path) -> None:
    tools = ToolSelection(copilot=True, opencode=True, claude=False)
    result = init_project(repo_root, str(tmp_target), tools, NO_GUIDELINES)

    assert result.target_path == str(tmp_target)
    assert result.tools == tools
    assert set(result.deployed) == {"copilot", "opencode"}
    assert os.path.isdir(result.deployed["copilot"])
    assert os.path.isdir(result.deployed["opencode"])
    assert (tmp_target / ".github" / "skills" / "backend" / "SKILL.md").exists()
    assert (tmp_target / ".opencode" / "skills" / "backend" / "SKILL.md").exists()
    assert not (tmp_target / ".claude").exists()


def test_guideline_selection_include_properties() -> None:
    assert not NO_GUIDELINES.include_backend
    assert not NO_GUIDELINES.include_frontend

    with_both = GuidelineSelection(
        backend_arch_file="python.md.j2",
        backend_doc_file="",
        frontend_arch_file="react-typescript.md.j2",
        frontend_doc_file="",
        include_conventions=False,
    )
    assert with_both.include_backend
    assert with_both.include_frontend


def test_custom_agent_ids_deploy_as_agent_md_for_copilot(repo_root: str, tmp_target: Path) -> None:
    """custom_agent_ids must produce .agent.md files under .github/agents for Copilot."""
    tools = ToolSelection(copilot=True, opencode=False, claude=False)
    init_project(
        repo_root,
        str(tmp_target),
        tools,
        NO_GUIDELINES,
        agent_ids=frozenset(),
        custom_agent_ids=frozenset({"backend"}),
    )

    assert (tmp_target / ".github" / "agents" / "backend.agent.md").exists()
    assert not (tmp_target / ".github" / "skills" / "backend").exists()


def test_custom_agent_ids_deploy_as_skill_for_opencode(repo_root: str, tmp_target: Path) -> None:
    """OpenCode has no Custom Agent format, so custom_agent_ids still deploy as Skills."""
    tools = ToolSelection(copilot=False, opencode=True, claude=False)
    init_project(
        repo_root,
        str(tmp_target),
        tools,
        NO_GUIDELINES,
        agent_ids=frozenset(),
        custom_agent_ids=frozenset({"backend"}),
    )

    assert (tmp_target / ".opencode" / "skills" / "backend" / "SKILL.md").exists()

