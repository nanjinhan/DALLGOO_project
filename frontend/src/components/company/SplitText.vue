<script setup>
import { computed, onMounted, ref } from 'vue'

/**
 * 글자 단위로 순차 등장하는 제목.
 * 페이지 진입 즉시 재생하므로 히어로처럼 첫 화면에 있는 문구에 쓴다.
 * (스크롤해서 만나는 문구는 기존 .reveal 을 그대로 쓰면 된다.)
 */
const props = defineProps({
  text: { type: String, required: true }, // 줄바꿈은 \n
  tag: { type: String, default: 'h1' },
  delay: { type: Number, default: 60 }, // 시작 지연(ms)
  stagger: { type: Number, default: 26 }, // 글자 간 간격(ms)
})

// 줄 단위로 자르고, 각 줄을 글자 배열로. (이모지 대응해 스프레드 사용)
const lines = computed(() => props.text.split('\n').map((line) => [...line]))

// 줄이 바뀌어도 지연이 이어지도록 앞 줄들의 글자 수를 누적한다.
const lineOffsets = computed(() => {
  let sum = 0
  return lines.value.map((line) => {
    const start = sum
    sum += line.length
    return start
  })
})

const shown = ref(false)

onMounted(() => {
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  if (reduce) {
    shown.value = true // 모션 최소화 설정이면 애니메이션 없이 바로 표시
    return
  }
  // 첫 페인트 이후에 클래스를 붙여야 transition이 실제로 재생된다.
  requestAnimationFrame(() => {
    shown.value = true
  })
})
</script>

<template>
  <component :is="tag" class="split-text" :class="{ 'split-in': shown }">
    <span v-for="(line, li) in lines" :key="li" class="split-line">
      <span
        v-for="(ch, ci) in line"
        :key="ci"
        class="split-char"
        :style="{
          transitionDelay: `${delay + (lineOffsets[li] + ci) * stagger}ms`,
        }"
        >{{ ch === ' ' ? ' ' : ch }}</span
      >
    </span>
  </component>
</template>

<style scoped>
.split-line {
  display: block;
}
.split-char {
  display: inline-block;
  opacity: 0;
  transform: translateY(0.38em);
  transition:
    opacity 0.55s cubic-bezier(0.22, 0.61, 0.36, 1),
    transform 0.55s cubic-bezier(0.22, 0.61, 0.36, 1);
  will-change: opacity, transform;
}
.split-in .split-char {
  opacity: 1;
  transform: none;
}

@media (prefers-reduced-motion: reduce) {
  .split-char {
    opacity: 1;
    transform: none;
    transition: none;
  }
}
</style>
