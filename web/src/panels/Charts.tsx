import { CartesianGrid, Line, LineChart, ResponsiveContainer, XAxis, YAxis } from "recharts";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import type { HistoryPoint } from "@/hooks/useSimSocket";

const SERIES = [
  { key: "l0", name: "RF", color: "#000000", dash: undefined },
  { key: "l1", name: "RM", color: "#1B8A73", dash: undefined },
  { key: "l5", name: "LF", color: "#E0A400", dash: "7 5" },
] as const;

export function Charts({ history }: { history: HistoryPoint[] }) {
  return (
    <Card className="flex h-[210px] flex-col overflow-hidden">
      <CardHeader>
        <CardTitle>Góc femur θ2 · 4 giây gần nhất</CardTitle>
        {/* Tripod: RM và LF cùng nhóm nên trùng nhau; LF vẽ nét đứt để vẫn thấy RM. */}
        <div className="flex gap-3 text-[13px] font-bold">
          {SERIES.map((s) => (
            <span key={s.key} className="flex items-center gap-1.5">
              <i className="inline-block h-1 w-[18px]" style={{ background: s.dash ? `repeating-linear-gradient(90deg, ${s.color} 0 6px, transparent 6px 9px)` : s.color }} />
              {s.name}
            </span>
          ))}
        </div>
      </CardHeader>
      <div className="min-h-0 flex-1 px-2 pb-1 pt-2">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={history} margin={{ top: 4, right: 12, bottom: 0, left: -12 }}>
            <CartesianGrid stroke="#00000022" strokeDasharray="5 5" vertical={false} />
            <XAxis dataKey="t" type="number" domain={["dataMin", "dataMax"]} tickFormatter={(v: number) => `${v.toFixed(1)}s`}
              stroke="#000" strokeWidth={3} tick={{ fontFamily: "JetBrains Mono", fontSize: 11, fill: "#000" }} />
            <YAxis domain={[-0.2, 1.0]} ticks={[-0.2, 0.4, 1.0]} stroke="#000" strokeWidth={3}
              tick={{ fontFamily: "JetBrains Mono", fontSize: 11, fill: "#000" }} unit=" rad" width={70} />
            {SERIES.map((s) => (
              <Line key={s.key} dataKey={s.key} name={s.name} stroke={s.color} strokeWidth={3} strokeDasharray={s.dash} dot={false} isAnimationActive={false} />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}
