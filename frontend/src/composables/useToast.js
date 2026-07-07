import { ref } from 'vue'

// 전역 토스트 목록 (모듈 레벨 → 앱 어디서든 같은 목록 공유)
const toasts = ref([])
let seq = 0

function show(message, type = 'info', timeout = 2600) {
  const id = ++seq
  toasts.value.push({ id, message, type })
  setTimeout(() => dismiss(id), timeout)
}

function dismiss(id) {
  toasts.value = toasts.value.filter((t) => t.id !== id)
}

export function useToast() {
  return {
    toasts,
    dismiss,
    success: (m) => show(m, 'success'),
    error: (m) => show(m, 'error'),
    info: (m) => show(m, 'info'),
  }
}
