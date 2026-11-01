"""N03 per-user storage: SQLite metadata + files on disk, /internal/workspace/files and /projects routes."""
from fastapi import APIRouter, Depends

from Build.api.storage import files, sample
from Build.api.storage.files import Store, video_seconds


def create_router(store=None, probe=video_seconds):
    """files.create_router plus the N11 hook that seeds the SAMPLE project on a user's first list."""
    router = APIRouter()
    router.include_router(files.create_router(store, probe), dependencies=[Depends(sample.make_hook((lambda: store) if store else files._default))])
    return router
