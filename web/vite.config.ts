import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Dev: Vite (5173) chuyển tiếp /ws và /api sang server Python (8000)
export default defineConfig({
  plugins: [react()],
  build: { chunkSizeWarningLimit: 1600 },
  resolve: { alias: { "@": new URL("./src", import.meta.url).pathname } },
  server: {
    port: 5173,
    proxy: {
      "/ws": { target: "ws://127.0.0.1:8000", ws: true },
      "/api": { target: "http://127.0.0.1:8000" },
    },
  },
});
