import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Em dev, /api é redirecionado para o backend FastAPI local.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": { target: "http://localhost:8000", ws: true, changeOrigin: true },
    },
  },
});
