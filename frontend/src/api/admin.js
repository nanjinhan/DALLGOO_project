import client from './client'

export const adminApi = {
  users: () => client.get('/admin/users'),
  setActive: (id, active) =>
    client.patch(`/admin/users/${id}/active`, null, { params: { active } }),
  deletePost: (id) => client.delete(`/admin/posts/${id}`),
  deleteComment: (id) => client.delete(`/admin/comments/${id}`),
}

export const notificationApi = {
  list: () => client.get('/notifications'),
  unreadCount: () => client.get('/notifications/unread-count'),
  read: (id) => client.patch(`/notifications/${id}/read`),
  readAll: () => client.patch('/notifications/read-all'),
}
