import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  optimizeDeps: {
    include: ["datatables.net-dt"],
  },
  define: {
    'import.meta.env.VITE_USER_SERVICE_URL': JSON.stringify(import.meta.env.VITE_USER_SERVICE_URL),
    'import.meta.env.VITE_ORDER_SERVICE_URL': JSON.stringify(import.meta.env.VITE_ORDER_SERVICE_URL),
    'import.meta.env.VITE_ADMIN_SERVICE_URL': JSON.stringify(import.meta.env.VITE_ADMIN_SERVICE_URL),
  },
  server: {
    port: 5173,
    host: true,
    allowedHosts: ['meal-provider.example.com'],
    setupMiddlewares(middlewares, devServer) {
      devServer.app.use('/health', (req, res) => {
        res.setHeader('Content-Type', 'application/json');
        res.end(JSON.stringify({ status: 'ok' }));
      });
      return middlewares;
    }
  },
})
