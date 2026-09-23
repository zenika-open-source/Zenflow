"""End-to-end API coverage for the Tech Migration export formats."""

from __future__ import annotations

import io
import zipfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from zenflow.routers.app import app


@pytest.mark.parametrize(
    "tool,base",
    [
        ("copilot", ".github"),
        ("opencode", ".opencode"),
        ("claude", ".claude"),
    ],
)
@pytest.mark.parametrize("mode", ["skill", "custom"])
@pytest.mark.parametrize(
    "backend_arch,frontend_arch",
    [
        ("", ""),
        ("golang-gin.md.j2", "nextjs-app-router.md.j2"),
        ("java-spring-boot.md.j2", "react-typescript.md.j2"),
    ],
)
def test_archive_exports_selected_migration_only(
    tool: str, base: str, mode: str, backend_arch: str, frontend_arch: str
) -> None:
    request = {
        "tools": {"copilot": tool == "copilot", "opencode": tool == "opencode", "claude": tool == "claude"},
        "guidelines": {
            "backend_arch_file": backend_arch,
            "frontend_arch_file": frontend_arch,
            "include_conventions": False,
        },
        "skills": ["tech-migration"] if mode == "skill" else [],
        "custom_skills": ["tech-migration"] if mode == "custom" else [],
    }
    response = TestClient(app).post("/init/archive", json=request)

    assert response.status_code == 200
    with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
        names = set(archive.namelist())
        expected = (
            ".github/agents/tech-migration.agent.md"
            if tool == "copilot" and mode == "custom"
            else f"{base}/skills/tech-migration/SKILL.md"
        )
        assert expected in names
        assert not any("backend/SKILL.md" in name or "frontend/SKILL.md" in name for name in names)
        assert not any("/tech-migration/references/" in name for name in names)
        assert not any(name.endswith("tech-migration.agent.md") for name in names if name != expected)
        assert not any(name.endswith("tech-migration/SKILL.md") for name in names if name != expected)
        rendered = archive.read(expected).decode("utf-8")
        assert "docs/plans/[migration-slug].md" in rendered
        assert "### G7 - Decommission" in rendered
        assert "{{" not in rendered and "{%" not in rendered
        if tool == "copilot" and mode == "custom":
            assert "handoffs:" in rendered
            assert "## Next Steps" not in rendered
        else:
            assert "handoffs:" not in rendered
            assert "## Next Steps" in rendered


def test_archive_orchestrator_without_migration_does_not_install_it() -> None:
    response = TestClient(app).post(
        "/init/archive",
        json={
            "tools": {"copilot": True},
            "skills": [],
            "custom_skills": ["orchestrator"],
        },
    )

    assert response.status_code == 200
    with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
        names = set(archive.namelist())
        assert ".github/agents/orchestrator.agent.md" in names
        assert not any("tech-migration" in name for name in names)
        assert "Tech Migration was installed" in archive.read(".github/agents/orchestrator.agent.md").decode("utf-8")


def test_init_and_agent_catalog_include_migration(tmp_path: Path) -> None:
    client = TestClient(app)
    catalog_response = client.get("/agents")

    assert catalog_response.status_code == 200
    assert "tech-migration" in {agent["id"] for agent in catalog_response.json()["agents"]}

    init_response = client.post(
        "/init",
        json={
            "target_path": str(tmp_path),
            "tools": {"copilot": True},
            "skills": ["tech-migration"],
            "custom_skills": [],
        },
    )

    assert init_response.status_code == 200
    assert (tmp_path / ".github" / "skills" / "tech-migration" / "SKILL.md").exists()
    assert not (tmp_path / ".github" / "agents" / "tech-migration.agent.md").exists()
