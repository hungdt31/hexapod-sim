import type { HelloMsg, StateMsg } from "@/lib/types";
import { cn, deg } from "@/lib/utils";

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-base border-3 border-ink px-2.5 py-2">
      <div className="text-xs font-bold">{label}</div>
      <div className="font-mono text-[17px] font-bold tabular-nums">{value}</div>
    </div>
  );
}

export function Telemetry({ state, hello }: { state: StateMsg | null; hello: HelloMsg | null }) {
  const m = state?.stability_margin ?? 0;
  const ok = m >= 0.01;
  const names = hello?.robot.leg_names ?? ["RF", "RM", "RR", "LR", "LM", "LF"];
  const yaw = state ? Math.round((((deg(state.body.rpy[2]) % 360) + 540) % 360) - 180) : 0;
  return (
    <aside aria-label="Telemetry" className="flex min-h-0 flex-col gap-4 overflow-auto rounded-base border-3 border-ink bg-white p-4 shadow-brutal">
      <h2 className="m-0 text-base font-bold">Telemetry</h2>
      <div className={cn("rounded-base border-3 border-ink p-3 shadow-brutal", ok ? "bg-accent" : "bg-danger")}>
        <div className="text-[13px] font-bold">Lề ổn định</div>
        <div className="font-mono text-[32px] font-bold leading-tight tabular-nums">
          {state ? `${m >= 0 ? "+" : ""}${m.toFixed(3)} m` : "—"}
        </div>
        <div className="text-[13px] font-medium">
          {ok ? "CoM nằm trong đa giác chống đỡ" : "Cảnh báo: CoM sát hoặc ra ngoài đa giác"}
        </div>
      </div>
      <div className="grid grid-cols-2 gap-2.5">
        <Stat label="Thời gian" value={`${(state?.t ?? 0).toFixed(2)} s`} />
        <Stat label="Vị trí (x, y)" value={state ? `${state.body.pos[0].toFixed(2)}, ${state.body.pos[1].toFixed(2)}` : "—"} />
        <Stat label="Hướng yaw" value={`${yaw}°`} />
        <Stat label="Chân chạm đất" value={`${state ? state.contacts.filter(Boolean).length : 6} / 6`} />
        <Stat label="Độ dài bước" value={`${(state?.stride ?? 0).toFixed(3)} m`} />
        <Stat label="Cảnh báo IK" value={String(state?.ik_warn ?? 0)} />
      </div>
      <h2 className="m-0 mt-1 text-base font-bold">Góc khớp (độ)</h2>
      <div className="overflow-x-auto">
        <table className="w-full border-collapse font-mono text-[13px] tabular-nums">
          <thead>
            <tr className="bg-bg">
              {["Chân", "Pha", "θ1", "θ2", "θ3"].map((h, i) => (
                <th key={h} className={cn("border-2 border-ink px-1.5 py-1", i === 0 ? "text-left" : "text-right")}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {names.map((n, i) => {
              const c = state?.contacts[i] ?? true;
              return (
                <tr key={n}>
                  <td className="border-2 border-ink px-1.5 py-1">{i} {n}</td>
                  <td className={cn("border-2 border-ink px-1.5 py-1 text-center font-bold", c ? "bg-accent" : "bg-main")}>
                    {c ? "Stance" : "Swing"}
                  </td>
                  {[0, 1, 2].map((j) => (
                    <td key={j} className="border-2 border-ink px-1.5 py-1 text-right">
                      {state ? deg(state.q[i][j]).toFixed(1) : "—"}
                    </td>
                  ))}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </aside>
  );
}
