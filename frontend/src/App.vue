<script setup>
import { computed, onMounted, onUnmounted } from 'vue'
import { RouterView, useRoute, useRouter } from 'vue-router'

import GlobalFooter from '@/components/GlobalFooter.vue'
import GlobalNav from '@/components/GlobalNav.vue'
import ToastContainer from '@/components/ToastContainer.vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

// bare 라우트(랜딩)는 전체화면(컨테이너 없음). 그 외는 .container로 감싼다.
const bare = computed(() => route.meta.bare === true)

// refresh 실패(만료) 시 인터셉터가 쏘는 강제 로그아웃 이벤트 처리
function handleForcedLogout() {
  auth.forceLogout()
  router.push({ name: 'login' })
}
onMounted(() => {
  window.addEventListener('auth:logout', handleForcedLogout)
  // 최초 로드 시 항상 최상단(해시/스크롤 복원 튐 방지 보강)
  requestAnimationFrame(() => window.scrollTo(0, 0))
})
onUnmounted(() => window.removeEventListener('auth:logout', handleForcedLogout))
</script>

<template>
  <GlobalNav />

  <RouterView v-if="bare" />
  <main v-else class="container app-main">
    <RouterView />
  </main>

  <GlobalFooter />
  <ToastContainer />
</template>

<style scoped>
.app-main {
  min-height: 60vh;
}
</style>
