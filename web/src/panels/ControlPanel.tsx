import { useRef } from "react";
import { Button } from "@/components/ui/button";
import { Kbd } from "@/components/ui/badge";
import { Slider } from "@/components/ui/slider";
import type { GaitName, HelloMsg } from "@/lib/types";

export interface Controls {
  vx: number;
  vy: number;
  wz: number;
  height: number;
  roll: number; // độ
  pitch: number; // độ
  swingHeight: number;
}

interface Props {
  hello: HelloMsg | null;
  controls: Controls;
  gait: GaitName | undefined;
  running: boolean | undefined;
  scenarioActive: boolean | undefined;
  onControls: (patch: Partial<Controls>) => void;
  onGait: (g: GaitName) => void;
  onAction: (a: "start" | "pause" | "step" | "reset") => void;
  onScenario: (yaml: string | null) => void;
}

const GAIT_LABEL: Record<GaitName, string> = { tripod: "Tripod", ripple: "Ripple", wave: "Wave" };

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="flex flex-col gap-2.5">
      <h2 className="m-0 text-base font-bold">{title}</h2>
      {children}
    </section>
  );
}

export function ControlPanel({ hello, controls: c, gait, running, scenarioActive, onControls, onGait, onAction, onScenario }: Props) {
  const file = useRef<HTMLInputElement>(null);
  const g = gait && hello?.gaits[gait];
  return (
    <aside aria-label="Bảng điều khiển" className="flex min-h-0 flex-col gap-5 overflow-auto rounded-base border-3 border-ink bg-white p-4 shadow-brutal">
      <Section title="Mô phỏng">
        <div className="grid grid-cols-3 gap-2.5">
          <Button variant="main" onClick={() => onAction(running ? "pause" : "start")}>{running ? "Pause" : "Start"}</Button>
          <Button onClick={() => onAction("step")}>Step</Button>
          <Button variant="danger" onClick={() => onAction("reset")}>Reset</Button>
        </div>
      </Section>

      <Section title="Dáng đi">
        <div className="grid grid-cols-3 gap-2.5">
          {(Object.keys(GAIT_LABEL) as GaitName[]).map((name) => (
            <Button key={name} pressed={gait === name} variant={gait === name ? "main" : "default"} onClick={() => onGait(name)}>
              {GAIT_LABEL[name]}
            </Button>
          ))}
        </div>
        {g && <div className="font-mono text-[13px]">β = {g.beta.toFixed(2)} · T = {g.period.toFixed(1)} s</div>}
      </Section>

      <Section title="Vận tốc">
        <Slider label="Tiến/lùi vx" value={c.vx} min={-0.1} max={0.1} step={0.005} format={(v) => `${v.toFixed(3)} m/s`} onChange={(vx) => onControls({ vx })} />
        <Slider label="Sang ngang vy" value={c.vy} min={-0.08} max={0.08} step={0.005} format={(v) => `${v.toFixed(3)} m/s`} onChange={(vy) => onControls({ vy })} />
        <Slider label="Xoay ωz" value={c.wz} min={-0.8} max={0.8} step={0.05} format={(v) => `${v.toFixed(2)} rad/s`} onChange={(wz) => onControls({ wz })} />
      </Section>

      <Section title="Tư thế thân">
        <Slider label="Chiều cao" value={c.height} min={0.06} max={0.14} step={0.005} format={(v) => `${v.toFixed(3)} m`} onChange={(height) => onControls({ height })} />
        <Slider label="Roll" value={c.roll} min={-15} max={15} step={1} format={(v) => `${v.toFixed(0)}°`} onChange={(roll) => onControls({ roll })} />
        <Slider label="Pitch" value={c.pitch} min={-15} max={15} step={1} format={(v) => `${v.toFixed(0)}°`} onChange={(pitch) => onControls({ pitch })} />
        <Slider label="Độ cao nhấc chân" value={c.swingHeight} min={0.01} max={0.07} step={0.005} format={(v) => `${v.toFixed(3)} m`} onChange={(swingHeight) => onControls({ swingHeight })} />
      </Section>

      <Section title="Kịch bản & log">
        <input
          ref={file}
          type="file"
          accept=".yaml,.yml"
          className="hidden"
          onChange={async (e) => {
            const f = e.target.files?.[0];
            if (f) onScenario(await f.text());
            e.target.value = "";
          }}
        />
        <div className="grid grid-cols-2 gap-2.5">
          {scenarioActive ? (
            <Button variant="danger" className="whitespace-nowrap px-2 text-[13px]" onClick={() => onScenario(null)}>Dừng kịch bản</Button>
          ) : (
            <Button className="whitespace-nowrap px-2 text-[13px]" onClick={() => file.current?.click()}>Tải kịch bản</Button>
          )}
          <a
            href="/api/log.csv"
            className="nb-focus inline-flex h-11 items-center justify-center whitespace-nowrap rounded-base border-3 border-ink bg-white px-2 text-[13px] font-bold text-ink shadow-brutal hover:-translate-x-px hover:-translate-y-px hover:shadow-brutal-hover"
          >
            Tải log CSV
          </a>
        </div>
      </Section>

      <Section title="Phím tắt">
        <div className="flex flex-wrap gap-2">
          <Kbd>W S</Kbd>
          <Kbd>A D</Kbd>
          <Kbd>Q E</Kbd>
          <Kbd>X dừng</Kbd>
          <Kbd>Space</Kbd>
        </div>
        <p className="m-0 text-[13px] leading-snug">Kéo chuột để xoay camera, cuộn để zoom. Camera bám theo robot.</p>
      </Section>
    </aside>
  );
}
