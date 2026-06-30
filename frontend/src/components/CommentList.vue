<script setup>
import { onMounted, ref } from 'vue'

import CommentItem from './CommentItem.vue'
import { commentApi } from '@/api/comment'
import { useAuthStore } from '@/stores/auth'
import { errorMessage } from '@/utils/format'

const props = defineProps({
  postId: { type: [Number, String], required: true },
})

const auth = useAuthStore()
const comments = ref([])
const loading = ref(false)
const newText = ref('')
const busy = ref(false)
const error = ref('')

async function load() {
  loading.value = true
  try {
    const { data } = await commentApi.list(props.postId)
    // 봉투 해제 후 data = { items: [...] }
    comments.value = data.items ?? []
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    loading.value = false
  }
}

async function submit() {
  if (!newText.value.trim()) return
  busy.value = true
  error.value = ''
  try {
    await commentApi.create(props.postId, {
      content: newText.value.trim(),
      parent_id: null,
    })
    newText.value = ''
    await load()
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    busy.value = false
  }
}

onMounted(load)
</script>

<template>
  <section class="comments card">
    <h3 class="heading">댓글</h3>

    <div v-if="auth.isLoggedIn" class="new-comment">
      <textarea
        v-model="newText"
        class="textarea short"
        placeholder="댓글을 입력하세요"
      />
      <div class="row">
        <span class="spacer" />
        <button class="btn btn-primary" :disabled="busy" @click="submit">
          댓글 등록
        </button>
      </div>
    </div>
    <p v-else class="muted login-hint">댓글을 작성하려면 로그인하세요.</p>
    <p v-if="error" class="error-text">{{ error }}</p>

    <div v-if="loading" class="muted">불러오는 중…</div>
    <div v-else-if="!comments.length" class="muted empty">첫 댓글을 남겨보세요.</div>
    <div v-else>
      <CommentItem
        v-for="c in comments"
        :key="c.id"
        :comment="c"
        :post-id="postId"
        :depth="0"
        @changed="load"
      />
    </div>
  </section>
</template>

<style scoped>
.comments {
  margin-top: 20px;
}
.heading {
  margin: 0 0 16px;
  font-size: 16px;
}
.new-comment {
  margin-bottom: 16px;
}
.textarea.short {
  min-height: 80px;
  margin-bottom: 8px;
}
.login-hint,
.empty {
  padding: 12px 0;
}
</style>
