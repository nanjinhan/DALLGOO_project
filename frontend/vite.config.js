import { fileURLToPath, URL } from 'node:url'

import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

// 이 설정은 로컬 `npm run dev`에서만 쓰인다.
// 배포 환경은 frontend 컨테이너의 nginx가 http://backend:8000 으로 프록시하므로 무관.
export default defineConfig(({ mode }) => {
  // 프로젝트 루트 .env의 BACKEND_PORT를 읽는다(없으면 8000).
  // 로컬에서 8000이 다른 프로젝트와 겹칠 때만 .env에 지정하면 된다.
  const rootDir = fileURLToPath(new URL('..', import.meta.url))
  const env = loadEnv(mode, rootDir, '')
  const backendPort = env.BACKEND_PORT || '8000'

  return {
    plugins: [vue()],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
      },
    },
    server: {
      host: true, // 0.0.0.0 바인딩 → 같은 와이파이의 다른 기기에서 접속 가능
      port: 5173,
      proxy: {
        // /api → 백엔드 컨테이너(호스트 ${BACKEND_PORT} → 컨테이너 8000)
        '/api': {
          target: `http://localhost:${backendPort}`,
          changeOrigin: true,
        },
      },
    },
  }
})
