import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  optimizeDeps: {
    include: ["datatables.net-dt"],
  },
  server: {
    port: 5173,
    setupMiddlewares(middlewares, devServer) {
      middlewares.use('/health', (req, res, next) => {
        res.setHeader('Content-Type', 'application/json');
        res.end(JSON.stringify({ status: 'ok' }));
      });
      return middlewares;
    }
  },
})
