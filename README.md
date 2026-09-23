# Hexapod Sim — mô phỏng robot 6 chân bằng Python

Mô phỏng hexapod 18 khớp (6 chân × 3 DOF): động học thuận/nghịch giải tích, dáng đi tripod/ripple/wave,
tư thế thân, backend **kinematic** và **MuJoCo** (vật lý), web UI 3D phong cách NeoBrutalism,
log CSV và wrapper Gymnasium cho RL.

## Yêu cầu

- Python 3.11+
- Node.js 20+ (chỉ cần cho web UI)

## Chạy nhanh

```bash
# 1. Cài Python (khuyến nghị dùng venv)
python -m venv .venv && source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[physics,viz,dev]"

# 2. Build web UI một lần
cd web && npm install && npm run build && cd ..

# 3. Chạy server + UI
python scripts/run_server.py --log-dir runs
# mở http://127.0.0.1:8000
```

Muốn sửa giao diện với hot reload: chạy server như bước 3, rồi ở terminal khác
`cd web && npm run dev` và mở http://localhost:5173 (Vite tự chuyển tiếp `/ws`, `/api` sang cổng 8000).

## Các lệnh khác

| Lệnh | Việc làm |
| --- | --- |
| `python scripts/run_server.py --backend mujoco` | Server khởi động với backend vật lý |
| `python scripts/run_kinematic.py configs/scenarios/walk_square.yaml --plot` | Chạy kịch bản headless, ghi log, vẽ đồ thị |
| `python scripts/run_physics.py configs/scenarios/walk_square.yaml` | Chạy kịch bản trong MuJoCo (headless) |
| `python scripts/run_physics.py --viewer` | Cửa sổ MuJoCo, điều khiển bằng phím I/K/J/L/U/O, 1/2/3 đổi dáng đi |
| `python scripts/run_physics.py --export-mjcf models/hexapod.xml` | Xuất mô hình MJCF từ config |
| `pytest -q` | Chạy test Python |
| `cd web && npm test` | Chạy test frontend |

## Điều khiển trên web UI

- Slider: vận tốc vx, vy, ωz; chiều cao, roll, pitch; độ cao nhấc chân.
- Phím: `W/S` tiến lùi, `A/D` sang ngang, `Q/E` xoay, `X` dừng, `Space` tạm dừng.
- Nút Kinematic / MuJoCo đổi backend (MuJoCo cần `pip install -e ".[physics]"`).
- "Tải kịch bản" nhận file YAML như `configs/scenarios/walk_square.yaml`.
- "Tải log CSV" chỉ hoạt động khi server chạy với `--log-dir`.

## Cấu trúc

```
configs/                 thông số robot (YAML) và kịch bản
src/hexapod/
  config.py              Pydantic models, đọc YAML
  geometry.py            ma trận quay, quaternion
  kinematics.py          LegKinematics: fk(), ik(), ik_clamped()
  body.py                BodyPose: hệ heading -> thân -> chân
  gait/                  Gait (base) + tripod, ripple, wave; GaitScheduler (chuyển dáng đi mượt)
  trajectory.py          quỹ đạo stance/swing của đầu chân
  controller.py          HexapodController: lệnh -> 18 góc khớp
  stability.py           bao lồi + lề ổn định
  backends/              KinematicBackend, MujocoBackend
  mjcf.py                sinh mô hình MuJoCo từ config
  sim.py                 Simulation: controller + backend + ổn định
  io/                    CsvLogger, Scenario/ScenarioRunner
  server/                FastAPI + WebSocket /ws
  envs/hexapod_env.py    Gymnasium (residual policy)
  viz/plots.py           đồ thị Matplotlib
scripts/                 run_server, run_kinematic, run_physics
tests/                   pytest + hypothesis
web/                     React + TypeScript + Tailwind + react-three-fiber
```

## Quy ước

- Đơn vị SI (m, rad, s) trong mã nguồn; độ chỉ dùng trong YAML và giao diện.
- Hệ thế giới: Z hướng lên, X hướng về trước. Chân đánh số 0–5: RF, RM, RR, LR, LM, LF.
- θ2 dương = nâng đùi; θ3 = 0 khi duỗi thẳng, âm khi gập xuống. IK chọn nghiệm "gối hướng lên".

## Thêm dáng đi mới

Tạo một class trong `src/hexapod/gait/`, khai báo `name`, `beta`, `period`, `offsets`, `min_stance`,
rồi thêm vào `GAITS` trong `gait/__init__.py`. Không cần sửa controller.

## Giới hạn hiện tại

- Backend kinematic không có vật lý: robot không ngã, chân có thể trượt nhẹ khi đổi vận tốc đột ngột.
- Controller chạy vòng hở (không dùng IMU để cân bằng); MuJoCo đi ổn định trên nền phẳng với cấu hình mặc định.
- Web UI chỉ đọc thông số hình học lúc kết nối; đổi file config cần khởi động lại server.
