<script setup>
import { computed } from 'vue'

const props = defineProps({
  address: { type: String, required: true },
  height: { type: String, default: '360px' },
})

// 구글 지도 임베드 — API 키·도메인 등록·심사 불필요(누구나 바로 표시)
const src = computed(
  () =>
    `https://maps.google.com/maps?q=${encodeURIComponent(props.address)}&z=16&hl=ko&output=embed`,
)
</script>

<template>
  <iframe
    class="map-embed"
    :style="{ height }"
    :src="src"
    loading="lazy"
    referrerpolicy="no-referrer-when-downgrade"
    title="위치 지도"
  />
</template>

<style scoped>
.map-embed {
  width: 100%;
  border: 1px solid var(--border-soft);
  border-radius: 16px;
  display: block;
}
</style>
