<script setup>
import { onMounted, reactive, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'

import { transportApi } from '@/api/transport'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import { errorMessage, formatDate } from '@/utils/format'

const props = defineProps({
  id: { type: [Number, String], required: true },
})

const auth = useAuthStore()
const router = useRouter()
const toast = useToast()

const rec = ref(null)
const comments = ref([])
const loading = ref(true)
const error = ref('')

// 보호자 인증(이름+코드) — 인증과 댓글 작성에 함께 사용
const guardian = reactive({ name: '', code: '' })
const verified = ref(false)
const unlocked = reactive({ patient_name: '', detail: '' })
const showAuth = ref(false)
const authBusy = ref(false)

// 4점 척도 / 추천(NPS)
const SCALE4 = [
  { v: 1, label: '매우 불만족' },
  { v: 2, label: '불만족' },
  { v: 3, label: '만족' },
  { v: 4, label: '매우 만족' },
]
const NPS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

const cform = reactive({
  content: '',
  medical: null,
  driving: null,
  hygiene: null,
  recommend: null,
})
const commentBusy = ref(false)

async function load() {
  loading.value = true
  try {
    const [d, c] = await Promise.all([
      transportApi.detail(props.id),
      transportApi.comments(props.id),
    ])
    rec.value = d.data
    comments.value = c.data
  } catch (e) {
    error.value = errorMessage(e, '이송 기록을 불러올 수 없습니다.')
  } finally {
    loading.value = false
  }
}

async function verifyGuardian() {
  if (!guardian.name.trim() || !guardian.code.trim()) {
    toast.error('보호자 이름과 인증 코드를 입력하세요.')
    return
  }
  authBusy.value = true
  try {
    const { data } = await transportApi.verify(props.id, {
      name: guardian.name.trim(),
      code: guardian.code.trim(),
    })
    unlocked.patient_name = data.patient_name
    unlocked.detail = data.detail
    verified.value = true
    showAuth.value = false
    toast.success('보호자 인증 완료 — 상세 정보가 열렸습니다.')
  } catch (e) {
    toast.error(errorMessage(e))
  } finally {
    authBusy.value = false
  }
}

async function submitComment() {
  const first = comments.value.length === 0
  if (!guardian.name.trim() || !guardian.code.trim()) {
    toast.error('보호자 이름과 인증 코드를 입력하세요.')
    return
  }
  if (!cform.content.trim()) {
    toast.error('댓글 내용을 입력하세요.')
    return
  }
  if (
    first &&
    (!cform.medical || !cform.driving || !cform.hygiene || !cform.recommend)
  ) {
    toast.error('첫 댓글에는 이송 서비스 평가가 필수입니다.')
    return
  }
  commentBusy.value = true
  try {
    const payload = {
      name: guardian.name.trim(),
      code: guardian.code.trim(),
      content: cform.content.trim(),
    }
    if (first) {
      payload.medical = cform.medical
      payload.driving = cform.driving
      payload.hygiene = cform.hygiene
      payload.recommend = cform.recommend
    }
    await transportApi.addComment(props.id, payload)
    toast.success('댓글이 등록되었습니다.')
    cform.content = ''
    cform.medical = cform.driving = cform.hygiene = cform.recommend = null
    await load()
  } catch (e) {
    toast.error(errorMessage(e))
  } finally {
    commentBusy.value = false
  }
}

async function remove() {
  if (!confirm('[관리자] 이 이송 기록을 삭제할까요?')) return
  try {
    await transportApi.remove(props.id)
    toast.success('이송 기록을 삭제했습니다.')
    router.push({ name: 'transport' })
  } catch (e) {
    toast.error(errorMessage(e))
  }
}

onMounted(load)
</script>

<template>
  <div class="tr-detail">
    <div v-if="loading" class="muted center">불러오는 중…</div>
    <p v-else-if="error && !rec" class="error-text center">{{ error }}</p>

    <template v-else-if="rec">
      <div class="head">
        <h1>{{ rec.title }}</h1>
        <div class="meta">
          <span>👤 {{ rec.author }}</span>
          <span class="dot">·</span>
          <span>📅 {{ formatDate(rec.created_at) }}</span>
          <span class="dot">·</span>
          <span>👁 조회 {{ rec.view_count }}회</span>
          <span class="spacer" />
          <button v-if="auth.isAdmin" class="btn btn-danger small" @click="remove">
            삭제
          </button>
        </div>
      </div>

      <!-- 관리자: 보호자 인증코드 안내 -->
      <div v-if="auth.isAdmin && rec.guardian_code" class="admin-box">
        🔑 <b>보호자 인증 정보</b> (관리자만 표시) — 보호자
        <b>{{ rec.guardian_name || '(미지정)' }}</b> 님께 코드
        <code>{{ rec.guardian_code }}</code> 를 전달하세요.
      </div>

      <!-- 이송 정보 -->
      <section class="panel">
        <div class="panel-head">이송 정보</div>
        <div class="panel-body info-layout">
          <div class="photo">
            <img
              v-if="rec.has_image"
              :src="transportApi.imageUrl(rec.id)"
              alt="이송 사진"
            />
            <div v-else class="photo-empty">🚑</div>
          </div>

          <div class="info-cards">
            <div class="mini">
              <div class="mini-h">🚑 이송 경로</div>
              <div class="route">
                <div class="rp">
                  <div class="rp-k">출발지</div>
                  <div class="rp-v">{{ rec.from_hospital }}</div>
                </div>
                <div class="rp-arrow">→</div>
                <div class="rp">
                  <div class="rp-k">도착지</div>
                  <div class="rp-v">{{ rec.to_hospital }}</div>
                </div>
              </div>
            </div>

            <div class="mini">
              <div class="mini-h">📍 이송 세부정보</div>
              <div class="detail-grid">
                <div>
                  <div class="rp-k">이송 거리</div>
                  <div class="rp-v">{{ rec.distance_km }} km</div>
                </div>
                <div>
                  <div class="rp-k">소요 시간</div>
                  <div class="rp-v">{{ rec.duration_min }} 분</div>
                </div>
              </div>
            </div>

            <div class="mini">
              <div class="mini-h">👤 환자 정보</div>
              <p v-if="verified" class="rp-v">{{ unlocked.patient_name }}</p>
              <p v-else class="locked-note">
                이송 상세 정보는 보호자 인증 후 확인할 수 있습니다.
              </p>
            </div>

            <div v-if="rec.crew.length" class="mini">
              <div class="mini-h">👥 출동 크루원</div>
              <div class="crew">
                <span v-for="(c, i) in rec.crew" :key="i" class="crew-badge">{{ c }}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 이송 상세 정보 (잠금/해제) -->
      <section class="panel">
        <div class="panel-head">이송 상세 정보</div>
        <div class="panel-body">
          <div v-if="verified" class="unlocked-detail">
            {{ unlocked.detail || '등록된 상세 내용이 없습니다.' }}
          </div>
          <div v-else class="locked">
            <div class="lock-ic">🔒</div>
            <p>이송 상세 정보는 보호자 인증 후 확인할 수 있습니다.</p>
            <button v-if="!showAuth" class="btn btn-primary" @click="showAuth = true">
              🔑 보호자 인증하기
            </button>
            <div v-else class="auth-form">
              <input v-model="guardian.name" class="input" placeholder="보호자 이름" />
              <input v-model="guardian.code" class="input" placeholder="인증 코드" />
              <button class="btn btn-primary" :disabled="authBusy" @click="verifyGuardian">
                인증
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- 댓글 -->
      <section class="panel">
        <div class="panel-head">💬 댓글 ({{ comments.length }})</div>
        <div class="panel-body">
          <div v-if="!comments.length" class="muted center" style="padding: 14px 0">
            등록된 댓글이 없습니다.
          </div>
          <ul v-else class="clist">
            <li v-for="c in comments" :key="c.id" class="citem">
              <div class="chead">
                <span class="cname">{{ c.guardian_name }}</span>
                <span class="muted">{{ formatDate(c.created_at) }}</span>
              </div>
              <div v-if="c.recommend" class="crating">
                의료 {{ c.medical }}/4 · 운전 {{ c.driving }}/4 · 위생
                {{ c.hygiene }}/4 · 추천 {{ c.recommend }}/10
              </div>
              <p class="cbody">{{ c.content }}</p>
            </li>
          </ul>

          <!-- 댓글 작성 -->
          <div class="cform">
            <p class="muted small">
              보호자분은 문자로 받으신 인증 코드로 댓글을 남길 수 있습니다.
            </p>
            <div class="grid2">
              <input v-model="guardian.name" class="input" placeholder="보호자 이름" />
              <input v-model="guardian.code" class="input" placeholder="인증 코드" />
            </div>

            <!-- 첫 댓글: 평가 설문 -->
            <div v-if="!comments.length" class="survey">
              <div class="survey-h">⭐ 이송 서비스 평가 <span class="req">(첫 댓글 필수)</span></div>
              <div class="q">
                <div class="q-t">1. 의료 전문성</div>
                <div class="opts">
                  <label v-for="o in SCALE4" :key="o.v" class="opt" :class="{ on: cform.medical === o.v }">
                    <input v-model="cform.medical" type="radio" :value="o.v" />{{ o.label }}
                  </label>
                </div>
              </div>
              <div class="q">
                <div class="q-t">2. 운전 기술</div>
                <div class="opts">
                  <label v-for="o in SCALE4" :key="o.v" class="opt" :class="{ on: cform.driving === o.v }">
                    <input v-model="cform.driving" type="radio" :value="o.v" />{{ o.label }}
                  </label>
                </div>
              </div>
              <div class="q">
                <div class="q-t">3. 위생 / 청결</div>
                <div class="opts">
                  <label v-for="o in SCALE4" :key="o.v" class="opt" :class="{ on: cform.hygiene === o.v }">
                    <input v-model="cform.hygiene" type="radio" :value="o.v" />{{ o.label }}
                  </label>
                </div>
              </div>
              <div class="q">
                <div class="q-t">4. 추천 의향</div>
                <div class="nps">
                  <label v-for="n in NPS" :key="n" class="nps-opt" :class="{ on: cform.recommend === n }">
                    <input v-model="cform.recommend" type="radio" :value="n" />{{ n }}
                  </label>
                </div>
                <div class="muted small" style="text-align: center">
                  1점(전혀 추천 안 함) ~ 10점(적극 추천)
                </div>
              </div>
            </div>

            <textarea
              v-model="cform.content"
              class="textarea"
              maxlength="100"
              placeholder="댓글을 입력하세요... (최대 100자)"
            />
            <div class="cform-foot">
              <span class="muted small">{{ cform.content.length }}/100</span>
              <button class="btn btn-primary" :disabled="commentBusy" @click="submitComment">
                댓글 등록
              </button>
            </div>
          </div>
        </div>
      </section>

      <div class="back">
        <RouterLink :to="{ name: 'transport' }" class="btn">← 목록으로</RouterLink>
      </div>
    </template>
  </div>
</template>

<style scoped>
.head {
  margin-bottom: 16px;
}
.head h1 {
  font-size: 24px;
  margin: 0 0 10px;
}
.meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--muted);
}
.small {
  padding: 5px 10px;
  font-size: 13px;
}
.admin-box {
  background: rgba(255, 149, 0, 0.1);
  border: 1px solid rgba(255, 149, 0, 0.35);
  border-radius: 12px;
  padding: 12px 16px;
  font-size: 13.5px;
  margin-bottom: 18px;
}
.admin-box code {
  background: var(--text);
  color: var(--card);
  padding: 2px 8px;
  border-radius: 6px;
  font-weight: 700;
  letter-spacing: 1px;
}
.panel {
  background: var(--card);
  border: 1px solid var(--border-soft);
  border-radius: 14px;
  overflow: hidden;
  margin-bottom: 18px;
}
.panel-head {
  padding: 14px 18px;
  background: var(--hover);
  font-weight: 700;
  font-size: 15px;
  border-bottom: 1px solid var(--border-soft);
}
.panel-body {
  padding: 18px;
}
.info-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18px;
}
.photo {
  border-radius: 10px;
  overflow: hidden;
  background: var(--hover);
  aspect-ratio: 4 / 3;
}
.photo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.photo-empty {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48px;
  opacity: 0.4;
}
.info-cards {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.mini {
  background: var(--bg);
  border-radius: 10px;
  padding: 13px 15px;
}
.mini-h {
  font-size: 13px;
  font-weight: 700;
  margin-bottom: 10px;
}
.route {
  display: flex;
  align-items: center;
  gap: 12px;
}
.rp-k {
  font-size: 11.5px;
  color: var(--muted);
  margin-bottom: 3px;
}
.rp-v {
  font-size: 14px;
  font-weight: 700;
  margin: 0;
}
.rp-arrow {
  color: var(--primary);
  font-size: 18px;
  font-weight: 700;
}
.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}
.locked-note {
  margin: 0;
  font-size: 13px;
  color: var(--muted);
}
.crew {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.crew-badge {
  padding: 5px 12px;
  border-radius: 999px;
  background: var(--card);
  border: 1px solid var(--border);
  font-size: 13px;
  font-weight: 600;
}
.unlocked-detail {
  white-space: pre-wrap;
  font-size: 14.5px;
  line-height: 1.7;
}
.locked {
  text-align: center;
  padding: 30px 18px;
}
.lock-ic {
  font-size: 34px;
  opacity: 0.5;
  margin-bottom: 12px;
}
.locked p {
  color: var(--muted);
  font-size: 14px;
  margin: 0 0 16px;
}
.auth-form {
  display: flex;
  gap: 8px;
  max-width: 460px;
  margin: 0 auto;
}
.auth-form .btn {
  flex-shrink: 0;
}

/* 댓글 */
.clist {
  list-style: none;
  margin: 0 0 18px;
  padding: 0;
}
.citem {
  padding: 12px 0;
  border-bottom: 1px solid var(--border-soft);
}
.chead {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 5px;
}
.cname {
  font-weight: 700;
  font-size: 14px;
}
.crating {
  font-size: 12px;
  color: var(--primary);
  font-weight: 600;
  margin-bottom: 5px;
}
.cbody {
  margin: 0;
  font-size: 14px;
  line-height: 1.55;
  white-space: pre-wrap;
}
.cform {
  border-top: 1px solid var(--border-soft);
  padding-top: 16px;
}
.grid2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin: 10px 0;
}
.survey {
  background: var(--bg);
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 12px;
}
.survey-h {
  font-weight: 700;
  margin-bottom: 14px;
}
.req {
  color: var(--danger);
  font-size: 12px;
}
.q {
  margin-bottom: 14px;
}
.q-t {
  font-size: 13.5px;
  font-weight: 600;
  margin-bottom: 8px;
}
.opts {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 6px;
}
.opt {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  padding: 8px 6px;
  border: 1px solid var(--border);
  border-radius: 8px;
  font-size: 12.5px;
  cursor: pointer;
  background: var(--card);
}
.opt.on {
  border-color: var(--primary);
  color: var(--primary);
  font-weight: 700;
}
.opt input {
  display: none;
}
.nps {
  display: grid;
  grid-template-columns: repeat(10, 1fr);
  gap: 4px;
  margin-bottom: 6px;
}
.nps-opt {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px 0;
  border: 1px solid var(--border);
  border-radius: 8px;
  font-size: 13px;
  cursor: pointer;
  background: var(--card);
}
.nps-opt.on {
  background: var(--primary);
  color: #fff;
  border-color: var(--primary);
  font-weight: 700;
}
.nps-opt input {
  display: none;
}
.cform-foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 10px;
}
.center {
  text-align: center;
  padding: 20px 0;
}
.back {
  margin-top: 6px;
}
@media (max-width: 700px) {
  .info-layout {
    grid-template-columns: 1fr;
  }
  .opts {
    grid-template-columns: repeat(2, 1fr);
  }
  .nps {
    grid-template-columns: repeat(5, 1fr);
  }
}
</style>
