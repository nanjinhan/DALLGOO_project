<script setup>
const props = defineProps({
  liked: { type: Boolean, default: false },
  count: { type: Number, default: 0 },
  disabled: { type: Boolean, default: false },
})
const emit = defineEmits(['toggle'])
</script>

<template>
  <button
    class="like-btn"
    :class="{ liked }"
    :disabled="disabled"
    @click="emit('toggle')"
  >
    <span class="heart">{{ liked ? '❤' : '🤍' }}</span>
    <span>{{ count }}</span>
  </button>
</template>

<style scoped>
.like-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 14px;
  border: 1px solid var(--border);
  border-radius: 999px;
  background: #fff;
  font-size: 14px;
  font-weight: 600;
}
.like-btn.liked {
  border-color: #ff6b6b;
  color: #e03131;
  background: #fff0f0;
}
.like-btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}
</style>
