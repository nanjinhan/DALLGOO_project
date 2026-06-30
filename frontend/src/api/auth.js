import client from './client'

export const authApi = {
  signup: (data) => client.post('/auth/signup', data),
  checkUsername: (username) =>
    client.get('/auth/check-username', { params: { username } }),
  checkEmail: (email) => client.get('/auth/check-email', { params: { email } }),
  checkNickname: (nickname) =>
    client.get('/auth/check-nickname', { params: { nickname } }),
  login: (data) => client.post('/auth/login', data),
  logout: (refresh_token) => client.post('/auth/logout', { refresh_token }),
  forgotPassword: (email) => client.post('/auth/password/forgot', { email }),
  resetPassword: (data) => client.post('/auth/password/reset', data),
  // 설정(이메일 인증 필요 여부 등)
  config: () => client.get('/auth/config'),
  // 이메일 인증 / 아이디 찾기
  sendEmailCode: (email) => client.post('/auth/email/send-code', { email }),
  verifyEmailCode: (email, code) =>
    client.post('/auth/email/verify', { email, code }),
  findUsername: (email) => client.post('/auth/username/find', { email }),
}

export const userApi = {
  me: () => client.get('/users/me'),
  updateMe: (data) => client.patch('/users/me', data),
  changePassword: (data) => client.patch('/users/me/password', data),
  deleteMe: (password) => client.delete('/users/me', { data: { password } }),
}
