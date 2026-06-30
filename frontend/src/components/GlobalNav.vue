<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'

import NotificationBell from '@/components/NotificationBell.vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

const scrolled = ref(false)
const onScroll = () => (scrolled.value = window.scrollY > 8)
onMounted(() => {
  onScroll()
  window.addEventListener('scroll', onScroll, { passive: true })
})
onUnmounted(() => window.removeEventListener('scroll', onScroll))

async function onLogout() {
  await auth.logout()
  router.push({ name: 'home' })
}
</script>

<template>
  <header class="gnav" :class="{ solid: scrolled }">
    <div class="gnav-inner">
      <RouterLink :to="{ name: 'home' }" class="gnav-brand">
        <span class="gnav-mark">🚑</span>
        <span>달구</span>
      </RouterLink>

      <nav class="gnav-menu">
        <RouterLink :to="{ name: 'home', hash: '#service' }">서비스</RouterLink>
        <RouterLink :to="{ name: 'home', hash: '#company' }">회사소개</RouterLink>
        <RouterLink :to="{ name: 'home', hash: '#data' }">연구·데이터</RouterLink>
        <RouterLink :to="{ name: 'posts' }">게시판</RouterLink>
        <RouterLink v-if="auth.isAdmin" :to="{ name: 'admin' }">관리자</RouterLink>
      </nav>

      <div class="gnav-right">
        <template v-if="auth.isLoggedIn">
          <NotificationBell />
          <RouterLink :to="{ name: 'post-create' }" class="gn-btn">글쓰기</RouterLink>
          <RouterLink :to="{ name: 'mypage' }" class="gn-link">
            {{ auth.user?.nickname || '마이페이지' }}
          </RouterLink>
          <button class="gn-link" @click="onLogout">로그아웃</button>
        </template>
        <template v-else>
          <RouterLink :to="{ name: 'login' }" class="gn-link">로그인</RouterLink>
          <RouterLink :to="{ name: 'signup' }" class="gn-btn">회원가입</RouterLink>
        </template>
      </div>
    </div>
  </header>
</template>

<style scoped>
.gnav {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(255, 255, 255, 0.72);
  backdrop-filter: saturate(180%) blur(20px);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
  border-bottom: 1px solid transparent;
  transition: border-color 0.25s;
}
.gnav.solid {
  border-bottom-color: var(--border);
}
.gnav-inner {
  max-width: 1120px;
  margin: 0 auto;
  height: 56px;
  padding: 0 22px;
  display: flex;
  align-items: center;
  gap: 18px;
}
.gnav-brand {
  display: flex;
  align-items: center;
  gap: 7px;
  font-weight: 800;
  font-size: 20px;
  letter-spacing: -0.02em;
  color: var(--text);
}
.gnav-mark {
  font-size: 18px;
}
.gnav-menu {
  display: flex;
  gap: 26px;
  margin-left: 14px;
}
.gnav-menu a {
  font-size: 15px;
  font-weight: 500;
  color: var(--muted);
  transition: 0.15s;
}
.gnav-menu a:hover,
.gnav-menu a.router-link-active {
  color: var(--text);
}
.gnav-right {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 16px;
}
.gn-link {
  border: none;
  background: none;
  font-size: 15px;
  font-weight: 500;
  color: var(--text);
  cursor: pointer;
  padding: 0;
  font-family: inherit;
}
.gn-link:hover {
  color: var(--primary);
}
.gn-btn {
  padding: 8px 16px;
  border-radius: 980px;
  background: var(--primary);
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  transition: 0.2s;
}
.gn-btn:hover {
  background: var(--primary-dark);
  transform: translateY(-1px);
}

@media (max-width: 760px) {
  .gnav-menu {
    display: none;
  }
}
</style>
