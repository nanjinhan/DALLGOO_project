<script setup>
import { ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'

import PasswordInput from '@/components/PasswordInput.vue'
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
    await authApi.forgotPassword(email.value)
    // 보안상 토큰은 응답에 오지 않는다. 실서비스는 이메일로, 개발 중에는 서버 로그에서 확인 후 입력.
    info.value =
      '가입된 이메일이라면 재설정 안내(토큰)를 보냈습니다. 받은 토큰을 아래에 입력하세요.'
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
        <PasswordInput v-model="newPassword" autocomplete="new-password" />
      </div>
      <div class="field">
        <label>새 비밀번호 확인</label>
        <PasswordInput v-model="newPasswordConfirm" autocomplete="new-password" />
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
