"""Worker health HTTP process; NOT a job consumer or worker heartbeat."""

import os
import re

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from Build.api.health.dependencies import DependencyHealth

SERVICE = "worker"


def create_app() -> FastAPI:
    dependencies = DependencyHealth(os.environ, ("redis", "bucket"))
    raw_revision = os.environ.get("RAILWAY_GIT_COMMIT_SHA", "")
    revision = raw_revision.lower() if re.fullmatch(r"[0-9a-fA-F]{40}", raw_revision) else "unknown"
    app = FastAPI(title="Real2Simulation worker health", docs_url=None, redoc_url=None, openapi_url=None)

    @app.get("/health/live")
    async def live():
        return {"service": SERVICE, "status": "ok", "revision": revision}

    @app.get("/health/ready")
    def ready():
        states = dependencies.check()
        states["heartbeat"] = "unavailable"
        # An HTTP sidecar cannot attest to a job loop that does not exist yet.
        return JSONResponse(status_code=503, content={
            "service": SERVICE, "status": "unavailable", "revision": revision,
            "dependencies": states,
        })

    @app.get("/api/version")
    async def version():
        return {"service": SERVICE, "revision": revision}

    return app


app = create_app()
