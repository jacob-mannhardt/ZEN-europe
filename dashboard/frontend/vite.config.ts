import { svelte } from "@sveltejs/vite-plugin-svelte";
import { defineConfig } from "vite";

// in development, the API runs on the Python backend (python -m zen_dashboard)
export default defineConfig({
  plugins: [svelte()],
  server: {
    port: 5173,
    proxy: { "/api": "http://127.0.0.1:8000" },
  },
  build: { chunkSizeWarningLimit: 5000 },
});
