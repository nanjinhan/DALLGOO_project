<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { notificationApi } from '@/api/admin'
import { formatDate } from '@/utils/format'

const router = useRouter()
const open = ref(false)
const unread = ref(0)
const items = ref([])
let timer = null

async function loadCount() {
  try {
    const { data } = await notificationApi.unreadCount()
    unread.value = data.unread
  } catch {
    /* 무시 */
  }
}

async function loadList() {
  try {
    const { data } = await notificationApi.list()
    items.value = data
  } catch {
    /* 무시 */
  }
}

async function toggle() {
  open.value = !open.value
  if (open.value) await loadList()
}

async function onClickItem(n) {
  try {
    if (!n.is_read) await notificationApi.read(n.id)
  } catch {
    /* 무시 */
  }
  open.value = false
  loadCount()
  if (n.post_id) router.push({ name: 'post-detail', params: { id: n.post_id } })
}

async function readAll() {
  await notificationApi.readAll()
  await loadList()
  unread.value = 0
}

function onDocClick(e) {
  if (!e.target.closest('.noti')) open.value = false
}

onMounted(() => {
  loadCount()
  timer = setInterval(loadCount, 30000) // 30초마다 미읽음 갱신
  document.addEventListener('click', onDocClick)
})
onUnmounted(() => {
  clearInterval(timer)
  document.removeEventListener('click', onDocClick)
})
</script>

<template>
  <div class="noti">
    <button class="noti-btn" aria-label="알림" @click.stop="toggle">
      🔔
      <span v-if="unread > 0" class="badge">{{ unread > 99 ? '99+' : unread }}</span>
    </button>

    <div v-if="open" class="noti-pop" @click.stop>
      <div class="noti-head">
        <span>알림</span>
        <button v-if="items.length" class="link" @click="readAll">모두 읽음</button>
      </div>
      <div v-if="!items.length" class="noti-empty">알림이 없습니다.</div>
      <ul v-else class="noti-list">
        <li
          v-for="n in items"
          :key="n.id"
          :class="{ unread: !n.is_read }"
          @click="onClickItem(n)"
        >
          <div class="msg">{{ n.message }}</div>
          <div class="time">{{ formatDate(n.created_at) }}</div>
        </li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.noti {
  position: relative;
  display: flex;
  align-items: center;
}
.noti-btn {
  position: relative;
  border: none;
  background: none;
  font-size: 19px;
  cursor: pointer;
  padding: 4px;
  line-height: 1;
}
.badge {
  position: absolute;
  top: -2px;
  right: -4px;
  min-width: 17px;
  height: 17px;
  padding: 0 4px;
  background: var(--danger);
  color: #fff;
  font-size: 11px;
  font-weight: 700;
  border-radius: 999px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.noti-pop {
  position: absolute;
  top: 38px;
  right: 0;
  width: 320px;
  max-height: 420px;
  overflow-y: auto;
  background: #fff;
  border: 1px solid var(--border);
  border-radius: 12px;
  box-shadow: 0 12px 32px -8px rgba(0, 0, 0, 0.18);
  z-index: 200;
}
.noti-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 14px;
  border-bottom: 1px solid var(--border-soft);
  font-weight: 700;
  font-size: 14px;
}
.link {
  border: none;
  background: none;
  color: var(--primary);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
}
.noti-empty {
  padding: 28px 14px;
  text-align: center;
  color: var(--muted);
  font-size: 14px;
}
.noti-list {
  list-style: none;
  margin: 0;
  padding: 0;
}
.noti-list li {
  padding: 11px 14px;
  border-bottom: 1px solid var(--border-soft);
  cursor: pointer;
}
.noti-list li:hover {
  background: #f5f5f7;
}
.noti-list li.unread {
  background: rgba(0, 113, 227, 0.06);
}
.msg {
  font-size: 13.5px;
  line-height: 1.45;
  color: var(--text);
}
.time {
  margin-top: 3px;
  font-size: 12px;
  color: var(--muted);
}
</style>
