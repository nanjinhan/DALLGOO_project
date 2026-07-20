<script setup>
import { onMounted, onUnmounted, ref } from 'vue'

/**
 * 화면에 들어오면 0부터 목표 숫자까지 올라가는 통계 숫자.
 * '2024' 처럼 순수 숫자, '3축' 처럼 숫자+단위 모두 받는다.
 * '딥테크' 처럼 숫자로 시작하지 않으면 애니메이션 없이 그대로 보여준다.
 */
const props = defineProps({
  value: { type: String, required: true },
  duration: { type: Number, default: 1500 },
})

// 앞쪽 숫자만 세고 뒤에 붙은 글자는 고정.
const parsed = props.value.match(/^(\d+)(.*)$/)
const target = parsed ? Number(parsed[1]) : null
const suffix = parsed ? parsed[2] : ''

const display = ref(target === null ? props.value : `0${suffix}`)
const el = ref(null)
let io = null
let raf = 0

function animate() {
  const start = performance.now()
  const step = (now) => {
    const p = Math.min(1, (now - start) / props.duration)
    const eased = 1 - Math.pow(1 - p, 3) // easeOutCubic — 끝에서 부드럽게 감속
    display.value = `${Math.round(target * eased)}${suffix}`
    if (p < 1) raf = requestAnimationFrame(step)
  }
  raf = requestAnimationFrame(step)
}

onMounted(() => {
  if (target === null) return // 숫자가 아니면 할 일 없음

  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  if (reduce) {
    display.value = props.value
    return
  }

  // 스크롤로 들어왔을 때 시작. 한 번 재생하면 관찰을 끊는다.
  io = new IntersectionObserver(
    (entries) => {
      if (entries.some((e) => e.isIntersecting)) {
        io.disconnect()
        io = null
        animate()
      }
    },
    { threshold: 0.4 },
  )
  io.observe(el.value)
})

onUnmounted(() => {
  io?.disconnect()
  cancelAnimationFrame(raf)
})
</script>

<template>
  <span ref="el">{{ display }}</span>
</template>
