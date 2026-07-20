<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'

import { adminApi } from '@/api/admin'
import { settingsApi } from '@/api/settings'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import { errorMessage, formatDate } from '@/utils/format'

const auth = useAuthStore()
const toast = useToast()
const users = ref([])
const loading = ref(true)
const error = ref('')

// --- 실시간 활동 피드 (Kafka → Redis → 5초 폴링) ---
const activities = ref([])
let feedTimer = null

const ACTIVITY_ICON = {
  post: '📝',
  comment: '💬',
  like: '❤️',
  login: '🔑',
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await adminApi.users()
    users.value = data
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    loading.value = false
  }
}

async function loadActivities() {
  try {
    const { data } = await adminApi.activities()
    activities.value = data
  } catch {
    // 피드는 부가기능 — 실패해도 조용히 무시
  }
}

// --- 사이트 설정 (회사 소개 영상) ---
const introVideoUrl = ref('')
const savedVideoUrl = ref('') // 저장된 값 — 변경 여부 판단용
const settingsSaving = ref(false)

const settingsDirty = computed(
  () => introVideoUrl.value.trim() !== savedVideoUrl.value,
)

// 입력 중에도 썸네일이 보이도록 주소에서 ID를 뽑는다(백엔드 검증과 동일 규칙).
const introVideoId = computed(() => {
  const raw = introVideoUrl.value.trim()
  const m = raw.match(
    /(?:youtu\.be\/|v=|\/embed\/|\/shorts\/|\/live\/)([A-Za-z0-9_-]{11})/,
  )
  if (m) return m[1]
  return /^[A-Za-z0-9_-]{11}$/.test(raw) ? raw : ''
})

async function loadSettings() {
  try {
    const { data } = await settingsApi.get()
    savedVideoUrl.value = data.intro_video_url || ''
    introVideoUrl.value = savedVideoUrl.value
  } catch (e) {
    toast.error(errorMessage(e))
  }
}

async function saveSettings() {
  if (settingsSaving.value || !settingsDirty.value) return
  settingsSaving.value = true
  try {
    const { data } = await settingsApi.update({
      intro_video_url: introVideoUrl.value.trim(),
    })
    // 서버가 표준 주소로 정규화해 돌려주므로 그 값으로 맞춘다.
    savedVideoUrl.value = data.intro_video_url || ''
    introVideoUrl.value = savedVideoUrl.value
    toast.success('소개 영상을 저장했습니다.')
  } catch (e) {
    toast.error(errorMessage(e))
  } finally {
    settingsSaving.value = false
  }
}

async function toggleActive(u) {
  const next = !u.is_active
  const word = next ? '정지 해제' : '정지'
  if (!confirm(`'${u.nickname}' 회원을 ${word}할까요?`)) return
  try {
    await adminApi.setActive(u.id, next)
    u.is_active = next
    toast.success(next ? '정지를 해제했습니다.' : '회원을 정지했습니다.')
  } catch (e) {
    toast.error(errorMessage(e))
  }
}

onMounted(() => {
  load()
  loadSettings()
  loadActivities()
  feedTimer = setInterval(loadActivities, 5000) // 5초마다 갱신
})

onUnmounted(() => {
  if (feedTimer) clearInterval(feedTimer)
})
</script>

<template>
  <div class="admin">
    <h2>관리자 · 회원 관리</h2>

    <!-- 실시간 활동 피드 (Kafka) -->
    <div class="feed card">
      <div class="feed-head">
        <span class="live-dot" />
        실시간 활동
        <span class="muted small">· 5초마다 갱신</span>
      </div>
      <ul v-if="activities.length" class="feed-list">
        <li v-for="(a, i) in activities" :key="i">
          <span class="ico">{{ ACTIVITY_ICON[a.type] || '•' }}</span>
          <span class="who">{{ a.actor }}</span>
          <span class="what">{{ a.detail }}</span>
          <span class="when muted">{{ formatDate(a.at) }}</span>
        </li>
      </ul>
      <p v-else class="muted small" style="padding: 8px 4px">
        아직 활동이 없습니다. 글쓰기·댓글·좋아요·로그인을 하면 여기에 실시간으로 표시됩니다.
      </p>
    </div>

    <!-- 사이트 설정 — 회사 소개 영상 -->
    <div class="card settings">
      <div class="settings-head">
        <h3>회사 소개 영상</h3>
        <span class="muted small">랜딩페이지 · 회사소개 아래 섹션</span>
      </div>
      <p class="muted small settings-desc">
        유튜브 주소를 붙여넣고 저장하면 홈페이지에 바로 반영됩니다.
        비워두면 영상 섹션이 자리표시로 바뀝니다.
      </p>
      <div class="settings-row">
        <input
          v-model="introVideoUrl"
          type="url"
          class="input"
          placeholder="https://www.youtube.com/watch?v=영상ID"
          :disabled="settingsSaving"
          @keyup.enter="saveSettings"
        />
        <button
          class="btn btn-primary"
          :disabled="settingsSaving || !settingsDirty"
          @click="saveSettings"
        >
          {{ settingsSaving ? '저장 중…' : '저장' }}
        </button>
      </div>
      <div v-if="introVideoId" class="settings-preview">
        <img
          :src="`https://i.ytimg.com/vi/${introVideoId}/hqdefault.jpg`"
          alt="현재 설정된 영상 미리보기"
        />
        <div>
          <div class="small">현재 영상</div>
          <a
            :href="`https://www.youtube.com/watch?v=${introVideoId}`"
            target="_blank"
            rel="noopener"
            class="small link"
          >
            유튜브에서 열기 ↗
          </a>
        </div>
      </div>
    </div>

    <p class="muted" style="margin-bottom: 16px">
      총 {{ users.length }}명 · 정지된 회원은 로그인할 수 없습니다.
    </p>

    <div v-if="loading" class="muted">불러오는 중…</div>
    <p v-else-if="error" class="error-text">{{ error }}</p>

    <div v-else class="table-wrap card">
      <table class="tbl">
        <thead>
          <tr>
            <th>ID</th>
            <th>아이디</th>
            <th>닉네임</th>
            <th>이메일</th>
            <th class="num">글</th>
            <th class="num">댓글</th>
            <th>가입일</th>
            <th>상태</th>
            <th>관리</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="u in users" :key="u.id">
            <td>{{ u.id }}</td>
            <td>{{ u.username }}</td>
            <td>
              {{ u.nickname }}
              <span v-if="u.is_admin" class="tag admin">관리자</span>
            </td>
            <td class="email">{{ u.email }}</td>
            <td class="num">{{ u.post_count }}</td>
            <td class="num">{{ u.comment_count }}</td>
            <td>{{ formatDate(u.created_at) }}</td>
            <td>
              <span :class="['tag', u.is_active ? 'on' : 'off']">
                {{ u.is_active ? '활성' : '정지' }}
              </span>
            </td>
            <td>
              <button
                v-if="u.id !== auth.user?.id"
                class="btn small"
                :class="u.is_active ? 'btn-danger' : ''"
                @click="toggleActive(u)"
              >
                {{ u.is_active ? '정지' : '해제' }}
              </button>
              <span v-else class="muted small">본인</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.admin h2 {
  margin: 0 0 6px;
}
.settings {
  padding: 16px 18px;
  margin: 0 0 18px;
}
.settings-head {
  display: flex;
  align-items: baseline;
  gap: 8px;
  flex-wrap: wrap;
}
.settings-head h3 {
  margin: 0;
  font-size: 15px;
  font-weight: 700;
}
.settings-desc {
  margin: 6px 0 12px;
  line-height: 1.5;
}
.settings-row {
  display: flex;
  gap: 8px;
  align-items: center;
}
.settings-row .input {
  flex: 1;
  min-width: 0;
}
.settings-row .btn {
  flex-shrink: 0;
}
.settings-preview {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--border-soft);
}
.settings-preview img {
  width: 112px;
  aspect-ratio: 16 / 9;
  object-fit: cover;
  border-radius: 8px;
  background: var(--hover);
}
.link {
  color: var(--primary);
}
@media (max-width: 560px) {
  .settings-row {
    flex-direction: column;
    align-items: stretch;
  }
}
.feed {
  padding: 14px 16px;
  margin: 14px 0 18px;
}
.feed-head {
  display: flex;
  align-items: center;
  gap: 7px;
  font-weight: 700;
  font-size: 14px;
  margin-bottom: 10px;
}
.live-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #e03131;
  box-shadow: 0 0 0 0 rgba(224, 49, 49, 0.5);
  animation: pulse 1.6s infinite;
}
@keyframes pulse {
  0% { box-shadow: 0 0 0 0 rgba(224, 49, 49, 0.5); }
  70% { box-shadow: 0 0 0 7px rgba(224, 49, 49, 0); }
  100% { box-shadow: 0 0 0 0 rgba(224, 49, 49, 0); }
}
.feed-list {
  list-style: none;
  margin: 0;
  padding: 0;
  max-height: 260px;
  overflow-y: auto;
}
.feed-list li {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 7px 2px;
  border-bottom: 1px solid var(--border-soft);
  font-size: 13.5px;
}
.feed-list li:last-child {
  border-bottom: none;
}
.feed-list .ico {
  flex: none;
}
.feed-list .who {
  font-weight: 700;
}
.feed-list .what {
  color: var(--text);
}
.feed-list .when {
  margin-left: auto;
  font-size: 12px;
  white-space: nowrap;
}
.table-wrap {
  padding: 0;
  overflow-x: auto;
}
.tbl {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}
.tbl th,
.tbl td {
  padding: 11px 12px;
  border-bottom: 1px solid var(--border-soft);
  text-align: left;
  white-space: nowrap;
}
.tbl th {
  background: #f5f5f7;
  font-size: 12.5px;
  font-weight: 700;
}
.tbl tr:last-child td {
  border-bottom: none;
}
.num {
  text-align: center;
}
.email {
  color: var(--muted);
}
.tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 11.5px;
  font-weight: 700;
}
.tag.on {
  background: #e7f5ec;
  color: #2b8a3e;
}
.tag.off {
  background: #ffe9e9;
  color: var(--danger);
}
.tag.admin {
  background: var(--primary);
  color: #fff;
  margin-left: 4px;
}
.small {
  font-size: 12.5px;
  padding: 5px 12px;
}
</style>
