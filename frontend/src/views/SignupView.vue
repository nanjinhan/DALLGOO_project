<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'

import PasswordInput from '@/components/PasswordInput.vue'
import { authApi } from '@/api/auth'
import { errorMessage } from '@/utils/format'

const router = useRouter()

const form = reactive({
  username: '',
  email: '',
  nickname: '',
  password: '',
  passwordConfirm: '',
})

// 중복확인 상태: null=미확인, true/false
const checked = reactive({ username: null, nickname: null })
const busy = ref(false)
const error = ref('')

// 이메일 인증 상태
const emailAuth = reactive({
  sent: false, // 인증번호 보냈는지
  verified: false, // 인증 완료
  code: '', // 입력한 인증번호
  msg: '',
  err: '',
  busy: false,
})

// 서버에 메일 발송이 설정돼 있을 때만 이메일 인증을 요구/표시
const verificationRequired = ref(false)
onMounted(async () => {
  try {
    const { data } = await authApi.config()
    verificationRequired.value = !!data.email_verification_required
  } catch {
    verificationRequired.value = false
  }
})

// 서버(§7.1.1)와 동일한 형식 규칙 — 클라이언트 1차 검증
const USERNAME_RE = /^[a-z][a-z0-9]{3,19}$/
const PASSWORD_RE = /^(?=.*[A-Z])(?=.*[a-z])(?=.*\d).{8,64}$/
const NICKNAME_RE = /^[가-힣a-zA-Z0-9]{2,20}$/
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

const usernameValid = computed(() =>
  USERNAME_RE.test(form.username.trim().toLowerCase()),
)
const emailValid = computed(() => EMAIL_RE.test(form.email.trim()))
const nicknameValid = computed(() => NICKNAME_RE.test(form.nickname.trim()))
const passwordValid = computed(
  () => !/\s/.test(form.password) && PASSWORD_RE.test(form.password),
)
const passwordMatch = computed(
  () => !!form.passwordConfirm && form.password === form.passwordConfirm,
)

async function check(field, apiFn) {
  const value = form[field]
  if (!value) return
  try {
    const { data } = await apiFn(value)
    checked[field] = data.available
  } catch {
    checked[field] = null
  }
}

function invalidate(field) {
  checked[field] = null
}

// 이메일이 바뀌면 인증 상태 초기화
function onEmailInput() {
  emailAuth.sent = false
  emailAuth.verified = false
  emailAuth.code = ''
  emailAuth.msg = ''
  emailAuth.err = ''
}

async function sendCode() {
  emailAuth.err = ''
  emailAuth.msg = ''
  if (!emailValid.value) {
    emailAuth.err = '올바른 이메일을 먼저 입력하세요.'
    return
  }
  emailAuth.busy = true
  try {
    const { data } = await authApi.sendEmailCode(form.email.trim())
    emailAuth.sent = true
    emailAuth.msg = data?.message || '인증번호를 보냈습니다. 메일을 확인하세요.'
  } catch (e) {
    emailAuth.err = errorMessage(e, '인증번호 발송에 실패했습니다.')
  } finally {
    emailAuth.busy = false
  }
}

async function verifyCode() {
  emailAuth.err = ''
  if (emailAuth.code.length !== 6) {
    emailAuth.err = '6자리 인증번호를 입력하세요.'
    return
  }
  emailAuth.busy = true
  try {
    await authApi.verifyEmailCode(form.email.trim(), emailAuth.code)
    emailAuth.verified = true
    emailAuth.msg = '이메일 인증이 완료되었습니다.'
  } catch (e) {
    emailAuth.err = errorMessage(e, '인증번호가 올바르지 않습니다.')
  } finally {
    emailAuth.busy = false
  }
}

const canSubmit = () =>
  usernameValid.value &&
  emailValid.value &&
  (!verificationRequired.value || emailAuth.verified) &&
  nicknameValid.value &&
  passwordValid.value &&
  passwordMatch.value &&
  checked.username === true &&
  checked.nickname === true

async function submit() {
  error.value = ''
  if (!passwordValid.value) {
    error.value = '비밀번호는 8~64자이며 대문자·소문자·숫자를 각각 1자 이상 포함해야 합니다.'
    return
  }
  if (!passwordMatch.value) {
    error.value = '비밀번호가 일치하지 않습니다.'
    return
  }
  busy.value = true
  try {
    await authApi.signup({
      username: form.username,
      email: form.email,
      nickname: form.nickname,
      password: form.password,
    })
    alert('회원가입이 완료되었습니다. 로그인해주세요.')
    router.push({ name: 'login' })
  } catch (e) {
    error.value = errorMessage(e, '회원가입에 실패했습니다.')
  } finally {
    busy.value = false
  }
}

function badge(state) {
  if (state === true) return { text: '사용 가능', cls: 'ok' }
  if (state === false) return { text: '사용 중', cls: 'no' }
  return null
}
</script>

<template>
  <div class="auth-wrap card">
    <h2>회원가입</h2>
    <form @submit.prevent="submit">
      <div class="field">
        <label>아이디</label>
        <div class="row">
          <input
            v-model="form.username"
            class="input"
            @input="invalidate('username')"
          />
          <button
            type="button"
            class="btn"
            @click="check('username', authApi.checkUsername)"
          >
            중복확인
          </button>
        </div>
        <span
          v-if="form.username && !usernameValid"
          class="hint no"
        >
          영문 소문자로 시작하는 4~20자 (영문 소문자·숫자만)
        </span>
        <span
          v-else-if="badge(checked.username)"
          :class="['hint', badge(checked.username).cls]"
        >
          {{ badge(checked.username).text }}
        </span>
      </div>

      <div class="field">
        <label>이메일<span v-if="verificationRequired"> (인증 필요)</span></label>
        <div class="row">
          <input
            v-model="form.email"
            type="email"
            class="input"
            :disabled="verificationRequired && emailAuth.verified"
            @input="onEmailInput"
          />
          <button
            v-if="verificationRequired"
            type="button"
            class="btn"
            :disabled="!emailValid || emailAuth.verified || emailAuth.busy"
            @click="sendCode"
          >
            {{ emailAuth.sent ? '재전송' : '인증번호 받기' }}
          </button>
        </div>
        <span v-if="form.email && !emailValid" class="hint no">
          올바른 이메일 형식이 아닙니다. (예: name@example.com)
        </span>

        <!-- 인증번호 입력 (메일 발송이 설정된 경우에만) -->
        <template v-if="verificationRequired">
          <div
            v-if="emailAuth.sent && !emailAuth.verified"
            class="row"
            style="margin-top: 8px"
          >
            <input
              v-model="emailAuth.code"
              class="input"
              inputmode="numeric"
              maxlength="6"
              placeholder="6자리 인증번호"
            />
            <button
              type="button"
              class="btn btn-primary"
              :disabled="emailAuth.busy"
              @click="verifyCode"
            >
              확인
            </button>
          </div>
          <span v-if="emailAuth.verified" class="hint ok">✓ 이메일 인증 완료</span>
          <span v-else-if="emailAuth.err" class="hint no">{{ emailAuth.err }}</span>
          <span
            v-else-if="emailAuth.msg"
            class="hint"
            style="color: var(--muted)"
            >{{ emailAuth.msg }}</span
          >
        </template>
      </div>

      <div class="field">
        <label>닉네임</label>
        <div class="row">
          <input
            v-model="form.nickname"
            class="input"
            @input="invalidate('nickname')"
          />
          <button
            type="button"
            class="btn"
            @click="check('nickname', authApi.checkNickname)"
          >
            중복확인
          </button>
        </div>
        <span
          v-if="form.nickname && !nicknameValid"
          class="hint no"
        >
          2~20자 (한글·영문·숫자만)
        </span>
        <span
          v-else-if="badge(checked.nickname)"
          :class="['hint', badge(checked.nickname).cls]"
        >
          {{ badge(checked.nickname).text }}
        </span>
      </div>

      <div class="field">
        <label>비밀번호 (8~64자, 대·소문자·숫자 포함)</label>
        <PasswordInput v-model="form.password" autocomplete="new-password" />
        <span v-if="form.password && !passwordValid" class="hint no">
          8~64자이며 대문자·소문자·숫자를 각각 1자 이상 포함해야 합니다.
        </span>
      </div>
      <div class="field">
        <label>비밀번호 확인</label>
        <PasswordInput v-model="form.passwordConfirm" autocomplete="new-password" />
        <span
          v-if="form.passwordConfirm && form.password !== form.passwordConfirm"
          class="hint no"
        >
          비밀번호가 일치하지 않습니다.
        </span>
      </div>

      <p v-if="error" class="error-text">{{ error }}</p>
      <button class="btn btn-primary full" :disabled="busy || !canSubmit()">
        가입하기
      </button>
    </form>
    <div class="links">
      <span class="muted">이미 계정이 있으신가요?</span>
      <RouterLink :to="{ name: 'login' }">로그인</RouterLink>
    </div>
  </div>
</template>

<style scoped>
.auth-wrap {
  max-width: 440px;
  margin: 32px auto;
}
/* 아이디/이메일/닉네임 줄: 입력칸은 늘고, 중복확인 버튼은 한 줄 고정 */
.row .input {
  flex: 1;
  min-width: 0;
}
.row .btn {
  flex-shrink: 0;
  white-space: nowrap;
}
h2 {
  margin: 0 0 20px;
}
.full {
  width: 100%;
  margin-top: 8px;
}
.hint {
  display: inline-block;
  margin-top: 6px;
  font-size: 13px;
  font-weight: 600;
}
.hint.ok {
  color: #2b8a3e;
}
.hint.no {
  color: var(--danger);
}
.links {
  display: flex;
  gap: 8px;
  justify-content: center;
  margin-top: 16px;
  font-size: 14px;
}
.links a {
  color: var(--primary);
  font-weight: 600;
}
</style>
