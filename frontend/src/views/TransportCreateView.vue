<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

import { transportApi } from '@/api/transport'
import { useToast } from '@/composables/useToast'
import { errorMessage } from '@/utils/format'

const router = useRouter()
const toast = useToast()

const form = ref({
  patient_name: '',
  from_hospital: '',
  to_hospital: '',
  distance_km: 0,
  duration_min: 0,
  crew: '',
  detail: '',
  guardian_name: '',
})
const image = ref(null)
const busy = ref(false)
const error = ref('')

function onFile(e) {
  image.value = e.target.files[0] || null
}

async function submit() {
  error.value = ''
  if (!form.value.patient_name.trim() || !form.value.from_hospital.trim() || !form.value.to_hospital.trim()) {
    error.value = '환자 이름과 출발/도착 병원은 필수입니다.'
    return
  }
  busy.value = true
  try {
    const fd = new FormData()
    Object.entries(form.value).forEach(([k, v]) => fd.append(k, v))
    if (image.value) fd.append('image', image.value)
    const { data } = await transportApi.create(fd)
    toast.success('이송 기록이 등록되었습니다.')
    if (data.guardian_code) {
      alert(
        `보호자 인증 코드가 생성되었습니다.\n\n보호자: ${data.guardian_name || '(미지정)'}\n인증 코드: ${data.guardian_code}\n\n이 코드를 보호자에게 문자로 전달하세요. (상세 페이지에서 다시 확인 가능)`,
      )
    }
    router.push({ name: 'transport-detail', params: { id: data.id } })
  } catch (e) {
    error.value = errorMessage(e, '등록에 실패했습니다.')
    toast.error(error.value)
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <div class="card">
    <h2>새 이송 기록</h2>
    <p class="muted" style="margin-bottom: 18px">
      환자 이름은 목록·상세에서 자동으로 마스킹(***)되어 표시됩니다.
    </p>

    <div class="field">
      <label>대표 사진</label>
      <input type="file" accept="image/*" class="input" @change="onFile" />
    </div>

    <div class="field">
      <label>환자 이름 <span class="req">*</span></label>
      <input v-model="form.patient_name" class="input" placeholder="예: 홍길동 (마스킹되어 표시됨)" />
    </div>

    <div class="grid2">
      <div class="field">
        <label>출발 병원 <span class="req">*</span></label>
        <input v-model="form.from_hospital" class="input" placeholder="예: 광주한국병원" />
      </div>
      <div class="field">
        <label>도착 병원 <span class="req">*</span></label>
        <input v-model="form.to_hospital" class="input" placeholder="예: 전남대학교병원" />
      </div>
    </div>

    <div class="grid2">
      <div class="field">
        <label>이송 거리 (km)</label>
        <input v-model.number="form.distance_km" type="number" min="0" class="input" />
      </div>
      <div class="field">
        <label>소요 시간 (분)</label>
        <input v-model.number="form.duration_min" type="number" min="0" class="input" />
      </div>
    </div>

    <div class="field">
      <label>출동 크루원 (쉼표로 구분)</label>
      <input v-model="form.crew" class="input" placeholder="예: 박영수, 이민호" />
    </div>

    <div class="field">
      <label>보호자 이름 (인증용)</label>
      <input v-model="form.guardian_name" class="input" placeholder="예: 홍보호 (등록 시 인증코드 자동 생성)" />
      <p class="hint">보호자는 이 이름 + 자동 생성된 인증코드로 상세정보를 확인하고 댓글을 남길 수 있어요.</p>
    </div>

    <div class="field">
      <label>이송 상세 내용 (보호자 인증 후 공개)</label>
      <textarea v-model="form.detail" class="textarea" placeholder="이송 경과, 처치 내용 등" />
    </div>

    <p v-if="error" class="error-text">{{ error }}</p>
    <div class="row">
      <button class="btn" @click="router.back()">취소</button>
      <span class="spacer" />
      <button class="btn btn-primary" :disabled="busy" @click="submit">등록</button>
    </div>
  </div>
</template>

<style scoped>
h2 {
  margin: 0 0 6px;
}
.grid2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
.req {
  color: var(--danger);
}
.hint {
  margin: 6px 0 0;
  font-size: 12.5px;
  color: var(--muted);
}
@media (max-width: 560px) {
  .grid2 {
    grid-template-columns: 1fr;
  }
}
</style>
