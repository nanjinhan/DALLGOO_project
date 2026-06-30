<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  // public/ 기준 경로. 파일이 있으면 자동 표시.
  video: { type: String, default: '' }, // 동영상(있으면 우선, 자동재생·무한반복·음소거)
  src: { type: String, default: '' }, // 이미지(동영상 없을 때 / 포스터로 사용)
  ratio: { type: String, default: '16 / 9' },
  label: { type: String, default: '이미지' },
  hint: { type: String, default: '' }, // 예: (21:9)
  path: { type: String, default: '' }, // 권장 저장 경로 안내
  rounded: { type: Boolean, default: true },
})

const videoFailed = ref(false)
const imgFailed = ref(false)

const showVideo = computed(() => props.video && !videoFailed.value)
const showImg = computed(
  () => !showVideo.value && props.src && !imgFailed.value,
)
</script>

<template>
  <div class="img-slot" :class="{ rounded }" :style="{ aspectRatio: ratio }">
    <video
      v-if="showVideo"
      :src="video"
      :poster="src || undefined"
      class="media-real"
      autoplay
      muted
      loop
      playsinline
      @error="videoFailed = true"
    />
    <img
      v-else-if="showImg"
      :src="src"
      :alt="label"
      class="media-real"
      @error="imgFailed = true"
    />
    <div v-else class="img-empty">
      <div class="img-ic">
        <svg width="34" height="34" viewBox="0 0 24 24" fill="none">
          <rect x="3" y="4" width="18" height="16" rx="2.5" stroke="currentColor" stroke-width="1.6" />
          <circle cx="8.5" cy="9.5" r="1.7" stroke="currentColor" stroke-width="1.5" />
          <path d="M4 17l4.5-4.5 3.5 3.5 3-3L20 16.5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" />
        </svg>
      </div>
      <div class="img-label">
        {{ label }} <span v-if="hint" class="img-hint">{{ hint }}</span>
      </div>
      <div v-if="path" class="img-path">권장 경로: {{ path }}</div>
      <div class="img-browse">이미지 또는 동영상(mp4)을 넣어주세요</div>
    </div>
  </div>
</template>

<style scoped>
.img-slot {
  width: 100%;
  overflow: hidden;
  background: #f0f0f3;
}
.img-slot.rounded {
  border-radius: 22px;
}
.media-real {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.img-empty {
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
.img-ic {
  color: #b0b0b8;
  margin-bottom: 2px;
}
.img-label {
  font-size: 14px;
  font-weight: 600;
  color: #6e6e73;
  max-width: 80%;
  line-height: 1.4;
}
.img-hint {
  color: #a1a1a6;
  font-weight: 500;
}
.img-path {
  font-size: 12px;
  color: #a1a1a6;
  font-family: 'SF Mono', ui-monospace, monospace;
}
.img-browse {
  font-size: 12.5px;
  color: #a1a1a6;
}
</style>
