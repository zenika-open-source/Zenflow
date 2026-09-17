"""Front-end-agnostic orchestration for deploying a Zenflow setup to a target project."""

from __future__ import annotations

import glob
import os
import shutil
from pathlib import Path

from zenflow.core.deployment import (
    deploy_agents,
    deploy_guidelines_to_github,
    deploy_guidelines_to_skills,
)
from zenflow.core.errors import ZenflowError
from zenflow.core.models import DeploymentResult, GuidelineSelection, SourceDirs, ToolSelection


def repo_root() -> str:
    """Return the Zenflow repository root, derived from this module's install location.

    Returns:
        Absolute path to the repository root (parent of src/).
    """
    return str(Path(__file__).resolve().parents[3])


def get_dirs(repo_root: str) -> SourceDirs:
    """Return key source directories derived from repo_root.

    Args:
        repo_root: Repository root path.

    Returns:
        SourceDirs with agents, instructions, and guidelines paths.
    """
    return SourceDirs(
        agents=os.path.join(repo_root, "templates", "agents"),
        instructions=os.path.join(repo_root, "templates", "instructions"),
        guidelines=os.path.join(repo_root, "templates", "guidelines"),
    )


def validate_dirs(*dirs: str) -> None:
    """Raise if any of the given directories do not exist.

    Args:
        *dirs: Directory paths to validate.

    Raises:
        ZenflowError: If any directory is missing.
    """
    for d in dirs:
        if not os.path.isdir(d):
            raise ZenflowError(f"missing source directory: {d}")


def _deploy_copilot(
    target_path: str,
    src: SourceDirs,
    repo_root: str,
    guidelines: GuidelineSelection,
    agent_ids: frozenset[str] | None,
) -> str:
    """Deploy GitHub Copilot (VS Code) setup to target_path.

    Args:
        target_path: Root target directory.
        src: Source directory paths.
        repo_root: Repository root path.
        guidelines: User's guideline file choices.
        agent_ids: Agent ids to deploy, or None to deploy every agent.

    Returns:
        The deployed .github directory path.
    """
    target_github_dir = os.path.join(target_path, ".github")
    agents_dir = os.path.join(target_github_dir, "agents")
    instructions_dir = os.path.join(target_github_dir, "instructions")
    guidelines_dir = os.path.join(target_github_dir, "guidelines")
    os.makedirs(agents_dir, exist_ok=True)
    os.makedirs(instructions_dir, exist_ok=True)
    os.makedirs(guidelines_dir, exist_ok=True)

    deploy_agents(src.agents, agents_dir, repo_root, tool="copilot", skill_mode=False, agent_ids=agent_ids)

    for f in glob.glob(os.path.join(src.instructions, "*.md")):
        shutil.copy(f, instructions_dir)

    deploy_guidelines_to_github(
        guidelines_dir,
        repo_root,
        guidelines.backend_arch_file,
        guidelines.frontend_arch_file,
        guidelines.backend_doc_file,
        guidelines.frontend_doc_file,
        guidelines.include_conventions,
    )
    return target_github_dir


def _deploy_skills_tool(
    target_path: str,
    tool_subdir: str,
    tool: str,
    src: SourceDirs,
    repo_root: str,
    guidelines: GuidelineSelection,
    agent_ids: frozenset[str] | None,
) -> str:
    """Deploy a skills-based tool (OpenCode or Claude Code) to target_path.

    Args:
        target_path: Root target directory.
        tool_subdir: Subdirectory under target_path (e.g. '.opencode/skills').
        tool: Tool identifier passed to deployment functions (e.g. 'opencode').
        src: Source directory paths.
        repo_root: Repository root path.
        guidelines: User's guideline file choices.
        agent_ids: Agent ids to deploy, or None to deploy every agent.

    Returns:
        The deployed skills directory path.
    """
    skills_dir = os.path.join(target_path, tool_subdir)
    deploy_agents(src.agents, skills_dir, repo_root, tool=tool, skill_mode=True, agent_ids=agent_ids)
    deploy_guidelines_to_skills(
        skills_dir,
        repo_root,
        guidelines.backend_arch_file,
        guidelines.frontend_arch_file,
        guidelines.backend_doc_file,
        guidelines.frontend_doc_file,
        guidelines.include_conventions,
        tool=tool,
    )
    return skills_dir


def init_project(
    repo_root: str,
    target_path: str,
    tools: ToolSelection,
    guidelines: GuidelineSelection,
    agent_ids: frozenset[str] | None = None,
) -> DeploymentResult:
    """Deploy the selected tools and guideline templates to target_path.

    Args:
        repo_root: Zenflow repository root (source of templates).
        target_path: Destination project root.
        tools: Which AI tools to deploy.
        guidelines: Selected guideline template files.
        agent_ids: Agent ids to deploy, or None to deploy every agent (e.g. the
            CLI, which has no skill selection).

    Returns:
        DeploymentResult describing what was deployed.

    Raises:
        ZenflowError: If no tool is selected, or a required source directory is missing.
    """
    if not tools.any_selected():
        raise ZenflowError("at least one tool must be selected")

    src = get_dirs(repo_root)
    validate_dirs(src.agents, src.instructions, src.guidelines)

    deployed: dict[str, str] = {}

    if tools.copilot:
        deployed["copilot"] = _deploy_copilot(target_path, src, repo_root, guidelines, agent_ids)
    if tools.opencode:
        deployed["opencode"] = _deploy_skills_tool(
            target_path, ".opencode/skills", "opencode", src, repo_root, guidelines, agent_ids
        )
    if tools.claude:
        deployed["claude"] = _deploy_skills_tool(
            target_path, ".claude/skills", "claude", src, repo_root, guidelines, agent_ids
        )

    return DeploymentResult(target_path=target_path, tools=tools, guidelines=guidelines, deployed=deployed)
