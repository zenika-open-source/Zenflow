"""Domain models shared by every Zenflow front end (CLI, API, ...)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SourceDirs:
    """Key source directories derived from the repository root.

    Attributes:
        agents: Path to the agents templates directory.
        instructions: Path to the instructions templates directory.
        guidelines: Path to the guidelines templates directory.
    """

    agents: str
    instructions: str
    guidelines: str


@dataclass(frozen=True)
class ToolSelection:
    """Which AI tools the user wants to set up.

    Attributes:
        copilot: Whether to deploy GitHub Copilot (VS Code) setup.
        opencode: Whether to deploy OpenCode setup.
        claude: Whether to deploy Claude Code setup.
    """

    copilot: bool
    opencode: bool
    claude: bool

    def any_selected(self) -> bool:
        """Return True if at least one tool is selected."""
        return any((self.copilot, self.opencode, self.claude))


@dataclass(frozen=True)
class GuidelineSelection:
    """User's guideline file choices.

    Attributes:
        backend_arch_file: Arch template filename for backend, or empty string.
        backend_doc_file: Doc template filename for backend, or empty string.
        frontend_arch_file: Arch template filename for frontend, or empty string.
        frontend_doc_file: Doc template filename for frontend, or empty string.
        include_conventions: Whether to include git conventions template.
    """

    backend_arch_file: str
    backend_doc_file: str
    frontend_arch_file: str
    frontend_doc_file: str
    include_conventions: bool

    @property
    def include_backend(self) -> bool:
        """Return True if backend guidelines were selected."""
        return bool(self.backend_arch_file)

    @property
    def include_frontend(self) -> bool:
        """Return True if frontend guidelines were selected."""
        return bool(self.frontend_arch_file)


@dataclass(frozen=True)
class DeploymentResult:
    """Outcome of a successful `init_project` call.

    Attributes:
        target_path: Root directory the setup was deployed to.
        tools: Tools that were deployed.
        guidelines: Guideline selection that was applied.
        deployed: Mapping of tool name to its deployed root directory.
    """

    target_path: str
    tools: ToolSelection
    guidelines: GuidelineSelection
    deployed: dict[str, str]


@dataclass(frozen=True)
class AgentInfo:
    """Summary of one available agent template.

    Attributes:
        id: Template filename stem (e.g. 'backend'), used as the stable agent identifier.
        name: Human-readable agent name from its frontmatter.
        description: One-line description from its frontmatter.
    """

    id: str
    name: str
    description: str
