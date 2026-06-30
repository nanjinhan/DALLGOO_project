<script setup>
import { ref } from 'vue'

defineProps({
  modelValue: { type: String, default: '' },
  placeholder: { type: String, default: '' },
  autocomplete: { type: String, default: 'off' },
})
const emit = defineEmits(['update:modelValue'])

// 버튼을 누르고 있는 동안에만 true → 비밀번호 표시
const reveal = ref(false)
</script>

<template>
  <div class="pw-field">
    <input
      :type="reveal ? 'text' : 'password'"
      :value="modelValue"
      :placeholder="placeholder"
      :autocomplete="autocomplete"
      class="input pw-input"
      @input="emit('update:modelValue', $event.target.value)"
    />
    <button
      type="button"
      class="pw-toggle"
      :aria-label="reveal ? '비밀번호 가리기' : '누르고 있는 동안 비밀번호 보기'"
      @mousedown.prevent="reveal = true"
      @mouseup="reveal = false"
      @mouseleave="reveal = false"
      @touchstart.prevent="reveal = true"
      @touchend="reveal = false"
      @touchcancel="reveal = false"
    >
      <!-- 가려짐: 눈 / 보임: 눈에 빗금 -->
      <svg v-if="!reveal" width="20" height="20" viewBox="0 0 24 24" fill="none">
        <path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7Z" stroke="currentColor" stroke-width="1.7" />
        <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="1.7" />
      </svg>
      <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none">
        <path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7Z" stroke="currentColor" stroke-width="1.7" />
        <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="1.7" />
        <path d="M4 4l16 16" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" />
      </svg>
    </button>
  </div>
</template>

<style scoped>
.pw-field {
  position: relative;
}
.pw-input {
  padding-right: 44px;
}
.pw-toggle {
  position: absolute;
  right: 6px;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  background: none;
  color: var(--muted);
  cursor: pointer;
  border-radius: 8px;
}
.pw-toggle:hover {
  color: var(--text);
  background: rgba(0, 0, 0, 0.04);
}
</style>
