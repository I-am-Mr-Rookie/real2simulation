FROM python:3.12-slim
# S15av: the lab bridge spawns Build/lab/simulate.mjs; copy only the Node runtime binary.
COPY --from=node:22-bookworm-slim /usr/local/bin/node /usr/local/bin/node
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
# N11: ffmpeg gives ffprobe (upload duration) and frame sampling for the live pipelines.
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY Build/api/health/requirements.txt /app/requirements.txt
# modal (pinned like Build/gpu/ondemand.py) is the client for the on-demand GPU app; python-multipart is in requirements.
RUN pip install --no-cache-dir -r requirements.txt modal==1.6.3
# Context is only stage.py's allowlisted committed files.
COPY . /app
# Build-time import smoke: the image fails to build if any mounted router cannot import.
RUN python -B -c "import Build.api.health.app, modal" && node --version && ffprobe -version | head -n 1
ARG R2S_SOURCE_REVISION
ENV RAILWAY_GIT_COMMIT_SHA=$R2S_SOURCE_REVISION
CMD ["sh", "-c", "exec python -m uvicorn Build.api.health.app:app --host 0.0.0.0 --port ${PORT:-8080}"]
