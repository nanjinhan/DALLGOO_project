import axios from 'axios'

const client = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

// --- 토큰 저장소 (메모리 access + localStorage refresh) ---
let accessToken = null
const REFRESH_KEY = 'dallgoo_refresh'

export function setAccessToken(token) {
  accessToken = token
}
export function getAccessToken() {
  return accessToken
}
export function setRefreshToken(token) {
  if (token) localStorage.setItem(REFRESH_KEY, token)
}
export function getRefreshToken() {
  return localStorage.getItem(REFRESH_KEY)
}
export function clearTokens() {
  accessToken = null
  localStorage.removeItem(REFRESH_KEY)
}

// --- 요청 인터셉터: access token 주입 ---
client.interceptors.request.use((config) => {
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`
  }
  return config
})

// --- 응답 인터셉터: 401 → refresh 자동 재발급 후 재시도 ---
let refreshing = null

client.interceptors.response.use(
  (res) => {
    // 공통 응답 봉투({success, code, message, data}) 해제 → data만 남긴다.
    const body = res.data
    if (body && typeof body === 'object' && 'success' in body && 'data' in body) {
      res.data = body.data
    }
    return res
  },
  async (error) => {
    const { response, config } = error
    if (!response || response.status !== 401 || config._retry) {
      return Promise.reject(error)
    }
    // refresh 자체 호출이 401이면 바로 실패
    if (config.url?.includes('/auth/refresh')) {
      clearTokens()
      return Promise.reject(error)
    }

    const refreshToken = getRefreshToken()
    if (!refreshToken) {
      clearTokens()
      return Promise.reject(error)
    }

    try {
      // 동시 401 다발 시 refresh는 한 번만
      if (!refreshing) {
        refreshing = client
          .post('/auth/refresh', { refresh_token: refreshToken })
          .then((r) => {
            setAccessToken(r.data.access_token)
            setRefreshToken(r.data.refresh_token)
            return r.data.access_token
          })
          .finally(() => {
            refreshing = null
          })
      }
      const newToken = await refreshing
      config._retry = true
      config.headers.Authorization = `Bearer ${newToken}`
      return client(config)
    } catch (e) {
      clearTokens()
      // 무한 루프 방지: refresh 실패 시 로그인으로
      if (typeof window !== 'undefined') {
        window.dispatchEvent(new CustomEvent('auth:logout'))
      }
      return Promise.reject(e)
    }
  },
)

export default client
