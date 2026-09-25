import { lazy, Suspense, useCallback, useEffect, useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardHeader } from "@/components/ui/card";
import { useSimSocket } from "@/hooks/useSimSocket";
import type { BackendName, GaitName } from "@/lib/types";
import { deg, rad } from "@/lib/utils";
import { ControlPanel, type Controls } from "@/panels/ControlPanel";
import { Telemetry } from "@/panels/Telemetry";
import { TopBar } from "@/panels/TopBar";
import type { CamPreset } from "@/scene/SceneCanvas";

// Tách chunk riêng cho three.js/fiber/drei (scene) và recharts (charts) — hai phần nặng nhất bundle.
const SceneCanvas = lazy(() => import("@/scene/SceneCanvas").then((m) => ({ default: m.SceneCanvas })));
const Charts = lazy(() => import("@/panels/Charts").then((m) => ({ default: m.Charts })));

const DEFAULTS: Controls = { vx: 0, vy: 0, wz: 0, height: 0.1, roll: 0, pitch: 0, swingHeight: 0.04 };

export default function App() {
  const { hello, state, stateRef, history, status, error, clearError, send } = useSimSocket();
  const [controls, setControls] = useState<Controls>(DEFAULTS);
  const [cam, setCam] = useState<CamPreset>("iso");
  const synced = useRef(false);

  // Lần đầu nhận state: lấy lệnh và tư thế hiện tại từ server để slider khớp.
  useEffect(() => {
    if (!state || synced.current) return;
    synced.current = true;
    setControls((c) => ({
      ...c,
      ...state.command,
      height: state.body_pose.height,
      roll: Math.round(deg(state.body_pose.roll)),
      pitch: Math.round(deg(state.body_pose.pitch)),
    }));
  }, [state]);
  useEffect(() => {
    if (status !== "open") synced.current = false;
  }, [status]);

  const update = useCallback(
    (patch: Partial<Controls>) => {
      setControls((prev) => {
        const next = { ...prev, ...patch };
        if ("vx" in patch || "vy" in patch || "wz" in patch) send({ type: "command", vx: next.vx, vy: next.vy, wz: next.wz });
        if ("height" in patch || "roll" in patch || "pitch" in patch)
          send({ type: "config", body_pose: { height: next.height, rpy: [rad(next.roll), rad(next.pitch), 0] } });
        if ("swingHeight" in patch) send({ type: "config", swing_height: next.swingHeight });
        return next;
      });
    },
    [send],
  );

  // Phím tắt: W/S tiến lùi, A/D ngang, Q/E xoay, X dừng, Space tạm dừng.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const el = e.target as HTMLElement | null;
      if (el && (el.tagName === "TEXTAREA" || (el.tagName === "INPUT" && (el as HTMLInputElement).type !== "range"))) return;
      if (e.metaKey || e.ctrlKey || e.altKey) return;
      const k = e.key.toLowerCase();
      const map: Record<string, Partial<Controls>> = {
        w: { vx: 0.06 }, s: { vx: -0.06 }, a: { vy: 0.04 }, d: { vy: -0.04 }, q: { wz: 0.5 }, e: { wz: -0.5 },
        x: { vx: 0, vy: 0, wz: 0 },
      };
      if (map[k]) {
        update(map[k]);
        e.preventDefault();
      } else if (k === " ") {
        send({ type: "control", action: stateRef.current?.running ? "pause" : "start" });
        e.preventDefault();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [update, send, stateRef]);

  return (
    <div className="flex min-h-full flex-col gap-[18px] p-[18px] lg:h-full">
      <TopBar
        status={status}
        backend={state?.backend}
        available={hello?.backends ?? ["kinematic"]}
        running={state?.running}
        hz={hello?.broadcast_hz}
        onBackend={(b: BackendName) => send({ type: "config", backend: b })}
      />

      {error && (
        <div role="alert" className="flex items-center justify-between gap-3 rounded-base border-3 border-ink bg-danger px-4 py-2 font-bold shadow-brutal">
          <span>{error}</span>
          <Button size="sm" onClick={clearError}>Đóng</Button>
        </div>
      )}

      <div className="grid min-h-0 flex-1 grid-cols-1 gap-[18px] lg:grid-cols-[300px_minmax(0,1fr)_340px]">
        <main className="order-first flex min-h-0 min-w-0 flex-col gap-[18px] lg:order-none lg:col-start-2 lg:row-start-1">
          <Card className="flex min-h-[60vh] flex-1 flex-col overflow-hidden lg:min-h-[320px]">
            <CardHeader className="bg-main">
              <div className="flex flex-wrap gap-3 text-[13px] font-bold">
                <span className="flex items-center gap-1.5"><i className="inline-block h-3.5 w-3.5 border-2 border-ink bg-main" />Swing</span>
                <span className="flex items-center gap-1.5"><i className="inline-block h-3.5 w-3.5 border-2 border-ink bg-accent" />Stance</span>
                <span className="flex items-center gap-1.5"><i className="inline-block h-3.5 w-3.5 border-2 border-dashed border-ink bg-[#9FE6D5]" />Support polygon</span>
                <span className="flex items-center gap-1.5"><i className="inline-block h-3.5 w-3.5 rounded-full border-2 border-ink bg-danger" />CoM</span>
              </div>
              <div className="flex gap-2">
                {(["iso", "top", "side"] as const).map((p) => (
                  <Button key={p} size="sm" pressed={cam === p} onClick={() => setCam(p)}>
                    {p === "iso" ? "3/4" : p === "top" ? "Trên" : "Bên"}
                  </Button>
                ))}
              </div>
            </CardHeader>
            <div className="relative min-h-0 flex-1">
              <Suspense fallback={<div className="flex h-full items-center justify-center font-bold">Đang tải 3D…</div>}>
                <SceneCanvas hello={hello} stateRef={stateRef} preset={cam} />
              </Suspense>
              {status !== "open" && (
                <div className="absolute inset-0 flex items-center justify-center p-6 text-center font-bold">
                  <div className="rounded-base border-3 border-ink bg-white px-5 py-4 shadow-brutal">
                    Chưa kết nối được server mô phỏng. Chạy <code className="font-mono">python scripts/run_server.py</code> rồi đợi vài giây.
                  </div>
                </div>
              )}
            </div>
          </Card>
          <Suspense fallback={null}>
            <Charts history={history} />
          </Suspense>
        </main>

        <div className="lg:col-start-1 lg:row-start-1 lg:flex lg:min-h-0 lg:flex-col">
          <ControlPanel
            hello={hello}
            controls={controls}
            gait={state?.gait}
            running={state?.running}
            scenarioActive={state?.scenario_active}
            onControls={update}
            onGait={(g: GaitName) => send({ type: "config", gait: g })}
            onAction={(a) => {
              send({ type: "control", action: a });
            }}
            onScenario={(yaml) => send({ type: "scenario", yaml })}
          />
        </div>

        <div className="lg:col-start-3 lg:row-start-1 lg:flex lg:min-h-0 lg:flex-col">
          <Telemetry state={state} hello={hello} />
        </div>
      </div>
    </div>
  );
}
