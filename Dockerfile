# ---- build web UI ----
FROM node:20-slim AS web
WORKDIR /web
COPY web/package.json web/package-lock.json ./
RUN npm ci
COPY web/ ./
RUN npm run build

# ---- runtime ----
FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src/ src/
RUN pip install --no-cache-dir -e ".[physics]"
COPY scripts/ scripts/
COPY configs/ configs/
COPY --from=web /web/dist web/dist

EXPOSE 8000
CMD ["python", "scripts/run_server.py", "--host", "0.0.0.0", "--backend", "kinematic"]
