"""FastAPI application entry point for the Zenflow API.

Interactive docs (Swagger UI) are served at /docs, ReDoc at /redoc, and the raw
OpenAPI schema at /openapi.json — all provided automatically by FastAPI.
"""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from zenflow.routers import agents, archive, init, stacks

app = FastAPI(
    title="Zenflow API",
    description="Programmatic access to Zenflow project initialization.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    # TODO: narrow to the deployed frontend origin once its GCP URL is known.
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths that serve FastAPI's built-in HTML docs, which load Swagger UI/ReDoc
# assets from a CDN with inline scripts — a locked-down CSP would break them.
_DOCS_PATHS = {"/docs", "/redoc", "/openapi.json"}


@app.middleware("http")
async def security_headers(request: Request, call_next):
    """Attach standard security headers to every response."""
    response = await call_next(request)
    response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    if request.url.path not in _DOCS_PATHS:
        response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
    return response


app.include_router(init.router, tags=["init"])
app.include_router(archive.router, tags=["archive"])
app.include_router(stacks.router, tags=["stacks"])
app.include_router(agents.router, tags=["agents"])


def main() -> None:
    """Run the Zenflow API locally with uvicorn (development entry point)."""
    import uvicorn

    uvicorn.run("zenflow.routers.app:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    main()
