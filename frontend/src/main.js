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

// 최초 진입(새로고침·직접 URL)에 남아 있는 해시를 '마운트 전에' 제거한다.
// 라우터가 초기 이동을 시작하기 전이자 #intro-video 같은 요소가 DOM에 생기기 전이라,
// 브라우저가 앵커 스크롤을 예약할 대상 자체가 사라진다.
//   ※ 예전엔 router.isReady() 안에서 지웠는데, 그 시점엔 지연 로딩된 섹션이 이미
//     DOM에 붙은 뒤라 브라우저가 해당 섹션으로 스크롤한 다음에 해시가 지워졌다.
if (window.location.hash) {
  history.replaceState(null, '', window.location.pathname + window.location.search)
}

const app = createApp(App)
app.use(createPinia())
app.use(router)

// 늦게 로드되는 이미지·영상 때문에 레이아웃이 밀릴 수 있어 한 번 더 최상단 고정
router.isReady().then(() => {
  window.scrollTo(0, 0)
})

app.mount('#app')
