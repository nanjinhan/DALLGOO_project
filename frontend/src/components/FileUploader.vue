<script setup>
import { ref } from 'vue'
import { formatSize } from '@/utils/format'

const props = defineProps({
  modelValue: { type: Array, default: () => [] },
})
const emit = defineEmits(['update:modelValue'])

const inputRef = ref(null)

function onPick(e) {
  const picked = Array.from(e.target.files || [])
  emit('update:modelValue', [...props.modelValue, ...picked])
  if (inputRef.value) inputRef.value.value = ''
}

function removeAt(idx) {
  const next = [...props.modelValue]
  next.splice(idx, 1)
  emit('update:modelValue', next)
}
</script>

<template>
  <div class="uploader">
    <button type="button" class="btn" @click="inputRef.click()">📎 파일 추가</button>
    <input ref="inputRef" type="file" multiple class="hidden" @change="onPick" />

    <ul v-if="modelValue.length" class="file-list">
      <li v-for="(f, i) in modelValue" :key="i">
        <span class="name">{{ f.name }}</span>
        <span class="muted">{{ formatSize(f.size) }}</span>
        <button type="button" class="remove" @click="removeAt(i)">✕</button>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.hidden {
  display: none;
}
.file-list {
  list-style: none;
  padding: 0;
  margin: 12px 0 0;
}
.file-list li {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  border: 1px solid var(--border);
  border-radius: 8px;
  margin-bottom: 6px;
  font-size: 14px;
}
.name {
  font-weight: 600;
}
.remove {
  margin-left: auto;
  border: none;
  background: none;
  color: var(--muted);
  font-size: 14px;
}
.remove:hover {
  color: var(--danger);
}
</style>
