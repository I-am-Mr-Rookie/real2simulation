"""API process health and read-only, dev-only dependency readiness."""

import os
import re

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from Build.api.health.dependencies import DependencyHealth
from Build.api.lab import create_router as lab_router
from Build.api.workspace import analysis, jobs

SERVICE = "api"


def create_app() -> FastAPI:
    dependencies = DependencyHealth(os.environ, ("postgres", "redis", "bucket"))
    # Railway's build metadata, not a secret/config dump. Reject arbitrary text.
    raw_revision = os.environ.get("RAILWAY_GIT_COMMIT_SHA", "")
    revision = raw_revision.lower() if re.fullmatch(r"[0-9a-fA-F]{40}", raw_revision) else "unknown"
    app = FastAPI(title="Real2Simulation API health", docs_url=None, redoc_url=None, openapi_url=None)

    @app.get("/health/live")
    async def live():
        # Must remain independent of DB, queue, storage and paid inference.
        return {"service": SERVICE, "status": "ok", "revision": revision}

    @app.get("/health/ready")
    def ready():
        states = dependencies.check()
        healthy = all(state == "ok" for state in states.values())
        return JSONResponse(status_code=200 if healthy else 503, content={
            "service": SERVICE, "status": "ok" if healthy else "unavailable", "revision": revision,
            "dependencies": states,
        })

    @app.get("/api/version")
    async def version():
        return {"service": SERVICE, "revision": revision}

    app.include_router(lab_router())  # internal-token lab bridge; independent of Redis like liveness
    # Internal owner-scoped routes (WORKSPACE_INTERNAL_TOKEN); analysis resolves scenes from the jobs store.
    try:
        store = jobs.default_store()
    except ValueError:  # malformed REDIS_URL: liveness must not depend on it; readiness reports redis, workspace stays unmounted
        return app
    app.include_router(jobs.create_router(store))
    app.include_router(analysis.create_router(jobs.scene_resolver(store)))
    return app


app = create_app()
