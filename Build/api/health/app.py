"""API process health and read-only, dev-only dependency readiness."""

import os
import re

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from Build.api.health.dependencies import DependencyHealth
from Build.api.gpu import create_router as gpu_router
from Build.api.lab import create_router as lab_router
from Build.api.storage import create_router as storage_router
from Build.api.agent import create_router as agent_router
from Build.api.experiment import create_router as experiment_router
from Build.api.experiment.share import create_router as share_router
from Build.api.room import create_router as room_router
from Build.api.agent import handlers as agent_handlers, lab_handlers, equation_handlers
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
    app.include_router(storage_router())  # N03 files/quotas/projects; SQLite + disk under R2S_DATA_DIR, no Redis
    app.include_router(agent_router(handlers={**agent_handlers.HANDLERS, **lab_handlers.HANDLERS, **equation_handlers.HANDLERS}))  # N05 agent turn + transcription; N12 lab tools; N15 fit_equation
    app.include_router(lab_handlers.create_router())  # N12 editor scene/run/report for the agent lab; disk only
    app.include_router(gpu_router())  # N04 GPU status dot; SQLite job table + Modal stats, independent of Redis
    app.include_router(experiment_router())  # N07 Mode B experiments; N03 SQLite + one worker thread, no Redis
    app.include_router(share_router())  # N16 Guess the Gravity share (owner) + public token reads; N03 SQLite
    app.include_router(room_router())  # N08 room video -> lab scene jobs; files under R2S_DATA_DIR, no Redis
    # Internal owner-scoped routes (WORKSPACE_INTERNAL_TOKEN); analysis resolves scenes from the jobs store.
    try:
        store = jobs.default_store()
    except ValueError:  # malformed REDIS_URL: liveness must not depend on it; readiness reports redis, workspace stays unmounted
        return app
    app.include_router(jobs.create_router(store))
    app.include_router(analysis.create_router(jobs.scene_resolver(store)))
    return app


app = create_app()
