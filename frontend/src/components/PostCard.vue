<script setup>
import { RouterLink } from 'vue-router'
import { formatDate } from '@/utils/format'

defineProps({
  post: { type: Object, required: true },
})
</script>

<template>
  <RouterLink :to="{ name: 'post-detail', params: { id: post.id } }" class="post-card">
    <div class="title">{{ post.title }}</div>
    <div class="meta">
      <span class="author">{{ post.author?.nickname }}</span>
      <span class="dot">·</span>
      <span>{{ formatDate(post.created_at) }}</span>
      <span class="spacer" />
      <span class="stat">👁 {{ post.view_count }}</span>
      <span class="stat">❤ {{ post.like_count }}</span>
      <span class="stat">💬 {{ post.comment_count }}</span>
    </div>
  </RouterLink>
</template>

<style scoped>
.post-card {
  display: block;
  background: #fff;
  border: 1px solid var(--border-soft);
  border-radius: 16px;
  padding: 18px 20px;
  margin-bottom: 10px;
  transition: 0.16s;
}
.post-card:hover {
  border-color: var(--primary);
  box-shadow: 0 4px 16px -4px rgba(0, 113, 227, 0.18);
  transform: translateY(-1px);
}
.title {
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 8px;
}
.meta {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--muted);
}
.author {
  font-weight: 600;
  color: #495057;
}
.stat {
  margin-left: 8px;
}
</style>
