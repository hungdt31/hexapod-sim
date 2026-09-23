import * as React from "react";
import { cn } from "@/lib/utils";

type Variant = "default" | "main" | "accent" | "danger";
const variants: Record<Variant, string> = {
  default: "bg-white",
  main: "bg-main",
  accent: "bg-accent",
  danger: "bg-danger",
};

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  pressed?: boolean;
  size?: "md" | "sm";
}

/** Nút NeoBrutalism: viền đen 3px, bóng cứng, "lún" xuống khi bấm hoặc đang được chọn. */
export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "default", pressed, size = "md", ...props }, ref) => (
    <button
      ref={ref}
      aria-pressed={pressed}
      className={cn(
        "nb-focus inline-flex items-center justify-center rounded-base border-3 border-ink font-bold text-ink",
        "shadow-brutal transition-[transform,box-shadow] duration-75",
        "hover:-translate-x-px hover:-translate-y-px hover:shadow-brutal-hover",
        "active:translate-x-box active:translate-y-box active:shadow-none",
        "disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:translate-x-0 disabled:hover:translate-y-0",
        size === "md" ? "h-11 px-4 text-sm" : "h-9 px-3 text-[13px]",
        variants[variant],
        pressed && "translate-x-box translate-y-box shadow-none hover:translate-x-box hover:translate-y-box hover:shadow-none",
        className,
      )}
      {...props}
    />
  ),
);
Button.displayName = "Button";
