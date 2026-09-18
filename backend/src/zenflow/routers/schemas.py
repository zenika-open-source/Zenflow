"""Pydantic request/response models for the Zenflow API — kept separate from core.models
so the HTTP contract (validation, JSON shape) can evolve independently of the domain."""

from __future__ import annotations

from pydantic import BaseModel, Field

from zenflow.core.models import AgentInfo, DeploymentResult, GuidelineSelection, ToolSelection


class ToolSelectionRequest(BaseModel):
    """Which AI tools to set up."""

    copilot: bool = False
    opencode: bool = False
    claude: bool = False

    def to_domain(self) -> ToolSelection:
        """Convert to the core ToolSelection dataclass."""
        return ToolSelection(copilot=self.copilot, opencode=self.opencode, claude=self.claude)


class GuidelineSelectionRequest(BaseModel):
    """Guideline template filenames to deploy, as returned by GET /stacks."""

    backend_arch_file: str = ""
    backend_doc_file: str = ""
    frontend_arch_file: str = ""
    frontend_doc_file: str = ""
    include_conventions: bool = True

    def to_domain(self) -> GuidelineSelection:
        """Convert to the core GuidelineSelection dataclass."""
        return GuidelineSelection(
            backend_arch_file=self.backend_arch_file,
            backend_doc_file=self.backend_doc_file,
            frontend_arch_file=self.frontend_arch_file,
            frontend_doc_file=self.frontend_doc_file,
            include_conventions=self.include_conventions,
        )


class InitRequest(BaseModel):
    """Request body for POST /init."""

    target_path: str
    tools: ToolSelectionRequest
    guidelines: GuidelineSelectionRequest = Field(default_factory=GuidelineSelectionRequest)
    skills: list[str] | None = None
    custom_skills: list[str] | None = None


class InitResponse(BaseModel):
    """Response body for POST /init."""

    target_path: str
    deployed: dict[str, str]

    @classmethod
    def from_domain(cls, result: DeploymentResult) -> InitResponse:
        """Build a response from a core DeploymentResult."""
        return cls(target_path=result.target_path, deployed=result.deployed)


class ErrorResponse(BaseModel):
    """Response body for error responses."""

    detail: str


class FrameworkOption(BaseModel):
    """A single selectable framework within a language."""

    label: str
    arch_file: str
    doc_file: str


class StackCatalog(BaseModel):
    """Response body for GET /stacks."""

    backend: dict[str, list[FrameworkOption]]
    frontend: dict[str, list[FrameworkOption]]


class AgentSummary(BaseModel):
    """A single available agent, as advertised by GET /agents."""

    id: str
    name: str
    description: str

    @classmethod
    def from_domain(cls, agent: AgentInfo) -> AgentSummary:
        """Build a response entry from a core AgentInfo."""
        return cls(id=agent.id, name=agent.name, description=agent.description)


class AgentCatalog(BaseModel):
    """Response body for GET /agents."""

    agents: list[AgentSummary]
