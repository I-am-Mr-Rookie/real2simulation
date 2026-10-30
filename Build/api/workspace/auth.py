"""Internal-token + owner-header gate for /internal/workspace/* (S15m §2).

The web BFF proxy (S04n) is the only caller: it sends x-workspace-token (WORKSPACE_INTERNAL_TOKEN) and
x-workspace-owner (Clerk userId). The owner header is trusted only because the token proved the caller.
"""
import hmac
import os
import re

from fastapi import Header, HTTPException

TOKEN_ENV = "WORKSPACE_INTERNAL_TOKEN"
_OWNER = re.compile(r"[A-Za-z0-9_-]{1,128}")  # Clerk user ids; also safe inside owner-scoped storage keys


def error(status: int, code: str, message: str, **extra) -> HTTPException:
    """FastAPI error; body is {"detail": {"code": <reducer code>, "message": ..., ...}}."""
    return HTTPException(status_code=status, detail={"code": code, "message": message, **extra})


def require_owner(x_workspace_token: str | None = Header(default=None),
                  x_workspace_owner: str | None = Header(default=None)) -> str:
    expected = os.environ.get(TOKEN_ENV, "")
    # Unset server token fails closed; compare_digest on bytes avoids a timing oracle and non-ASCII TypeError.
    if not expected or not x_workspace_token or not hmac.compare_digest(
            x_workspace_token.encode(), expected.encode()):
        raise error(401, "UNAUTHORIZED", "internal workspace token missing or invalid")
    if not x_workspace_owner or not _OWNER.fullmatch(x_workspace_owner):
        raise error(401, "UNAUTHORIZED", "workspace owner header missing or invalid")
    return x_workspace_owner
