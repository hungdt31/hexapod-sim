# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Hexapod Sim: a Python simulation of an 18-DOF (6 legs × 3 DOF) hexapod robot — analytic
forward/inverse kinematics, tripod/ripple/wave gaits, body pose control, a kinematic backend and a
MuJoCo physics backend, a React/Three.js web UI, CSV logging, and a Gymnasium wrapper for RL.

README.md is in Vietnamese and is the source of truth for user-facing docs; keep it in sync with
behavior changes.

## Commands

Python (from repo root, after `pip install -e ".[physics,viz,dev]"`):
```bash
python scripts/run_server.py --log-dir runs          # server + web UI at http://127.0.0.1:8000
python scripts/run_server.py --backend mujoco         # server with physics backend
python scripts/run_kinematic.py configs/scenarios/walk_square.yaml --plot   # headless scenario, kinematic backend
python scripts/run_physics.py configs/scenarios/walk_square.yaml            # headless scenario, MuJoCo
python scripts/run_physics.py --viewer                # MuJoCo viewer; keys I/K/J/L/U/O move, 1/2/3 switch gait
python scripts/run_physics.py --export-mjcf models/hexapod.xml              # export MJCF from config

pytest -q                                              # run all tests
pytest tests/test_kinematics.py -q                     # single test file
pytest tests/test_kinematics.py::test_name -q          # single test

ruff check src tests scripts                           # lint (also runs via pre-commit)
ruff check --fix src tests scripts
mypy src                                                # type check
```

Web UI (from `web/`):
```bash
npm install
npm run dev          # Vite dev server on :5173, proxies /ws and /api to :8000
npm run build         # tsc -b && vite build -> web/dist, served by the FastAPI app
npm test              # vitest run
npm run typecheck
```

CI (`.github/workflows/ci.yml`) runs `ruff check`, `pytest -q` for Python, and `npm run build` +
`npm test` for web on every push/PR — mirror these before considering work done.

## Architecture

### Control pipeline (`src/hexapod/`)

A single per-tick pipeline turns a body-velocity command into 18 joint angles:

```
command (vx, vy, wz, body pose) -> HexapodController -> ControlOutput (q, swing, progress, ...)
    -> SimBackend.step(q, dt) -> RobotState (joint angles, body pose, foot contacts, COM)
    -> stability.py (convex hull of stance feet + COM margin) -> Frame
```

- `config.py` — Pydantic models loaded from YAML (`configs/robot_default.yaml`); `RobotConfig.load()`
  is the entry point. Angles/lengths in config + UI are degrees/human units; everything inside the
  simulation core is SI (m, rad, s) — see README "Quy ước" for the exact convention (world frame Z-up,
  X-forward, legs numbered 0–5 as RF, RM, RR, LR, LM, LF; θ2 positive lifts thigh, θ3=0 is straight,
  negative is bent; IK picks the "knee up" solution).
- `geometry.py` — rotation matrices / quaternions used throughout.
- `kinematics.py` (`LegKinematics`) — analytic `fk()`/`ik()`/`ik_clamped()` per leg.
- `body.py` (`BodyPose`) — heading -> body -> leg frame chain.
- `gait/` — `Gait` base class + `TripodGait`/`RippleGait`/`WaveGait`, each declaring `name`, `beta`,
  `period`, `offsets`, `min_stance`; registered in `GAITS` (`gait/__init__.py`). `GaitScheduler`
  handles smooth gait transitions. **To add a gait**: create a class in `gait/`, register it in
  `GAITS` — the controller needs no changes.
- `trajectory.py` — swing/stance foot-tip trajectories.
- `controller.py` (`HexapodController`) — ties gait + trajectory + kinematics together; command in,
  18 joint angles (`ControlOutput`) out.
- `stability.py` — support-polygon convex hull and stability margin.
- `backends/` — `SimBackend` protocol (`base.py`) with two implementations: `KinematicBackend`
  (no physics; feet don't slip except under abrupt velocity changes, robot cannot fall) and
  `MujocoBackend` (real physics, needs the `physics` extra). `make_backend()` in `__init__.py` is the
  factory; add new backends there.
- `mjcf.py` — generates a MuJoCo MJCF model from `RobotConfig` (used by `--export-mjcf` and
  `MujocoBackend`).
- `sim.py` (`Simulation`) — the top-level loop: controller + backend + stability, produces a `Frame`
  per `step()`; `Frame.to_message()` is the exact JSON shape sent to the web UI over WebSocket.
- `io/` — `CsvLogger` (state logging) and `Scenario`/`ScenarioRunner` (YAML-driven headless scripts
  under `configs/scenarios/`).
- `server/` — FastAPI app (`app.py`): `/api/health`, `/api/state`, `/api/log.csv`, and the `/ws`
  WebSocket that streams `Frame.to_message()` and accepts client commands (validated via
  `schemas.py`'s `client_adapter`). `sim_loop.py`'s `SimRunner` owns the `Simulation` instance, the
  background tick loop, connected clients, and broadcasting. Serves the built `web/dist` as static
  files when present, otherwise a plain-text fallback message.
- `envs/hexapod_env.py` — Gymnasium environment wrapping `Simulation` as a residual-policy RL env.
- `viz/plots.py` — Matplotlib plots for headless scenario runs (`--plot`).

### Web UI (`web/`)

React + TypeScript + Tailwind + react-three-fiber/drei/three, built with Vite. `useSimSocket.ts`
owns the `/ws` connection and state; `scene/` renders the 3D hexapod and ground; `panels/` are the
control/telemetry/chart UI (NeoBrutalism style); `App.tsx` composes them. The UI only reads robot
geometry at connect time — changing the config file requires restarting the server.

### Scenarios and configs

`configs/robot_default.yaml` is the default robot config; `configs/scenarios/*.yaml` are
scripted command sequences consumed by `io/script.py`'s `ScenarioRunner`, runnable headless via
`run_kinematic.py`/`run_physics.py` or loadable from the web UI ("Tải kịch bản").
