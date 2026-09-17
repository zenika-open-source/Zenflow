"""GET /agents — expose the catalog of available agent templates."""

from __future__ import annotations

from fastapi import APIRouter

from zenflow.core.agents import list_agents
from zenflow.core.service import get_dirs, repo_root
from zenflow.routers.schemas import AgentCatalog, AgentSummary

router = APIRouter()


@router.get("/agents", response_model=AgentCatalog)
def get_agents() -> AgentCatalog:
    """Return every agent template available for deployment.

    Returns:
        AgentCatalog listing each agent's id, name, and description.
    """
    root = repo_root()
    agents = list_agents(get_dirs(root).agents)
    return AgentCatalog(agents=[AgentSummary.from_domain(agent) for agent in agents])
