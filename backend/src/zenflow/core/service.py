"""Front-end-agnostic orchestration for deploying a Zenflow setup to a target project."""

from __future__ import annotations

import glob
import os
import shutil
from pathlib import Path

from zenflow.core.deployment import (
    deploy_agents,
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
    custom_agent_ids: frozenset[str] | None,
) -> str:
    """Deploy GitHub Copilot (VS Code) setup to target_path.

    Agents in agent_ids are deployed as Skills (.github/skills/<name>/SKILL.md),
    same as OpenCode and Claude Code, since that's the format Copilot loads
    on-demand. Agents in custom_agent_ids are deployed as standalone Custom
    Agent files (.github/agents/<name>.agent.md) instead.

    Args:
        target_path: Root target directory.
        src: Source directory paths.
        repo_root: Repository root path.
        guidelines: User's guideline file choices.
        agent_ids: Agent ids to deploy as Skills, or None to deploy every agent.
        custom_agent_ids: Agent ids to deploy as Custom Agent files, or None/empty
            to skip this format entirely.

    Returns:
        The deployed .github directory path.
    """
    target_github_dir = os.path.join(target_path, ".github")
    skills_dir = os.path.join(target_github_dir, "skills")
    agents_dir = os.path.join(target_github_dir, "agents")
    instructions_dir = os.path.join(target_github_dir, "instructions")
    os.makedirs(instructions_dir, exist_ok=True)

    deploy_agents(src.agents, skills_dir, repo_root, tool="copilot", skill_mode=True, agent_ids=agent_ids)
    if custom_agent_ids:
        deploy_agents(
            src.agents, agents_dir, repo_root, tool="copilot", skill_mode=False, agent_ids=custom_agent_ids
        )

    for f in glob.glob(os.path.join(src.instructions, "*.md")):
        shutil.copy(f, instructions_dir)

    deploy_guidelines_to_skills(
        skills_dir,
        repo_root,
        guidelines.backend_arch_file,
        guidelines.frontend_arch_file,
        guidelines.backend_doc_file,
        guidelines.frontend_doc_file,
        guidelines.include_conventions,
        tool="copilot",
        agent_ids=agent_ids,
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

    Neither tool has a Custom Agent file format, so callers should merge any
    custom-mode agent ids into agent_ids before calling this — they still get
    deployed as Skills here.

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
        agent_ids=agent_ids,
    )
    return skills_dir


def init_project(
    repo_root: str,
    target_path: str,
    tools: ToolSelection,
    guidelines: GuidelineSelection,
    agent_ids: frozenset[str] | None = None,
    custom_agent_ids: frozenset[str] | None = None,
) -> DeploymentResult:
    """Deploy the selected tools and guideline templates to target_path.

    Args:
        repo_root: Zenflow repository root (source of templates).
        target_path: Destination project root.
        tools: Which AI tools to deploy.
        guidelines: Selected guideline template files.
        agent_ids: Agent ids to deploy as Skills, or None to deploy every agent
            (e.g. the CLI, which has no skill selection).
        custom_agent_ids: Agent ids to deploy as Custom Agent files (Copilot
            only; deployed as Skills for OpenCode/Claude, which have no Custom
            Agent format). None or empty deploys none in this format.

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
    skills_and_custom_ids = None if agent_ids is None else agent_ids | (custom_agent_ids or frozenset())

    if tools.copilot:
        deployed["copilot"] = _deploy_copilot(target_path, src, repo_root, guidelines, agent_ids, custom_agent_ids)
    if tools.opencode:
        deployed["opencode"] = _deploy_skills_tool(
            target_path, ".opencode/skills", "opencode", src, repo_root, guidelines, skills_and_custom_ids
        )
    if tools.claude:
        deployed["claude"] = _deploy_skills_tool(
            target_path, ".claude/skills", "claude", src, repo_root, guidelines, skills_and_custom_ids
        )

    return DeploymentResult(target_path=target_path, tools=tools, guidelines=guidelines, deployed=deployed)
