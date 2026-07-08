<script setup>
import { onMounted, ref } from 'vue'

const KEY = 'dallgoo_popup_hide_date'
const show = ref(false)

onMounted(() => {
  // '오늘 하루 보지 않기'로 저장된 날짜가 오늘과 같으면 표시하지 않음
  const hideDate = localStorage.getItem(KEY)
  const today = new Date().toDateString()
  if (hideDate !== today) {
    show.value = true
  }
})

// 닫기: 이번만 닫힘 → 다음 방문(새로고침) 시 다시 뜸
function close() {
  show.value = false
}

// 오늘 하루 보지 않기: 오늘 날짜 저장 → 자정 지나면 다시 뜸
function hideToday() {
  localStorage.setItem(KEY, new Date().toDateString())
  show.value = false
}
</script>

<template>
  <Transition name="popup">
    <div v-if="show" class="popup-overlay" @click.self="close">
      <div class="popup-card">
        <button class="popup-x" aria-label="닫기" @click="close">✕</button>

        <!-- 배너 이미지 -->
        <img class="popup-img" src="/images/popup.png" alt="주식회사 달구 — ABC 통합 응급처치 AI 코파일럿" />

        <!-- 하단 버튼 -->
        <div class="popup-actions">
          <button class="popup-btn ghost" @click="hideToday">오늘 하루 보지 않기</button>
          <button class="popup-btn solid" @click="close">닫기</button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.popup-overlay {
  position: fixed;
  inset: 0;
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: rgba(0, 0, 0, 0.55);
  backdrop-filter: blur(4px);
}
.popup-card {
  position: relative;
  width: 100%;
  max-width: 620px;
  border-radius: 18px;
  overflow: hidden;
  background: #0a0f1a;
  box-shadow: 0 24px 70px -18px rgba(0, 0, 0, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.08);
}
.popup-img {
  display: block;
  width: 100%;
  height: auto;
}
.popup-x {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.45);
  color: #fff;
  font-size: 14px;
  transition: 0.15s;
}
.popup-x:hover {
  background: rgba(0, 0, 0, 0.7);
}
.popup-actions {
  display: flex;
  background: #0a0f1a;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}
.popup-btn {
  flex: 1;
  padding: 15px;
  border: none;
  background: transparent;
  font-size: 14px;
  font-weight: 600;
  color: #9fb3c8;
  transition: 0.15s;
}
.popup-btn.ghost:hover {
  background: rgba(255, 255, 255, 0.06);
  color: #fff;
}
.popup-btn.solid {
  color: #fff;
  background: var(--primary);
}
.popup-btn.solid:hover {
  background: var(--primary-dark);
}

/* 등장/퇴장 애니메이션 */
.popup-enter-active,
.popup-leave-active {
  transition: opacity 0.25s ease;
}
.popup-enter-active .popup-card,
.popup-leave-active .popup-card {
  transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
.popup-enter-from,
.popup-leave-to {
  opacity: 0;
}
.popup-enter-from .popup-card {
  transform: translateY(24px) scale(0.96);
}
</style>
