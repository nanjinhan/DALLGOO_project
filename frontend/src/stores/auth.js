import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

import { authApi, userApi } from '@/api/auth'
import {
  clearTokens,
  getRefreshToken,
  setAccessToken,
  setRefreshToken,
} from '@/api/client'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const ready = ref(false) // 초기 복원 완료 여부

  const isLoggedIn = computed(() => user.value !== null)
  const isAdmin = computed(() => user.value?.is_admin === true)

  async function login(username, password) {
    const { data } = await authApi.login({ username, password })
    setAccessToken(data.access_token)
    setRefreshToken(data.refresh_token)
    await fetchMe()
  }

  async function fetchMe() {
    const { data } = await userApi.me()
    user.value = data
    return data
  }

  async function logout() {
    const refresh = getRefreshToken()
    try {
      if (refresh) await authApi.logout(refresh)
    } catch {
      // 무시 — 어차피 토큰 폐기
    }
    clearTokens()
    user.value = null
  }

  // 새로고침 시 refresh 토큰으로 세션 복원
  async function restore() {
    const refresh = getRefreshToken()
    if (!refresh) {
      ready.value = true
      return
    }
    try {
      // access는 메모리라 새로고침 시 없음 → 인터셉터가 refresh로 자동 복원
      await fetchMe()
    } catch {
      clearTokens()
      user.value = null
    } finally {
      ready.value = true
    }
  }

  function forceLogout() {
    clearTokens()
    user.value = null
  }

  return {
    user,
    ready,
    isLoggedIn,
    isAdmin,
    login,
    logout,
    fetchMe,
    restore,
    forceLogout,
  }
})
