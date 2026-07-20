import client from './client'

export const settingsApi = {
  // 공개 조회 — 비로그인 랜딩페이지에서도 호출
  get: () => client.get('/settings'),
  // 관리자만
  update: (payload) => client.patch('/settings', payload),
}
