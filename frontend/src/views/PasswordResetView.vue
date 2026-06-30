<script setup>
import { ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'

import { authApi } from '@/api/auth'
import { errorMessage } from '@/utils/format'

const router = useRouter()

const step = ref(1) // 1: 이메일 입력, 2: 토큰+새 비번
const email = ref('')
const token = ref('')
const newPassword = ref('')
const newPasswordConfirm = ref('')
const busy = ref(false)
const error = ref('')
const info = ref('')

async function requestToken() {
  busy.value = true
  error.value = ''
  try {
    const { data } = await authApi.forgotPassword(email.value)
    // 학습용: 메일 인프라가 없어 토큰을 응답으로 받아 자동 채움
    if (data.reset_token) {
      token.value = data.reset_token
      info.value = '재설정 토큰이 발급되었습니다. 새 비밀번호를 설정하세요.'
    } else {
      info.value = '가입된 이메일이라면 재설정 안내가 발송됩니다.'
    }
    step.value = 2
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    busy.value = false
  }
}

async function reset() {
  error.value = ''
  if (newPassword.value !== newPasswordConfirm.value) {
    error.value = '비밀번호가 일치하지 않습니다.'
    return
  }
  busy.value = true
  try {
    await authApi.resetPassword({
      token: token.value,
      new_password: newPassword.value,
    })
    alert('비밀번호가 변경되었습니다. 다시 로그인해주세요.')
    router.push({ name: 'login' })
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <div class="auth-wrap card">
    <h2>비밀번호 재설정</h2>

    <form v-if="step === 1" @submit.prevent="requestToken">
      <div class="field">
        <label>가입한 이메일</label>
        <input v-model="email" type="email" class="input" />
      </div>
      <p v-if="error" class="error-text">{{ error }}</p>
      <button class="btn btn-primary full" :disabled="busy">재설정 토큰 받기</button>
    </form>

    <form v-else @submit.prevent="reset">
      <p v-if="info" class="success-text">{{ info }}</p>
      <div class="field">
        <label>재설정 토큰</label>
        <input v-model="token" class="input" />
      </div>
      <div class="field">
        <label>새 비밀번호 (8~64자, 대·소문자·숫자 포함)</label>
        <input v-model="newPassword" type="password" class="input" />
      </div>
      <div class="field">
        <label>새 비밀번호 확인</label>
        <input v-model="newPasswordConfirm" type="password" class="input" />
      </div>
      <p v-if="error" class="error-text">{{ error }}</p>
      <button class="btn btn-primary full" :disabled="busy">비밀번호 변경</button>
    </form>

    <div class="links">
      <RouterLink :to="{ name: 'login' }">로그인으로 돌아가기</RouterLink>
    </div>
  </div>
</template>

<style scoped>
.auth-wrap {
  max-width: 420px;
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
  text-align: center;
  margin-top: 16px;
  font-size: 14px;
}
.links a {
  color: var(--primary);
  font-weight: 600;
}
</style>
