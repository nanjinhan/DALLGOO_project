import { ref } from 'vue'

const KEY = 'dallgoo_theme'

// 저장된 테마(없으면 light)로 시작
const theme = ref(localStorage.getItem(KEY) || 'light')

function apply(t) {
  document.documentElement.setAttribute('data-theme', t)
}

// 앱 로드 시 즉시 반영
apply(theme.value)

export function useTheme() {
  function toggle() {
    theme.value = theme.value === 'dark' ? 'light' : 'dark'
    localStorage.setItem(KEY, theme.value)
    apply(theme.value)
  }
  return { theme, toggle }
}
