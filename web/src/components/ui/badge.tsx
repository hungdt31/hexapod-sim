import * as React from "react";
import { cn } from "@/lib/utils";

export function Badge({ className, ...props }: React.HTMLAttributes<HTMLSpanElement>) {
  return (
    <span
      className={cn("inline-flex items-center gap-2 rounded-base border-3 border-ink px-2.5 py-1 text-[13px] font-bold", className)}
      {...props}
    />
  );
}

export function Kbd({ className, ...props }: React.HTMLAttributes<HTMLElement>) {
  return (
    <kbd
      className={cn("rounded-[3px] border-2 border-ink bg-bg px-2 py-0.5 font-mono text-xs font-bold shadow-brutal-sm", className)}
      {...props}
    />
  );
}
