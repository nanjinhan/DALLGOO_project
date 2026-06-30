<script setup>
import { onMounted, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'

import CommentList from '@/components/CommentList.vue'
import LikeButton from '@/components/LikeButton.vue'
import { adminApi } from '@/api/admin'
import { fileApi, postApi } from '@/api/post'
import { useAuthStore } from '@/stores/auth'
import { errorMessage, formatDate, formatSize } from '@/utils/format'

const props = defineProps({
  id: { type: [Number, String], required: true },
})

const auth = useAuthStore()
const router = useRouter()

const post = ref(null)
const loading = ref(true)
const error = ref('')
const likeBusy = ref(false)

const isOwner = () => auth.isLoggedIn && post.value?.author?.id === auth.user?.id

async function load() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await postApi.detail(props.id)
    post.value = data
  } catch (e) {
    error.value = errorMessage(e, '게시글을 불러올 수 없습니다.')
  } finally {
    loading.value = false
  }
}

async function toggleLike() {
  if (!auth.isLoggedIn) {
    router.push({ name: 'login', query: { redirect: `/posts/${props.id}` } })
    return
  }
  likeBusy.value = true
  try {
    if (post.value.liked_by_me) {
      await postApi.unlike(props.id)
      post.value.liked_by_me = false
      post.value.like_count -= 1
    } else {
      await postApi.like(props.id)
      post.value.liked_by_me = true
      post.value.like_count += 1
    }
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    likeBusy.value = false
  }
}

async function remove() {
  if (!confirm('게시글을 삭제할까요? 첨부파일도 함께 삭제됩니다.')) return
  try {
    await postApi.remove(props.id)
    router.push({ name: 'posts' })
  } catch (e) {
    error.value = errorMessage(e)
  }
}

async function adminRemove() {
  if (!confirm('[관리자] 이 게시글을 강제 삭제할까요?')) return
  try {
    await adminApi.deletePost(props.id)
    router.push({ name: 'posts' })
  } catch (e) {
    error.value = errorMessage(e)
  }
}

onMounted(load)
</script>

<template>
  <div class="detail-view">
    <div v-if="loading" class="muted center">불러오는 중…</div>
    <p v-else-if="error && !post" class="error-text center">{{ error }}</p>

    <template v-else-if="post">
      <article class="card">
        <h1 class="title">{{ post.title }}</h1>
        <div class="meta">
          <span class="author">{{ post.author?.nickname }}</span>
          <span class="dot">·</span>
          <span>{{ formatDate(post.created_at) }}</span>
          <span class="dot">·</span>
          <span>조회 {{ post.view_count }}</span>
          <span class="spacer" />
          <template v-if="isOwner()">
            <RouterLink
              :to="{ name: 'post-edit', params: { id: post.id } }"
              class="btn small"
            >
              수정
            </RouterLink>
            <button class="btn btn-danger small" @click="remove">삭제</button>
          </template>
          <button
            v-else-if="auth.isAdmin"
            class="btn btn-danger small"
            @click="adminRemove"
          >
            관리자 삭제
          </button>
        </div>

        <div class="content">{{ post.content }}</div>

        <div v-if="post.files?.length" class="files">
          <div class="files-title">첨부파일</div>
          <ul>
            <li v-for="f in post.files" :key="f.id">
              <a :href="fileApi.downloadUrl(f.id)" target="_blank" rel="noopener">
                📎 {{ f.original_name }}
              </a>
              <span class="muted">{{ formatSize(f.file_size) }}</span>
            </li>
          </ul>
        </div>

        <div class="like-row">
          <LikeButton
            :liked="post.liked_by_me"
            :count="post.like_count"
            :disabled="likeBusy"
            @toggle="toggleLike"
          />
        </div>
        <p v-if="error" class="error-text">{{ error }}</p>
      </article>

      <CommentList :post-id="post.id" />

      <div class="back">
        <RouterLink :to="{ name: 'posts' }" class="btn">← 목록으로</RouterLink>
      </div>
    </template>
  </div>
</template>

<style scoped>
.title {
  font-size: 24px;
  margin: 0 0 12px;
}
.meta {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--muted);
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border);
}
.author {
  font-weight: 700;
  color: #495057;
}
.small {
  padding: 5px 10px;
  font-size: 13px;
}
.content {
  padding: 20px 0;
  font-size: 15px;
  line-height: 1.7;
  white-space: pre-wrap;
  min-height: 80px;
}
.files {
  padding: 14px;
  background: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 16px;
}
.files-title {
  font-size: 13px;
  font-weight: 700;
  margin-bottom: 8px;
}
.files ul {
  list-style: none;
  margin: 0;
  padding: 0;
}
.files li {
  display: flex;
  gap: 10px;
  align-items: center;
  padding: 4px 0;
  font-size: 14px;
}
.files a {
  color: var(--primary);
  font-weight: 600;
}
.like-row {
  display: flex;
  justify-content: center;
  padding: 8px 0;
}
.center {
  text-align: center;
  padding: 40px 0;
}
.back {
  margin-top: 20px;
}
</style>
