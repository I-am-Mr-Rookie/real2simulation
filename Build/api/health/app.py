"""API process health and read-only, dev-only dependency readiness."""

import os
import re

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from Build.api.health.dependencies import DependencyHealth

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

    return app


app = create_app()
