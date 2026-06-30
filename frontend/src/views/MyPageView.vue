<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import PasswordInput from '@/components/PasswordInput.vue'
import { userApi } from '@/api/auth'
import { useAuthStore } from '@/stores/auth'
import { errorMessage, formatDate } from '@/utils/format'

const auth = useAuthStore()
const router = useRouter()

const profile = reactive({ nickname: '', email: '' })
const profileMsg = ref('')
const profileErr = ref('')

const pw = reactive({ current_password: '', new_password: '', confirm: '' })
const pwMsg = ref('')
const pwErr = ref('')

const deletePw = ref('')
const deleteErr = ref('')

function syncProfile() {
  profile.nickname = auth.user?.nickname || ''
  profile.email = auth.user?.email || ''
}
syncProfile()

async function saveProfile() {
  profileMsg.value = ''
  profileErr.value = ''
  const payload = {}
  if (profile.nickname !== auth.user.nickname) payload.nickname = profile.nickname
  if (profile.email !== auth.user.email) payload.email = profile.email
  if (!Object.keys(payload).length) {
    profileMsg.value = '변경 사항이 없습니다.'
    return
  }
  try {
    const { data } = await userApi.updateMe(payload)
    auth.user = data
    profileMsg.value = '회원정보가 수정되었습니다.'
  } catch (e) {
    profileErr.value = errorMessage(e)
  }
}

async function changePassword() {
  pwMsg.value = ''
  pwErr.value = ''
  if (pw.new_password !== pw.confirm) {
    pwErr.value = '새 비밀번호가 일치하지 않습니다.'
    return
  }
  try {
    await userApi.changePassword({
      current_password: pw.current_password,
      new_password: pw.new_password,
    })
    pwMsg.value = '비밀번호가 변경되었습니다. 다시 로그인해주세요.'
    pw.current_password = pw.new_password = pw.confirm = ''
    setTimeout(async () => {
      await auth.logout()
      router.push({ name: 'login' })
    }, 1200)
  } catch (e) {
    pwErr.value = errorMessage(e)
  }
}

async function withdraw() {
  deleteErr.value = ''
  if (!confirm('정말 탈퇴하시겠습니까? 되돌릴 수 없습니다.')) return
  try {
    await userApi.deleteMe(deletePw.value)
    auth.forceLogout()
    alert('회원 탈퇴가 완료되었습니다.')
    router.push({ name: 'posts' })
  } catch (e) {
    deleteErr.value = errorMessage(e)
  }
}
</script>

<template>
  <div class="mypage">
    <h2>마이페이지</h2>

    <section class="card block">
      <div class="summary">
        <div>
          <div class="big">{{ auth.user?.nickname }}</div>
          <div class="muted">@{{ auth.user?.username }} · {{ auth.user?.email }}</div>
          <div class="muted">가입일 {{ formatDate(auth.user?.created_at) }}</div>
        </div>
        <div class="counts">
          <div class="count">
            <div class="num">{{ auth.user?.post_count ?? 0 }}</div>
            <div class="muted">작성글</div>
          </div>
          <div class="count">
            <div class="num">{{ auth.user?.comment_count ?? 0 }}</div>
            <div class="muted">작성댓글</div>
          </div>
        </div>
      </div>
    </section>

    <section class="card block">
      <h3>회원정보 수정</h3>
      <div class="field">
        <label>닉네임</label>
        <input v-model="profile.nickname" class="input" />
      </div>
      <div class="field">
        <label>이메일</label>
        <input v-model="profile.email" type="email" class="input" />
      </div>
      <p v-if="profileMsg" class="success-text">{{ profileMsg }}</p>
      <p v-if="profileErr" class="error-text">{{ profileErr }}</p>
      <button class="btn btn-primary" @click="saveProfile">저장</button>
    </section>

    <section class="card block">
      <h3>비밀번호 변경</h3>
      <div class="field">
        <label>현재 비밀번호</label>
        <PasswordInput v-model="pw.current_password" autocomplete="current-password" />
      </div>
      <div class="field">
        <label>새 비밀번호 (8~64자, 대·소문자·숫자 포함)</label>
        <PasswordInput v-model="pw.new_password" autocomplete="new-password" />
      </div>
      <div class="field">
        <label>새 비밀번호 확인</label>
        <PasswordInput v-model="pw.confirm" autocomplete="new-password" />
      </div>
      <p v-if="pwMsg" class="success-text">{{ pwMsg }}</p>
      <p v-if="pwErr" class="error-text">{{ pwErr }}</p>
      <button class="btn btn-primary" @click="changePassword">비밀번호 변경</button>
    </section>

    <section class="card block danger-zone">
      <h3>회원 탈퇴</h3>
      <p class="muted">탈퇴 시 계정이 비활성화됩니다. 비밀번호를 입력해 확인하세요.</p>
      <div class="field">
        <PasswordInput v-model="deletePw" placeholder="비밀번호" autocomplete="current-password" />
      </div>
      <p v-if="deleteErr" class="error-text">{{ deleteErr }}</p>
      <button class="btn btn-danger" @click="withdraw">회원 탈퇴</button>
    </section>
  </div>
</template>

<style scoped>
.mypage h2 {
  margin: 0 0 16px;
}
.block {
  margin-bottom: 16px;
}
.block h3 {
  margin: 0 0 14px;
  font-size: 16px;
}
.summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}
.big {
  font-size: 20px;
  font-weight: 800;
  margin-bottom: 4px;
}
.counts {
  display: flex;
  gap: 24px;
}
.count {
  text-align: center;
}
.num {
  font-size: 22px;
  font-weight: 800;
  color: var(--primary);
}
.danger-zone {
  border-color: #ffc9c9;
}
</style>
