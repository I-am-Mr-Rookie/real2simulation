"""N05 agent API: POST /workspace/agent/turn and /workspace/agent/transcribe (owner-gated like workspace)."""
from __future__ import annotations

from typing import Any, Callable, Mapping

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool

from Build.agent import core
from Build.api.workspace.auth import error, require_owner


class Turn(BaseModel):
    text: str = Field(min_length=1, max_length=core.MAX_TEXT)
    contributor: bool = False  # per-user mode, resolved by the BFF from the user's saved choice
    history: list[dict[str, Any]] = Field(default_factory=list, max_length=core.MAX_HISTORY)


def create_router(post: Callable = core.http_post, post_file: Callable = core.http_post_file,
                  handlers: Mapping[str, Callable] | None = None) -> APIRouter:
    router = APIRouter(prefix="/workspace/agent")

    @router.post("/turn")
    def turn(body: Turn, owner: str = Depends(require_owner)):
        try:
            return core.run_turn(body.text, post, owner=owner, contributor=body.contributor,
                                 history=body.history, handlers=handlers)
        except core.ModelUnavailable as exc:
            raise error(502, "AGENT_UNAVAILABLE", f"model call failed: {exc}") from None

    @router.post("/transcribe")
    async def transcribe(request: Request, owner: str = Depends(require_owner)):
        audio = await request.body()  # shortcut: full body read before the 4 MB check; add a streaming cap if abused
        try:
            return await run_in_threadpool(core.transcribe, audio, post_file)
        except ValueError as exc:
            raise error(422, "BAD_AUDIO", str(exc)) from None
        except core.ModelUnavailable as exc:
            raise error(502, "TRANSCRIBE_UNAVAILABLE", f"transcription failed: {exc}") from None

    return router

