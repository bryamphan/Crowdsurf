// Vite config: how the dev server and production build behave.
//
// The important part is the proxy. Any request the frontend makes to /api/...
// (including WebSocket connections) is forwarded to the FastAPI backend, so
// frontend code never needs to know the backend's address and we avoid CORS
// errors in development. You rarely need to touch this file.

import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// In Docker the API is at http://api:8000 (set in docker-compose.yml); locally it's localhost.
const apiTarget = process.env.API_PROXY_TARGET ?? "http://localhost:8000";

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
    proxy: {
      "/api": { target: apiTarget, changeOrigin: true, ws: true },
    },
  },
});
