FROM node:22-bookworm-slim
ENV NEXT_TELEMETRY_DISABLED=1
WORKDIR /app
COPY Build/web/package.json ./package.json
RUN npm install --no-audit --no-fund
COPY Build/web/src ./src
RUN npm run build
ENV NODE_ENV=production
CMD ["sh", "-c", "exec npm start -- --hostname 0.0.0.0 --port ${PORT:-8080}"]
