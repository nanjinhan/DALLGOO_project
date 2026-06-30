<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

import FileUploader from '@/components/FileUploader.vue'
import { postApi } from '@/api/post'
import { errorMessage } from '@/utils/format'

const router = useRouter()

const title = ref('')
const content = ref('')
const files = ref([])
const busy = ref(false)
const error = ref('')

async function submit() {
  error.value = ''
  if (!title.value.trim() || !content.value.trim()) {
    error.value = '제목과 내용을 입력하세요.'
    return
  }
  busy.value = true
  try {
    const fd = new FormData()
    fd.append('title', title.value)
    fd.append('content', content.value)
    files.value.forEach((f) => fd.append('files', f))
    const { data } = await postApi.create(fd)
    router.push({ name: 'post-detail', params: { id: data.id } })
  } catch (e) {
    error.value = errorMessage(e, '글 작성에 실패했습니다.')
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <div class="card">
    <h2>글쓰기</h2>
    <div class="field">
      <label>제목</label>
      <input v-model="title" class="input" placeholder="제목을 입력하세요" />
    </div>
    <div class="field">
      <label>내용</label>
      <textarea v-model="content" class="textarea" placeholder="내용을 입력하세요" />
    </div>
    <div class="field">
      <label>첨부파일</label>
      <FileUploader v-model="files" />
    </div>
    <p v-if="error" class="error-text">{{ error }}</p>
    <div class="row">
      <button class="btn" @click="router.back()">취소</button>
      <span class="spacer" />
      <button class="btn btn-primary" :disabled="busy" @click="submit">등록</button>
    </div>
  </div>
</template>

<style scoped>
h2 {
  margin: 0 0 20px;
}
</style>
