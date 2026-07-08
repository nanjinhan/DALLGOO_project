import { createRouter, createWebHistory } from 'vue-router'

import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/',
    name: 'home',
    component: () => import('@/views/CompanyView.vue'),
    meta: { bare: true }, // 전체화면 랜딩(공통 nav/footer는 유지, container만 없음)
  },
  {
    path: '/board',
    name: 'posts',
    component: () => import('@/views/PostListView.vue'),
  },
  {
    path: '/transport',
    name: 'transport',
    component: () => import('@/views/TransportListView.vue'),
  },
  {
    path: '/transport/new',
    name: 'transport-create',
    component: () => import('@/views/TransportCreateView.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
  },
  {
    path: '/transport/:id',
    name: 'transport-detail',
    component: () => import('@/views/TransportDetailView.vue'),
    props: true,
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/LoginView.vue'),
    meta: { guestOnly: true },
  },
  {
    path: '/signup',
    name: 'signup',
    component: () => import('@/views/SignupView.vue'),
    meta: { guestOnly: true },
  },
  {
    path: '/password-reset',
    name: 'password-reset',
    component: () => import('@/views/PasswordResetView.vue'),
    meta: { guestOnly: true },
  },
  {
    path: '/find-id',
    name: 'find-id',
    component: () => import('@/views/FindIdView.vue'),
    meta: { guestOnly: true },
  },
  {
    path: '/mypage',
    name: 'mypage',
    component: () => import('@/views/MyPageView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/posts/new',
    name: 'post-create',
    component: () => import('@/views/PostCreateView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/posts/:id',
    name: 'post-detail',
    component: () => import('@/views/PostDetailView.vue'),
    props: true,
  },
  {
    path: '/posts/:id/edit',
    name: 'post-edit',
    component: () => import('@/views/PostEditView.vue'),
    props: true,
    meta: { requiresAuth: true },
  },
  {
    path: '/admin',
    name: 'admin',
    component: () => import('@/views/AdminView.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: { name: 'home' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    // 사이트 안에서 메뉴 클릭 시에만 해시 섹션으로 스크롤.
    // 새로고침·직접진입(from.name 없음)에서는 해시를 무시하고 최상단으로.
    if (to.hash && from.name) {
      return { el: to.hash, behavior: 'smooth' }
    }
    if (savedPosition) return savedPosition
    return { top: 0 }
  },
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  // 최초 진입 시 세션 복원 1회
  if (!auth.ready) {
    await auth.restore()
  }
  if (to.meta.requiresAuth && !auth.isLoggedIn) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  if (to.meta.requiresAdmin && !auth.isAdmin) {
    return { name: 'home' }
  }
  if (to.meta.guestOnly && auth.isLoggedIn) {
    return { name: 'home' }
  }
  return true
})

export default router
