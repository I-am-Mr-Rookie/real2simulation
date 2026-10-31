FROM python:3.12-slim
# S15av: the lab bridge spawns Build/lab/simulate.mjs; copy only the Node runtime binary.
COPY --from=node:22-bookworm-slim /usr/local/bin/node /usr/local/bin/node
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY Build/api/health/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
# Context is only stage.py's allowlisted committed files.
COPY . /app
# Build-time import smoke: the image fails to build if any mounted router cannot import.
RUN python -B -c "import Build.api.health.app" && node --version
ARG R2S_SOURCE_REVISION
ENV RAILWAY_GIT_COMMIT_SHA=$R2S_SOURCE_REVISION
CMD ["sh", "-c", "exec python -m uvicorn Build.api.health.app:app --host 0.0.0.0 --port ${PORT:-8080}"]
