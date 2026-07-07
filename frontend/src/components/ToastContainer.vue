<script setup>
import { useToast } from '@/composables/useToast'

const { toasts, dismiss } = useToast()

const ICON = { success: '✓', error: '⚠', info: 'ℹ' }
</script>

<template>
  <div class="toast-wrap">
    <TransitionGroup name="toast">
      <div
        v-for="t in toasts"
        :key="t.id"
        :class="['toast', t.type]"
        @click="dismiss(t.id)"
      >
        <span class="t-ico">{{ ICON[t.type] }}</span>
        <span>{{ t.message }}</span>
      </div>
    </TransitionGroup>
  </div>
</template>

<style scoped>
.toast-wrap {
  position: fixed;
  top: 70px;
  right: 20px;
  z-index: 3000;
  display: flex;
  flex-direction: column;
  gap: 10px;
  pointer-events: none;
}
.toast {
  pointer-events: auto;
  display: flex;
  align-items: center;
  gap: 9px;
  min-width: 220px;
  max-width: 340px;
  padding: 13px 16px;
  border-radius: 12px;
  background: var(--card);
  border: 1px solid var(--border-soft);
  box-shadow: 0 8px 28px -8px rgba(0, 0, 0, 0.25);
  font-size: 14px;
  font-weight: 500;
  color: var(--text);
  cursor: pointer;
}
.t-ico {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  font-size: 12px;
  font-weight: 700;
  color: #fff;
  flex: none;
}
.toast.success .t-ico {
  background: #2b8a3e;
}
.toast.error .t-ico {
  background: var(--danger);
}
.toast.info .t-ico {
  background: var(--primary);
}

/* 등장/퇴장 애니메이션 */
.toast-enter-active,
.toast-leave-active {
  transition: all 0.28s cubic-bezier(0.16, 1, 0.3, 1);
}
.toast-enter-from {
  opacity: 0;
  transform: translateX(40px);
}
.toast-leave-to {
  opacity: 0;
  transform: translateX(40px);
}
</style>
