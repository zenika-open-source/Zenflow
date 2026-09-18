"""POST /init/archive — build the selected setup and return it as a downloadable zip.

Unlike POST /init (which writes to a target_path on the machine running the API),
this deploys into a discarded temp directory and streams the result back as a zip —
the shape a browser client actually wants.
"""

from __future__ import annotations

import io
import shutil
import tempfile
import zipfile
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from zenflow.core.deployment import resolve_agent_ids
from zenflow.core.errors import ZenflowError
from zenflow.core.service import init_project, repo_root
from zenflow.routers.schemas import ErrorResponse, GuidelineSelectionRequest, ToolSelectionRequest

router = APIRouter()


class ArchiveRequest(BaseModel):
    """Request body for POST /init/archive."""

    tools: ToolSelectionRequest
    guidelines: GuidelineSelectionRequest = Field(default_factory=GuidelineSelectionRequest)
    skills: list[str] | None = None
    custom_skills: list[str] | None = None


def _zip_directory(directory: str) -> io.BytesIO:
    """Zip every file under directory, with archive paths relative to it.

    Args:
        directory: Root directory to archive.

    Returns:
        An in-memory buffer positioned at the start, ready to stream.
    """
    buffer = io.BytesIO()
    root = Path(directory)
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in root.rglob("*"):
            if path.is_file():
                archive.write(path, path.relative_to(root))
    buffer.seek(0)
    return buffer


@router.post("/init/archive", responses={400: {"model": ErrorResponse}})
def init_archive(request: ArchiveRequest) -> StreamingResponse:
    """Deploy the selected tools and guidelines, then stream the result back as a zip.

    Args:
        request: Tool and guideline selection (no target_path — the archive is built
            into a temporary directory that is discarded once the response is ready).

    Returns:
        A zip archive of the generated files as a streaming download.

    Raises:
        HTTPException: 400 if no tool is selected or a source directory is missing.
    """
    agent_ids = resolve_agent_ids(request.skills) if request.skills is not None else None
    custom_agent_ids = resolve_agent_ids(request.custom_skills) if request.custom_skills is not None else None
    tmp_dir = tempfile.mkdtemp(prefix="zenflow-")
    try:
        init_project(
            repo_root(),
            tmp_dir,
            request.tools.to_domain(),
            request.guidelines.to_domain(),
            agent_ids,
            custom_agent_ids,
        )
        buffer = _zip_directory(tmp_dir)
    except ZenflowError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    return StreamingResponse(
        buffer,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=zenflow-setup.zip"},
    )
