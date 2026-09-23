import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { ConnStatus } from "@/hooks/useSimSocket";
import type { BackendName } from "@/lib/types";
import { cn } from "@/lib/utils";

interface Props {
  status: ConnStatus;
  backend: BackendName | undefined;
  available: BackendName[];
  running: boolean | undefined;
  hz: number | undefined;
  onBackend: (b: BackendName) => void;
}

const STATUS_TEXT: Record<ConnStatus, string> = {
  open: "Đã kết nối",
  connecting: "Đang kết nối…",
  closed: "Mất kết nối, đang thử lại",
};

export function TopBar({ status, backend, available, running, hz, onBackend }: Props) {
  return (
    <header className="flex flex-wrap items-center justify-between gap-4 rounded-base border-3 border-ink bg-white px-4 py-3 shadow-brutal">
      <div className="flex items-center gap-3.5">
        <span className="rounded-base border-3 border-ink bg-main px-3 py-1 text-xl font-bold tracking-wide">HEXAPOD/SIM</span>
        <span className="hidden font-medium sm:inline">Mô phỏng robot 6 chân · 18 khớp</span>
      </div>
      <div className="flex flex-wrap items-center gap-3">
        <span className="text-sm font-bold">Backend</span>
        {(["kinematic", "mujoco"] as const).map((b) => (
          <Button
            key={b}
            size="sm"
            pressed={backend === b}
            variant={backend === b ? "accent" : "default"}
            disabled={!available.includes(b)}
            title={available.includes(b) ? undefined : "Cài MuJoCo: pip install -e '.[physics]'"}
            onClick={() => onBackend(b)}
          >
            {b === "kinematic" ? "Kinematic" : "MuJoCo"}
          </Button>
        ))}
        <Badge className={cn(status === "open" ? "bg-accent" : status === "closed" ? "bg-danger" : "bg-main")}>
          <i className="inline-block h-2.5 w-2.5 bg-ink" />
          {STATUS_TEXT[status]}
          {status === "open" && hz ? ` · ${hz} Hz` : ""}
          {status === "open" && running === false ? " · tạm dừng" : ""}
        </Badge>
      </div>
    </header>
  );
}
