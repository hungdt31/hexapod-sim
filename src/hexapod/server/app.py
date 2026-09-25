"""FastAPI server: WebSocket /ws + phục vụ web UI đã build (web/dist)."""

from __future__ import annotations

import json
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError

from ..config import RobotConfig
from .schemas import client_adapter
from .sim_loop import SimRunner

log = logging.getLogger("hexapod.server")
WEB_DIST = Path(__file__).resolve().parents[3] / "web" / "dist"


def create_app(cfg: RobotConfig | None = None, backend: str | None = None, log_dir: str | None = None) -> FastAPI:
    cfg = cfg or RobotConfig.load(os.environ.get("HEXAPOD_CONFIG"))
    backend = backend or os.environ.get("HEXAPOD_BACKEND", "kinematic")
    log_dir = log_dir or os.environ.get("HEXAPOD_LOG_DIR")
    runner = SimRunner(cfg, backend, log_dir)

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        await runner.start()
        yield
        await runner.stop()

    app = FastAPI(title="Hexapod Sim", lifespan=lifespan)
    app.state.runner = runner

    @app.get("/api/health")
    async def health() -> dict:
        return {"ok": True, "backend": runner.sim.backend_name, "t": runner.sim.state.t}

    @app.get("/api/state")
    async def state() -> JSONResponse:
        return JSONResponse(runner.snapshot())

    @app.get("/api/log.csv")
    async def log_csv():
        if not runner.logger:
            return PlainTextResponse("Server chạy không bật log. Thêm --log-dir runs khi khởi động.", status_code=404)
        runner.logger.flush()
        return FileResponse(runner.logger.path, filename="state.csv", media_type="text/csv")

    @app.websocket("/ws")
    async def ws_endpoint(ws: WebSocket) -> None:
        await ws.accept()
        runner.clients.add(ws)
        await ws.send_text(json.dumps(runner.hello()))
        await ws.send_text(json.dumps(runner.snapshot()))
        try:
            while True:
                raw = await ws.receive_text()
                try:
                    msg = client_adapter.validate_json(raw)
                    err = runner.handle(msg)
                except (ValidationError, ValueError) as e:
                    err = str(e).splitlines()[0]
                if err:
                    await ws.send_text(json.dumps({"type": "error", "message": err}))
                else:
                    await runner.broadcast()
        except WebSocketDisconnect:
            pass
        finally:
            runner.clients.discard(ws)

    if WEB_DIST.exists():
        app.mount("/", StaticFiles(directory=WEB_DIST, html=True), name="web")
    else:
        @app.get("/")
        async def index() -> PlainTextResponse:
            return PlainTextResponse(
                "Hexapod server đang chạy. Chưa build web UI: cd web && npm install && npm run build "
                "(hoặc npm run dev rồi mở http://localhost:5173)."
            )

    return app
