<script setup>
import { computed } from 'vue'

const props = defineProps({
  page: { type: Number, required: true },
  totalPages: { type: Number, required: true },
})
const emit = defineEmits(['change'])

const pages = computed(() => {
  const result = []
  const start = Math.max(1, props.page - 2)
  const end = Math.min(props.totalPages, start + 4)
  for (let i = start; i <= end; i++) result.push(i)
  return result
})

function go(p) {
  if (p < 1 || p > props.totalPages || p === props.page) return
  emit('change', p)
}
</script>

<template>
  <div v-if="totalPages > 1" class="pagination">
    <button class="pg-btn" :disabled="page <= 1" @click="go(page - 1)">이전</button>
    <button
      v-for="p in pages"
      :key="p"
      class="pg-btn"
      :class="{ active: p === page }"
      @click="go(p)"
    >
      {{ p }}
    </button>
    <button class="pg-btn" :disabled="page >= totalPages" @click="go(page + 1)">
      다음
    </button>
  </div>
</template>

<style scoped>
.pagination {
  display: flex;
  justify-content: center;
  gap: 6px;
  margin-top: 24px;
}
.pg-btn {
  min-width: 38px;
  padding: 8px 10px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: #fff;
  font-size: 14px;
}
.pg-btn:hover:not(:disabled) {
  background: #f1f3f5;
}
.pg-btn.active {
  background: var(--primary);
  border-color: var(--primary);
  color: #fff;
  font-weight: 700;
}
.pg-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}
</style>
