FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY Build/worker/health/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY Build/api/health/dependencies.py /app/Build/api/health/dependencies.py
COPY Build/worker/health /app/Build/worker/health
ARG R2S_SOURCE_REVISION
ENV RAILWAY_GIT_COMMIT_SHA=$R2S_SOURCE_REVISION
CMD ["sh", "-c", "exec python -m uvicorn Build.worker.health.app:app --host 0.0.0.0 --port ${PORT:-8080}"]
