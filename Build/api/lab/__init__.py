"""Internal S10 lab bridge for the deployed web /api/lab route (S15av).

The web container has no Python, so it calls this route with WORKSPACE_INTERNAL_TOKEN. The handler is the same
fixed-action Build/lab/session-bridge.py used locally: strict schema, bounded samples, 20 s simulator timeout,
no file uploads, network, paid/GPU/Meta calls or secrets. Mystery-g private values stay server-to-server.
"""
import hmac
import importlib.util
import json
import os
from pathlib import Path

from fastapi import APIRouter, Header, HTTPException, Request
from fastapi.concurrency import run_in_threadpool

from Build.api.workspace.auth import TOKEN_ENV

_SPEC = importlib.util.spec_from_file_location("s10_lab_bridge", Path(__file__).resolve().parents[2] / "lab/session-bridge.py")
bridge = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(bridge)
MAX_BODY = 1_000_000


def create_router() -> APIRouter:
    router = APIRouter()

    @router.post("/internal/lab/bridge")
    async def run(request: Request, x_workspace_token: str | None = Header(default=None)):
        expected = os.environ.get(TOKEN_ENV, "")
        # Unset server token fails closed (same rule as workspace auth).
        if not expected or not x_workspace_token or not hmac.compare_digest(x_workspace_token.encode(), expected.encode()):
            raise HTTPException(status_code=401, detail={"code": "UNAUTHORIZED"})
        raw = await request.body()
        if len(raw) > MAX_BODY:
            return bridge.error("request_too_large")
        try:
            payload = json.loads(raw)
        except ValueError:
            return bridge.error("invalid_json")
        return await run_in_threadpool(bridge.handle, payload)

    return router
