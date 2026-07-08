import client from './client'

export const transportApi = {
  list: (params) => client.get('/transport', { params }),
  detail: (id) => client.get(`/transport/${id}`),
  create: (formData) =>
    client.post('/transport', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  remove: (id) => client.delete(`/transport/${id}`),
  imageUrl: (id) => `/api/transport/${id}/image`,
  verify: (id, payload) => client.post(`/transport/${id}/verify`, payload),
  comments: (id) => client.get(`/transport/${id}/comments`),
  addComment: (id, payload) => client.post(`/transport/${id}/comments`, payload),
}
