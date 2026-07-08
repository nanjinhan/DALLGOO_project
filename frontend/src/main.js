import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import './assets/main.css'
import './assets/company.css'

// 새로고침 시 브라우저가 이전 스크롤 위치를 자동 복원하지 않도록(수동 제어)
if ('scrollRestoration' in history) {
  history.scrollRestoration = 'manual'
}

const app = createApp(App)
app.use(createPinia())
app.use(router)

// 최초 진입(새로고침·직접 URL)에 해시가 남아 있으면 제거하고 최상단으로 이동
router.isReady().then(() => {
  if (window.location.hash) {
    history.replaceState(null, '', window.location.pathname + window.location.search)
  }
  window.scrollTo(0, 0)
})

app.mount('#app')
