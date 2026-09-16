"""Tests for the agents catalog used by GET /agents."""

from __future__ import annotations

import os

from zenflow.core.agents import list_agents

EXPECTED_AGENT_IDS = {
    "backend",
    "frontend",
    "reviewer",
    "git",
    "documentation",
    "orchestrator",
    "product-requirements",
    "static-prototyping",
    "dynamic-prototyping",
}


def test_list_agents_returns_all_templates(repo_root: str) -> None:
    """list_agents must return one entry per *.md.j2 template, sorted by id."""
    agents_dir = os.path.join(repo_root, "templates", "agents")
    agents = list_agents(agents_dir)

    assert {a.id for a in agents} == EXPECTED_AGENT_IDS
    assert [a.id for a in agents] == sorted(a.id for a in agents)


def test_list_agents_has_name_and_description(repo_root: str) -> None:
    """Every agent must expose a non-empty name and description."""
    agents_dir = os.path.join(repo_root, "templates", "agents")
    agents = list_agents(agents_dir)

    for agent in agents:
        assert agent.name.strip() != ""
        assert agent.description.strip() != ""
