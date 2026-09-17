"""Guidelines context per supported AI tool."""

from __future__ import annotations

from enum import StrEnum


class Tool(StrEnum):
    """Supported AI coding tools."""

    COPILOT = "copilot"
    OPENCODE = "opencode"
    CLAUDE = "claude"


# (skills base directory, project-instructions file) per tool. All three tools
# deploy agents as Skills (SKILL.md under a skills/ folder), so their guideline
# reference paths follow the same shape.
_SKILLS_BASE: dict[Tool, tuple[str, str]] = {
    Tool.COPILOT: (".github/skills", ".github/copilot-instructions.md"),
    Tool.OPENCODE: (".opencode/skills", "AGENTS.md"),
    Tool.CLAUDE: (".claude/skills", "CLAUDE.md"),
}


def guidelines_context(tool: str) -> dict[str, str]:
    """Return the guidelines file paths for a given tool.

    Args:
        tool: One of 'copilot', 'opencode', 'claude'.

    Returns:
        A dict mapping guideline keys to their file paths for that tool.

    Raises:
        ValueError: If the tool is not recognised.
    """
    try:
        base, project_context = _SKILLS_BASE[Tool(tool)]
    except ValueError:
        msg = f"Unknown tool: {tool}"
        raise ValueError(msg) from None

    return {
        "backend_arch": f"{base}/backend/references/architecture.md",
        "frontend_arch": f"{base}/frontend/references/architecture.md",
        "review_backend": f"{base}/reviewer/references/review-backend.md",
        "review_frontend": f"{base}/reviewer/references/review-frontend.md",
        "documentation_backend": f"{base}/documentation/references/documentation-backend.md",
        "documentation_frontend": f"{base}/documentation/references/documentation-frontend.md",
        "conventions": f"{base}/git/references/conventions.md",
        "project_context": project_context,
    }

