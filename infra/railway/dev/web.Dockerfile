FROM node:22-bookworm-slim
ENV NEXT_TELEMETRY_DISABLED=1
# Mirror the repo's Build/ layout so relative imports (../simulator, ../lab, ../library) resolve as locally.
WORKDIR /app/Build/web
COPY Build/web/package.json ./package.json
RUN npm install --no-audit --no-fund
# Context holds only stage.py's allowlist plus the guest snapshot (library-snapshot/guest.json, read at runtime).
COPY Build /app/Build
RUN npm run build
ENV NODE_ENV=production
CMD ["sh", "-c", "exec npm start -- --hostname 0.0.0.0 --port ${PORT:-8080}"]
