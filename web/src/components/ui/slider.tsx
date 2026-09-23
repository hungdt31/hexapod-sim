import { useId } from "react";

interface Props {
  label: string;
  value: number;
  min: number;
  max: number;
  step: number;
  format: (v: number) => string;
  onChange: (v: number) => void;
}

export function Slider({ label, value, min, max, step, format, onChange }: Props) {
  const id = useId();
  return (
    <div className="flex flex-col gap-1.5">
      <div className="flex justify-between text-sm font-medium">
        <label htmlFor={id}>{label}</label>
        <output htmlFor={id} className="font-mono font-bold tabular-nums">
          {format(value)}
        </output>
      </div>
      <input
        id={id}
        type="range"
        className="nb-range nb-focus"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
      />
    </div>
  );
}
