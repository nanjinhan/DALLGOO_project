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
}

export const userApi = {
  me: () => client.get('/users/me'),
  updateMe: (data) => client.patch('/users/me', data),
  changePassword: (data) => client.patch('/users/me/password', data),
  deleteMe: (password) => client.delete('/users/me', { data: { password } }),
}
