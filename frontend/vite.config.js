import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// In local dev, the Flask API runs on the host at localhost:5000.
// In Docker Compose, "localhost" inside the frontend container refers to
// the frontend container itself -- it must instead reach the backend by
// its service name. Set VITE_API_TARGET=http://backend:5000 in that case.
const apiTarget = process.env.VITE_API_TARGET || "http://localhost:5000";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true, // listen on 0.0.0.0 so the dev server is reachable from outside the container
    proxy: {
      "/api": {
        target: apiTarget,
        changeOrigin: true,
      },
      "/uploads": {
        target: apiTarget,
        changeOrigin: true,
      },
    },
  },
});

