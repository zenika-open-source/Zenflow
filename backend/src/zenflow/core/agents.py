"""Discovery of available agent templates, independent of deployment."""

from __future__ import annotations

import glob
import os
import re
from pathlib import Path

from zenflow.core.errors import ZenflowError
from zenflow.core.models import AgentInfo

_NAME_RE = re.compile(r"^name:\s*(.+)$", re.MULTILINE)
_DESCRIPTION_RE = re.compile(r"^description:\s*(.+)$", re.MULTILINE)


def list_agents(agents_dir: str) -> list[AgentInfo]:
    """Return metadata for every agent template in agents_dir.

    Reads each template's static frontmatter (name/description) directly —
    it does not render the Jinja2 template, since those two fields never
    depend on template variables.

    Args:
        agents_dir: Directory containing *.md.j2 agent template source files.

    Returns:
        AgentInfo entries sorted by id.

    Raises:
        ZenflowError: If a template is missing a name or description field.
    """
    agents: list[AgentInfo] = []
    for path in sorted(glob.glob(os.path.join(agents_dir, "*.md.j2"))):
        agent_id = os.path.splitext(os.path.splitext(os.path.basename(path))[0])[0]
        text = Path(path).read_text(encoding="utf-8")
        name_match = _NAME_RE.search(text)
        description_match = _DESCRIPTION_RE.search(text)
        if not name_match or not description_match:
            raise ZenflowError(f"agent template missing name/description frontmatter: {path}")
        agents.append(
            AgentInfo(
                id=agent_id,
                name=name_match.group(1).strip(),
                description=description_match.group(1).strip(),
            )
        )
    return agents
