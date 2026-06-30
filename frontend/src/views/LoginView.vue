<script setup>
import { ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'

import { useAuthStore } from '@/stores/auth'
import { errorMessage } from '@/utils/format'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const username = ref('')
const password = ref('')
const busy = ref(false)
const error = ref('')

async function submit() {
  busy.value = true
  error.value = ''
  try {
    await auth.login(username.value, password.value)
    const redirect = route.query.redirect || { name: 'posts' }
    router.push(redirect)
  } catch (e) {
    error.value = errorMessage(e, '로그인에 실패했습니다.')
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <div class="auth-wrap card">
    <h2>로그인</h2>
    <form @submit.prevent="submit">
      <div class="field">
        <label>아이디</label>
        <input v-model="username" class="input" autocomplete="username" />
      </div>
      <div class="field">
        <label>비밀번호</label>
        <input
          v-model="password"
          type="password"
          class="input"
          autocomplete="current-password"
        />
      </div>
      <p v-if="error" class="error-text">{{ error }}</p>
      <button class="btn btn-primary full" :disabled="busy">로그인</button>
    </form>
    <div class="links">
      <RouterLink :to="{ name: 'signup' }">회원가입</RouterLink>
      <RouterLink :to="{ name: 'password-reset' }">비밀번호 찾기</RouterLink>
    </div>
  </div>
</template>

<style scoped>
.auth-wrap {
  max-width: 400px;
  margin: 40px auto;
}
h2 {
  margin: 0 0 20px;
}
.full {
  width: 100%;
  margin-top: 8px;
}
.links {
  display: flex;
  justify-content: space-between;
  margin-top: 16px;
  font-size: 14px;
  color: var(--muted);
}
.links a:hover {
  color: var(--primary);
}
</style>
