<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  // 유튜브 주소 또는 영상 ID. 넣으면 mp4보다 우선한다.
  youtube: { type: String, default: '' },
  // public/ 기준 경로. 파일이 있으면 자동 표시.
  src: { type: String, default: '' }, // 영상(mp4) — 소리 켜고 끝까지 보는 용도
  poster: { type: String, default: '' }, // 표지 이미지 (선택, 유튜브는 자동 썸네일)
  ratio: { type: String, default: '16 / 9' },
  label: { type: String, default: '소개 영상' },
  path: { type: String, default: '' }, // 권장 저장 경로 안내
  tone: { type: String, default: 'light' }, // light | dark — 배경 섹션에 맞춘 placeholder 색
})

const videoEl = ref(null)
const failed = ref(false)
const started = ref(false)

// watch?v= / youtu.be / embed / shorts / 그냥 ID 전부 허용
const ytId = computed(() => {
  const raw = props.youtube.trim()
  if (!raw) return ''
  const m = raw.match(
    /(?:youtu\.be\/|v=|\/embed\/|\/shorts\/|\/live\/)([A-Za-z0-9_-]{11})/,
  )
  if (m) return m[1]
  return /^[A-Za-z0-9_-]{11}$/.test(raw) ? raw : ''
})

// 유튜브 자동 썸네일 — maxres가 없는 영상은 hq로 폴백
const thumbLevel = ref('maxresdefault')
const ytThumb = computed(
  () => `https://i.ytimg.com/vi/${ytId.value}/${thumbLevel.value}.jpg`,
)
function onThumbError() {
  if (thumbLevel.value === 'maxresdefault') thumbLevel.value = 'hqdefault'
}

// 클릭 전에는 iframe을 만들지 않는다 — 유튜브 스크립트를 미리 받지 않아 랜딩이 가벼워짐
const ytEmbed = computed(
  () =>
    `https://www.youtube-nocookie.com/embed/${ytId.value}` +
    '?autoplay=1&rel=0&modestbranding=1&playsinline=1',
)

const coverImage = computed(() =>
  ytId.value ? props.poster || ytThumb.value : props.poster,
)
const available = computed(() => (ytId.value || props.src) && !failed.value)

// 표지를 누른 순간부터 재생 — 히어로 배경영상과 달리 소리가 나오고 반복하지 않는다.
function play() {
  started.value = true
  if (!ytId.value) videoEl.value?.play()
}
</script>

<template>
  <div
    class="video-slot"
    :class="`tone-${tone}`"
    :style="{ aspectRatio: ratio }"
  >
    <template v-if="available">
      <!-- 유튜브: 클릭 후에만 iframe 삽입 -->
      <iframe
        v-if="ytId && started"
        :src="ytEmbed"
        :title="label"
        class="video-real"
        frameborder="0"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
        referrerpolicy="strict-origin-when-cross-origin"
        allowfullscreen
      />
      <!-- mp4 직접 재생 -->
      <video
        v-else-if="!ytId"
        ref="videoEl"
        :src="src"
        :poster="poster || undefined"
        class="video-real"
        controls
        controlslist="nodownload"
        playsinline
        preload="metadata"
        @error="failed = true"
        @play="started = true"
        @ended="started = false"
      />
      <button
        v-if="!started"
        type="button"
        class="video-cover"
        :aria-label="`${label} 재생`"
        @click="play"
      >
        <img
          v-if="coverImage"
          :src="coverImage"
          alt=""
          class="video-thumb"
          @error="onThumbError"
        />
        <span class="video-play">
          <svg width="26" height="26" viewBox="0 0 24 24" fill="currentColor">
            <path d="M8 5.5v13l11-6.5-11-6.5z" />
          </svg>
        </span>
        <span class="video-cta">{{ label }} 재생</span>
      </button>
    </template>

    <div v-else class="video-empty">
      <div class="video-ic">
        <svg width="34" height="34" viewBox="0 0 24 24" fill="none">
          <rect x="3" y="5" width="18" height="14" rx="2.5" stroke="currentColor" stroke-width="1.6" />
          <path d="M10 9.5v5l4.5-2.5-4.5-2.5z" fill="currentColor" />
        </svg>
      </div>
      <div class="video-label">{{ label }}</div>
      <div v-if="path" class="video-path">권장 경로: {{ path }}</div>
      <div class="video-browse">유튜브 주소 또는 mp4 파일을 넣어주세요</div>
    </div>
  </div>
</template>

<style scoped>
.video-slot {
  position: relative;
  width: 100%;
  overflow: hidden;
  border-radius: 22px;
  background: #000;
}
.video-real {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

/* 표지 — 첫 재생 전까지 컨트롤 위를 덮는다 */
.video-cover {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 14px;
  border: 0;
  padding: 0;
  cursor: pointer;
  color: #fff;
  background: transparent;
}
/* 썸네일 위에 덮는 어두운 막 — 재생 버튼 가독성 확보 */
.video-cover::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(
    180deg,
    rgba(0, 0, 0, 0.15) 0%,
    rgba(0, 0, 0, 0.45) 100%
  );
  transition: background 0.3s ease;
}
.video-cover:hover::after {
  background: linear-gradient(
    180deg,
    rgba(0, 0, 0, 0.25) 0%,
    rgba(0, 0, 0, 0.55) 100%
  );
}
.video-thumb {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.video-play,
.video-cta {
  position: relative;
  z-index: 1;
}
.video-play {
  width: 74px;
  height: 74px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.18);
  border: 1.5px solid rgba(255, 255, 255, 0.7);
  backdrop-filter: saturate(180%) blur(12px);
  -webkit-backdrop-filter: saturate(180%) blur(12px);
  padding-left: 4px;
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1), background 0.3s ease;
}
.video-cover:hover .video-play {
  transform: scale(1.08);
  background: rgba(255, 255, 255, 0.28);
}
.video-cta {
  font-size: 15px;
  font-weight: 600;
  letter-spacing: -0.01em;
  text-shadow: 0 1px 12px rgba(0, 0, 0, 0.4);
}

/* 파일이 아직 없을 때 */
.video-empty {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 7px;
  border: 1.5px dashed #c7c7cf;
  border-radius: inherit;
  background: #f5f5f7;
  color: #86868b;
  text-align: center;
  padding: 20px;
}
.tone-dark .video-empty {
  border-color: rgba(255, 255, 255, 0.24);
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.62);
}
.video-ic {
  color: #b0b0b8;
  margin-bottom: 2px;
}
.tone-dark .video-ic {
  color: rgba(255, 255, 255, 0.45);
}
.video-label {
  font-size: 14px;
  font-weight: 600;
  color: #6e6e73;
  line-height: 1.4;
}
.tone-dark .video-label {
  color: rgba(255, 255, 255, 0.8);
}
.video-path {
  font-size: 12px;
  color: #a1a1a6;
  font-family: 'SF Mono', ui-monospace, monospace;
}
.video-browse {
  font-size: 12.5px;
  color: #a1a1a6;
}

@media (max-width: 640px) {
  .video-play {
    width: 60px;
    height: 60px;
  }
  .video-cta {
    font-size: 13.5px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .video-cover::after,
  .video-play {
    transition: none;
  }
  .video-cover:hover .video-play {
    transform: none;
  }
}
</style>
