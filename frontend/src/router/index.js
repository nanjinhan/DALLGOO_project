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
    path: '/:pathMatch(.*)*',
    redirect: { name: 'home' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    // 해시(#service 등)로 이동 시 해당 섹션으로 부드럽게 스크롤
    if (to.hash) {
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
  if (to.meta.guestOnly && auth.isLoggedIn) {
    return { name: 'home' }
  }
  return true
})

export default router
