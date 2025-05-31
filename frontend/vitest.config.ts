// import { defineConfig } from 'vitest/config'
// import react from '@vitejs/plugin-react'

// export default defineConfig({
//   plugins: [react()],
//   test: {
//     globals: true,
//     environment: 'jsdom',
//     setupFiles: ['./src/test/setup.ts'],
//     include: ['./src/test/**/*.{test,spec}.{ts,tsx}'],
//     coverage: {
//       reporter: ['text', 'json', 'html'],
//     },
//     testTimeout: 15000, // 增加默認測試超時時間到 15 秒
//   },
// })
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom', // ✅ jsdom 是正確的 test environment
    setupFiles: ['./src/test/setup.ts'],
    include: ['./src/test/**/*.{test,spec}.{ts,tsx}'],
    coverage: {
      provider: 'istanbul', // ✅ 明確指定使用 istanbul，而非 v8
      reporter: ['text', 'json', 'html'],
    },
    testTimeout: 15000,
  },
})