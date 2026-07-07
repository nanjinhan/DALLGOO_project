<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { fileApi, postApi } from '@/api/post'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import { errorMessage, formatSize } from '@/utils/format'

const props = defineProps({
  id: { type: [Number, String], required: true },
})

const auth = useAuthStore()
const router = useRouter()
const toast = useToast()

const title = ref('')
const content = ref('')
const isSecret = ref(false)
const existingFiles = ref([])
const loading = ref(true)
const busy = ref(false)
const error = ref('')

async function load() {
  loading.value = true
  try {
    const { data } = await postApi.detail(props.id)
    if (!auth.isLoggedIn || data.author?.id !== auth.user?.id) {
      error.value = '본인 글만 수정할 수 있습니다.'
      return
    }
    title.value = data.title
    content.value = data.content
    isSecret.value = data.is_secret
    existingFiles.value = data.files || []
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    loading.value = false
  }
}

async function removeFile(fileId) {
  if (!confirm('첨부파일을 삭제할까요?')) return
  try {
    await fileApi.remove(fileId)
    existingFiles.value = existingFiles.value.filter((f) => f.id !== fileId)
  } catch (e) {
    error.value = errorMessage(e)
  }
}

async function submit() {
  error.value = ''
  if (!title.value.trim() || !content.value.trim()) {
    error.value = '제목과 내용을 입력하세요.'
    return
  }
  busy.value = true
  try {
    await postApi.update(props.id, {
      title: title.value,
      content: content.value,
      is_secret: isSecret.value,
    })
    toast.success('수정되었습니다.')
    router.push({ name: 'post-detail', params: { id: props.id } })
  } catch (e) {
    error.value = errorMessage(e, '수정에 실패했습니다.')
    toast.error(error.value)
  } finally {
    busy.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="card">
    <h2>글 수정</h2>
    <div v-if="loading" class="muted">불러오는 중…</div>
    <template v-else>
      <div class="field">
        <label>제목</label>
        <input v-model="title" class="input" />
      </div>
      <div class="field">
        <label>내용</label>
        <textarea v-model="content" class="textarea" />
      </div>
      <div v-if="existingFiles.length" class="field">
        <label>첨부파일</label>
        <ul class="file-list">
          <li v-for="f in existingFiles" :key="f.id">
            <span>📎 {{ f.original_name }}</span>
            <span class="muted">{{ formatSize(f.file_size) }}</span>
            <button class="remove" @click="removeFile(f.id)">삭제</button>
          </li>
        </ul>
      </div>
      <div class="field">
        <label class="secret-check">
          <input v-model="isSecret" type="checkbox" />
          <span>🔒 비밀글 (작성자와 관리자만 볼 수 있어요 — 1:1 문의)</span>
        </label>
      </div>
      <p v-if="error" class="error-text">{{ error }}</p>
      <div class="row">
        <button class="btn" @click="router.back()">취소</button>
        <span class="spacer" />
        <button class="btn btn-primary" :disabled="busy" @click="submit">수정 완료</button>
      </div>
    </template>
  </div>
</template>

<style scoped>
h2 {
  margin: 0 0 20px;
}
.file-list {
  list-style: none;
  padding: 0;
  margin: 0;
}
.file-list li {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  border: 1px solid var(--border);
  border-radius: 8px;
  margin-bottom: 6px;
  font-size: 14px;
}
.remove {
  margin-left: auto;
  border: none;
  background: none;
  color: var(--danger);
  font-size: 13px;
  font-weight: 600;
}
.secret-check {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text);
  cursor: pointer;
}
.secret-check input {
  width: 16px;
  height: 16px;
  cursor: pointer;
}
</style>
