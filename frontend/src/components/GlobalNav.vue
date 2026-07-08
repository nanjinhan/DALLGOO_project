<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'

import NotificationBell from '@/components/NotificationBell.vue'
import { useAuthStore } from '@/stores/auth'
import { useTheme } from '@/composables/useTheme'

const auth = useAuthStore()
const router = useRouter()
const { theme, toggle: toggleTheme } = useTheme()

// 대표 전화 (실제 번호로 교체 가능)
const TEL = '062-236-1191'

// 메가 메뉴 구조 — 하위 항목은 랜딩 섹션으로 스크롤 이동
const menu = [
  {
    label: '회사 소개',
    hash: '#company',
    children: [
      { label: '회사 개요', hash: '#company' },
      { label: '미션 · 비전', hash: '#mission' },
      { label: '사회공헌', hash: '#csr' },
      { label: '오시는 길', hash: '#location' },
    ],
  },
  {
    label: '서비스',
    hash: '#service',
    children: [
      { label: '구급차 호출 · 배차', hash: '#service' },
      { label: '실시간 모니터링', hash: '#monitoring' },
      { label: 'AI 의료기록', hash: '#ai-record' },
      { label: '세 개의 축', hash: '#pillars' },
    ],
  },
  {
    label: '연구 · 데이터',
    hash: '#data',
    children: [
      { label: '데이터 플랫폼', hash: '#data' },
      { label: 'Vision AI', hash: '#ai-record' },
    ],
  },
  { label: '이송기록', route: 'transport', children: [] },
  { label: '게시판', route: 'posts', children: [] },
  { label: '문의', hash: '#partner', children: [] },
]

const openIdx = ref(-1)
let closeTimer = null
function openMenu(i) {
  clearTimeout(closeTimer)
  openIdx.value = i
}
function closeMenu() {
  closeTimer = setTimeout(() => (openIdx.value = -1), 120)
}

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

      <!-- 메가 메뉴 -->
      <nav class="gnav-menu">
        <div
          v-for="(m, i) in menu"
          :key="m.label"
          class="menu-item"
          @mouseenter="openMenu(i)"
          @mouseleave="closeMenu"
        >
          <RouterLink
            v-if="m.route"
            :to="{ name: m.route }"
            class="menu-top"
          >
            {{ m.label }}
          </RouterLink>
          <RouterLink
            v-else
            :to="{ name: 'home', hash: m.hash }"
            class="menu-top"
          >
            {{ m.label }}
          </RouterLink>

          <!-- 드롭다운 -->
          <div
            v-if="m.children.length && openIdx === i"
            class="dropdown"
          >
            <RouterLink
              v-for="c in m.children"
              :key="c.label"
              :to="{ name: 'home', hash: c.hash }"
              class="drop-link"
              @click="openIdx = -1"
            >
              {{ c.label }}
            </RouterLink>
          </div>
        </div>
      </nav>

      <div class="gnav-right">
        <a :href="`tel:${TEL}`" class="tel-btn">
          <span class="tel-ic">📞</span>{{ TEL }}
        </a>
        <button
          class="theme-btn"
          :title="theme === 'dark' ? '라이트 모드' : '다크 모드'"
          @click="toggleTheme"
        >
          {{ theme === 'dark' ? '☀️' : '🌙' }}
        </button>
        <template v-if="auth.isLoggedIn">
          <NotificationBell />
          <RouterLink v-if="auth.isAdmin" :to="{ name: 'admin' }" class="gn-link">
            관리자
          </RouterLink>
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
  max-width: 1180px;
  margin: 0 auto;
  height: 58px;
  padding: 0 22px;
  display: flex;
  align-items: center;
  gap: 14px;
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

/* 메가 메뉴 */
.gnav-menu {
  display: flex;
  margin-left: 12px;
  height: 100%;
}
.menu-item {
  position: relative;
  display: flex;
  align-items: center;
  height: 100%;
}
.menu-top {
  display: flex;
  align-items: center;
  height: 100%;
  padding: 0 15px;
  font-size: 15px;
  font-weight: 500;
  color: var(--muted);
  transition: color 0.15s;
  white-space: nowrap;
}
.menu-item:hover .menu-top,
.menu-top.router-link-active {
  color: var(--text);
}
.dropdown {
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  min-width: 176px;
  padding: 8px;
  background: var(--card);
  border: 1px solid var(--border-soft);
  border-radius: 14px;
  box-shadow: 0 14px 34px -12px rgba(0, 0, 0, 0.22);
  display: flex;
  flex-direction: column;
  gap: 2px;
  animation: drop-in 0.16s ease;
}
@keyframes drop-in {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(6px);
  }
}
.drop-link {
  padding: 10px 14px;
  border-radius: 9px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text);
  white-space: nowrap;
  transition: 0.13s;
}
.drop-link:hover {
  background: var(--hover);
  color: var(--primary);
}

.gnav-right {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 13px;
}
.tel-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 15px;
  border-radius: 980px;
  background: var(--primary);
  color: #fff;
  font-size: 14px;
  font-weight: 700;
  transition: 0.2s;
}
.tel-btn:hover {
  background: var(--primary-dark);
  transform: translateY(-1px);
}
.tel-ic {
  font-size: 12px;
}
.theme-btn {
  border: none;
  background: none;
  font-size: 18px;
  line-height: 1;
  padding: 4px;
  border-radius: 8px;
  transition: transform 0.15s;
}
.theme-btn:hover {
  transform: scale(1.15);
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
  white-space: nowrap;
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
  white-space: nowrap;
}
.gn-btn:hover {
  background: var(--primary-dark);
  transform: translateY(-1px);
}

/* 좁은 화면: 메가 메뉴와 전화번호는 숨김(모바일 단순화) */
@media (max-width: 1000px) {
  .gnav-menu {
    display: none;
  }
  .tel-btn {
    display: none;
  }
}
</style>
