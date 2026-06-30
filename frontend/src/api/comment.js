import client from './client'

export const commentApi = {
  list: (postId) => client.get(`/posts/${postId}/comments`),
  create: (postId, data) => client.post(`/posts/${postId}/comments`, data),
  update: (id, content) => client.patch(`/comments/${id}`, { content }),
  remove: (id) => client.delete(`/comments/${id}`),
  like: (id) => client.post(`/comments/${id}/like`),
  unlike: (id) => client.delete(`/comments/${id}/like`),
}
