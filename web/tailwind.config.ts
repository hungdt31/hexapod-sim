import type { Config } from "tailwindcss";

// Design token NeoBrutalism (xem mục 5A của đặc tả)
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  darkMode: "media",
  theme: {
    extend: {
      colors: {
        ink: "#000000",
        bg: "#FFF8E7",
        main: "#FFD23F",
        accent: "#3BCEAC",
        danger: "#FF6B6B",
        teal: { deep: "#1B8A73" },
      },
      borderWidth: { 3: "3px" },
      borderRadius: { base: "4px" },
      boxShadow: {
        brutal: "4px 4px 0 0 #000",
        "brutal-sm": "2px 2px 0 0 #000",
        "brutal-hover": "5px 5px 0 0 #000",
      },
      translate: { box: "4px" },
      fontFamily: {
        sans: ['"Space Grotesk"', "system-ui", "sans-serif"],
        mono: ['"JetBrains Mono"', "ui-monospace", "monospace"],
      },
    },
  },
  plugins: [],
} satisfies Config;
