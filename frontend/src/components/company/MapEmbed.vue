<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'

const props = defineProps({
  address: { type: String, required: true },
  height: { type: String, default: '360px' },
})

// 구글 지도 임베드 — API 키·도메인 등록·심사 불필요(누구나 바로 표시)
const src = computed(
  () =>
    `https://maps.google.com/maps?q=${encodeURIComponent(props.address)}&z=16&hl=ko&output=embed`,
)

// 화면에 들어올 때만 iframe 로딩 → 초기 새로고침 시 스크롤 튐 방지
const wrap = ref(null)
const visible = ref(false)
let io = null

onMounted(() => {
  io = new IntersectionObserver(
    (entries) => {
      if (entries.some((e) => e.isIntersecting)) {
        visible.value = true
        io.disconnect()
      }
    },
    { rootMargin: '150px' },
  )
  if (wrap.value) io.observe(wrap.value)
})
onUnmounted(() => io && io.disconnect())
</script>

<template>
  <div ref="wrap" class="map-wrap" :style="{ height }">
    <iframe
      v-if="visible"
      class="map-embed"
      :style="{ height }"
      :src="src"
      loading="lazy"
      referrerpolicy="no-referrer-when-downgrade"
      title="위치 지도"
    />
    <div v-else class="map-ph">지도를 불러오는 중…</div>
  </div>
</template>

<style scoped>
.map-wrap {
  width: 100%;
}
.map-embed {
  width: 100%;
  border: 1px solid var(--border-soft);
  border-radius: 16px;
  display: block;
}
.map-ph {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--hover);
  border: 1px solid var(--border-soft);
  border-radius: 16px;
  color: var(--muted);
  font-size: 14px;
}
</style>
