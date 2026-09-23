import json

from fastapi.testclient import TestClient

from hexapod.server.app import create_app


def test_websocket_roundtrip():
    app = create_app()
    with TestClient(app) as client:
        with client.websocket_connect("/ws") as ws:
            hello = json.loads(ws.receive_text())
            assert hello["type"] == "hello" and len(hello["robot"]["lengths"]) == 3
            state = json.loads(ws.receive_text())
            assert state["type"] == "state" and len(state["q"]) == 6
            ws.send_text(json.dumps({"type": "config", "gait": "wave"}))
            ws.send_text(json.dumps({"type": "command", "vx": 0.03, "vy": 0, "wz": 0}))
            ws.send_text(json.dumps({"type": "command", "vx": 9}))
            got_error = got_wave = False
            for _ in range(40):
                m = json.loads(ws.receive_text())
                got_error |= m["type"] == "error"
                got_wave |= m.get("gait") == "wave"
                if got_error and got_wave:
                    break
            assert got_error and got_wave
