import client from './client'

export const postApi = {
  list: (params) => client.get('/posts', { params }),
  suggest: (keyword) => client.get('/posts/suggest', { params: { keyword } }),
  detail: (id) => client.get(`/posts/${id}`),
  create: (formData) =>
    client.post('/posts', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  update: (id, data) => client.patch(`/posts/${id}`, data),
  remove: (id) => client.delete(`/posts/${id}`),
  like: (id) => client.post(`/posts/${id}/like`),
  unlike: (id) => client.delete(`/posts/${id}/like`),
}

export const fileApi = {
  downloadUrl: (id) => `/api/files/${id}/download`,
  remove: (id) => client.delete(`/files/${id}`),
}
