"""Deployment helpers for agents and guidelines."""

from __future__ import annotations

import glob
import os

from zenflow.core.guidelines import guidelines_context
from zenflow.core.rendering import assemble_agent, assemble_guideline, make_env

# Maps a frontend skill id to its backend agent template id, for the ids that
# don't already match 1:1 (e.g. the "Code review" skill deploys the reviewer
# agent).
SKILL_ID_TO_AGENT_ID: dict[str, str] = {
    "code-review": "reviewer",
}


def resolve_agent_ids(skill_ids: list[str]) -> frozenset[str]:
    """Translate frontend skill ids into backend agent template ids.

    Args:
        skill_ids: Skill ids selected by the user (e.g. "code-review").

    Returns:
        The corresponding agent ids (e.g. "reviewer").
    """
    return frozenset(SKILL_ID_TO_AGENT_ID.get(skill_id, skill_id) for skill_id in skill_ids)


def deploy_agents(
    agents_src_dir: str,
    target_agents_dir: str,
    repo_root: str,
    tool: str,
    *,
    skill_mode: bool = False,
    agent_ids: frozenset[str] | None = None,
) -> None:
    """Render and deploy the selected agent templates.

    Args:
        agents_src_dir: Directory containing *.agent.md.j2 source files.
        target_agents_dir: Destination directory.
        repo_root: Repository root path.
        tool: Tool name for guidelines context ('copilot', 'opencode', 'claude').
        skill_mode: If True, strips handoffs and appends Next Steps block.
        agent_ids: Agent ids to deploy. If None, every agent template is
            deployed (used when no selection applies, e.g. the CLI).
    """
    os.makedirs(target_agents_dir, exist_ok=True)
    context = {"guidelines": guidelines_context(tool)}
    env = make_env(repo_root)

    for agent_file in glob.glob(os.path.join(agents_src_dir, "*.md.j2")):
        agent_name = os.path.splitext(os.path.splitext(os.path.basename(agent_file))[0])[0]
        template_path = f"agents/{os.path.basename(agent_file)}"

        if agent_ids is not None and agent_name not in agent_ids:
            continue

        if skill_mode:
            skill_dir = os.path.join(target_agents_dir, agent_name)
            dst = os.path.join(skill_dir, "SKILL.md")
        else:
            out_name = f"{agent_name}.agent.md"
            dst = os.path.join(target_agents_dir, out_name)

        assemble_agent(template_path, dst, env, context, skill_mode=skill_mode)


def deploy_guidelines_to_skills(
    target_skills_dir: str,
    repo_root: str,
    backend_arch_file: str,
    frontend_arch_file: str,
    backend_doc_file: str,
    frontend_doc_file: str,
    include_conventions: bool,
    tool: str,
) -> None:
    """Deploy guideline files into skill references/ subdirs (Copilot / OpenCode / Claude Code).

    Mapping:
      backend/<arch>.md.j2          -> backend/references/architecture.md
      frontend/<arch>.md.j2         -> frontend/references/architecture.md
      review/backend.md.j2          -> reviewer/references/review-backend.md
      review/frontend.md.j2         -> reviewer/references/review-frontend.md
      documentation/<doc>.md.j2     -> documentation/references/documentation-backend.md
      documentation/<doc>.md.j2     -> documentation/references/documentation-frontend.md
      git-conventions/default.md.j2 -> git/references/conventions.md

    Args:
        target_skills_dir: Root skills directory (e.g. .opencode/skills/).
        repo_root: Repository root path.
        backend_arch_file: Selected backend architecture template filename.
        frontend_arch_file: Selected frontend architecture template filename.
        backend_doc_file: Selected backend documentation template filename (may be empty).
        frontend_doc_file: Selected frontend documentation template filename (may be empty).
        include_conventions: Whether to include git conventions.
        tool: Tool name ('opencode' or 'claude') for guidelines context.
    """
    env = make_env(repo_root)
    ctx: dict[str, object] = {"guidelines": guidelines_context(tool)}

    def deploy(src_subdir: str, src_filename: str, skill_name: str, dst_filename: str) -> None:
        src_template = f"guidelines/{src_subdir}/{src_filename}"
        dst = os.path.join(target_skills_dir, skill_name, "references", dst_filename)
        assemble_guideline(src_template, dst, env, ctx)

    if backend_arch_file:
        deploy("backend", backend_arch_file, "backend", "architecture.md")
        deploy("review", "backend.md.j2", "reviewer", "review-backend.md")
    if frontend_arch_file:
        deploy("frontend", frontend_arch_file, "frontend", "architecture.md")
        deploy("review", "frontend.md.j2", "reviewer", "review-frontend.md")
    if backend_doc_file:
        deploy(
            "documentation",
            backend_doc_file,
            "documentation",
            "documentation-backend.md",
        )
    if frontend_doc_file:
        deploy(
            "documentation",
            frontend_doc_file,
            "documentation",
            "documentation-frontend.md",
        )
    if include_conventions:
        deploy("git-conventions", "default.md.j2", "git", "conventions.md")
