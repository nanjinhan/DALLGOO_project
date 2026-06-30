<script setup>
import { ref } from 'vue'
import { RouterLink } from 'vue-router'

import { authApi } from '@/api/auth'
import { errorMessage } from '@/utils/format'

const email = ref('')
const busy = ref(false)
const done = ref(false)
const error = ref('')

async function submit() {
  error.value = ''
  busy.value = true
  try {
    await authApi.findUsername(email.value.trim())
    done.value = true
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <div class="auth-wrap card">
    <h2>아이디 찾기</h2>

    <template v-if="!done">
      <p class="muted" style="margin-bottom: 14px">
        가입할 때 사용한 이메일을 입력하면, 그 이메일로 아이디를 보내드립니다.
      </p>
      <form @submit.prevent="submit">
        <div class="field">
          <label>가입한 이메일</label>
          <input v-model="email" type="email" class="input" />
        </div>
        <p v-if="error" class="error-text">{{ error }}</p>
        <button class="btn btn-primary full" :disabled="busy">아이디 찾기</button>
      </form>
    </template>

    <p v-else class="success-text" style="margin: 16px 0">
      가입된 이메일이라면 아이디를 보냈습니다. 메일함을 확인해주세요.
    </p>

    <div class="links">
      <RouterLink :to="{ name: 'login' }">로그인</RouterLink>
      <RouterLink :to="{ name: 'password-reset' }">비밀번호 찾기</RouterLink>
    </div>
  </div>
</template>

<style scoped>
.auth-wrap {
  max-width: 420px;
  margin: 40px auto;
}
h2 {
  margin: 0 0 16px;
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
}
.links a {
  color: var(--primary);
  font-weight: 600;
}
</style>
