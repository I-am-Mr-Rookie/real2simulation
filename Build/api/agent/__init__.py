"""N05 agent API: POST /workspace/agent/turn and /workspace/agent/transcribe (owner-gated like workspace)."""
from __future__ import annotations

from typing import Any, Callable, Literal, Mapping

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool

from Build.agent import core
from Build.api.workspace.auth import error, require_owner


class Turn(BaseModel):
    text: str = Field(min_length=1, max_length=core.MAX_TEXT)
    contributor: bool = False  # per-user mode, resolved by the BFF from the user's saved choice
    tier: Literal["spark", "open"] = "spark"  # N36 Standard model: Muse Spark 1.3 or Muse Open; ignored for contributor
    history: list[dict[str, Any]] = Field(default_factory=list, max_length=core.MAX_HISTORY)


def create_router(post: Callable = core.http_post, post_file: Callable = core.http_post_file,
                  handlers: Mapping[str, Callable] | None = None) -> APIRouter:
    from Build.api.agent.handlers import HANDLERS
    handlers = HANDLERS if handlers is None else handlers
    router = APIRouter(prefix="/workspace/agent")

    @router.post("/turn")
    def turn(body: Turn, owner: str = Depends(require_owner)):
        try:
            return core.run_turn(body.text, post, owner=owner, contributor=body.contributor,
                                 tier=body.tier, history=body.history, handlers=handlers)
        except core.ModelUnavailable as exc:
            raise error(502, "AGENT_UNAVAILABLE", f"model call failed: {exc}") from None

    @router.post("/transcribe")
    async def transcribe(request: Request, owner: str = Depends(require_owner)):
        declared = request.headers.get("content-length", "")
        if declared.isdigit() and int(declared) > core.MAX_AUDIO_BYTES:
            raise error(413, "AUDIO_TOO_LARGE", "audio exceeds 4 MB")
        audio = bytearray()
        async for chunk in request.stream():  # cap while reading: never buffer more than the limit
            audio += chunk
            if len(audio) > core.MAX_AUDIO_BYTES:
                raise error(413, "AUDIO_TOO_LARGE", "audio exceeds 4 MB")
        try:
            return await run_in_threadpool(core.transcribe, bytes(audio), post_file)
        except ValueError as exc:
            raise error(422, "BAD_AUDIO", str(exc)) from None
        except core.ModelUnavailable as exc:
            raise error(502, "TRANSCRIBE_UNAVAILABLE", f"transcription failed: {exc}") from None

    return router

