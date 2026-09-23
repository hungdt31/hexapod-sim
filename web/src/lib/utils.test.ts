import { describe, expect, it } from "vitest";
import { cn, deg, rad } from "./utils";

describe("utils", () => {
  it("chuyển đổi độ/radian", () => {
    expect(deg(Math.PI)).toBeCloseTo(180);
    expect(rad(90)).toBeCloseTo(Math.PI / 2);
  });
  it("gộp class Tailwind, lớp sau thắng", () => {
    expect(cn("bg-white", "bg-main")).toBe("bg-main");
  });
});
