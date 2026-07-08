<script setup>
import { onMounted, reactive, ref } from 'vue'
import { RouterLink } from 'vue-router'

import Pagination from '@/components/Pagination.vue'
import { transportApi } from '@/api/transport'
import { useAuthStore } from '@/stores/auth'
import { errorMessage, formatDate } from '@/utils/format'

const auth = useAuthStore()

const items = ref([])
const page = ref(1)
const totalPages = ref(0)
const total = ref(0)
const loading = ref(true)
const error = ref('')

const FILTERS = [
  { key: 'all', label: '전체' },
  { key: 'title', label: '제목' },
  { key: 'hospital', label: '병원' },
  { key: 'author', label: '작성자' },
]
const search = reactive({ type: 'all', keyword: '' })

async function load(p = 1) {
  loading.value = true
  error.value = ''
  try {
    const params = { page: p, size: 12 }
    if (search.keyword.trim()) {
      params.keyword = search.keyword.trim()
      params.search_type = search.type
    }
    const { data } = await transportApi.list(params)
    items.value = data.items
    page.value = data.page
    total.value = data.total
    totalPages.value = data.total_pages
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    loading.value = false
  }
}

function reset() {
  search.type = 'all'
  search.keyword = ''
  load(1)
}

onMounted(() => load(1))
</script>

<template>
  <div class="tr-list">
    <div class="tr-top">
      <div>
        <h2>이송 기록</h2>
        <p class="muted">안전하고 신뢰할 수 있는 달구의 이송 서비스 기록입니다.</p>
      </div>
      <RouterLink
        v-if="auth.isAdmin"
        :to="{ name: 'transport-create' }"
        class="btn btn-primary"
      >
        + 새 이송기록
      </RouterLink>
    </div>

    <!-- 검색 -->
    <div class="tr-search card">
      <div class="filters">
        <button
          v-for="f in FILTERS"
          :key="f.key"
          class="filter-pill"
          :class="{ on: search.type === f.key }"
          @click="search.type = f.key"
        >
          {{ f.label }}
        </button>
      </div>
      <input
        v-model="search.keyword"
        class="input"
        placeholder="검색어 입력"
        @keyup.enter="load(1)"
      />
      <button class="btn btn-dark" @click="load(1)">검색</button>
      <button class="btn" @click="reset">초기화</button>
    </div>

    <div v-if="loading" class="muted center">불러오는 중…</div>
    <p v-else-if="error" class="error-text center">{{ error }}</p>
    <div v-else-if="!items.length" class="muted center">이송 기록이 없습니다.</div>

    <div v-else class="tr-grid">
      <RouterLink
        v-for="r in items"
        :key="r.id"
        :to="{ name: 'transport-detail', params: { id: r.id } }"
        class="tr-card"
      >
        <div class="tr-thumb">
          <img v-if="r.has_image" :src="transportApi.imageUrl(r.id)" alt="이송 사진" />
          <div v-else class="tr-thumb-empty">🚑</div>
        </div>
        <div class="tr-body">
          <div class="tr-title">{{ r.title }}</div>
          <div class="tr-route">
            {{ r.from_hospital }} <span class="arrow">→</span> {{ r.to_hospital }}
          </div>
          <div class="tr-meta">
            <span>{{ r.author }}</span>
            <span class="dot">·</span>
            <span>👁 {{ r.view_count }}</span>
            <span class="spacer" />
            <span>{{ formatDate(r.created_at) }}</span>
          </div>
        </div>
      </RouterLink>
    </div>

    <Pagination :page="page" :total-pages="totalPages" @change="load" />
  </div>
</template>

<style scoped>
.tr-top {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}
.tr-top h2 {
  margin: 0 0 4px;
}
.tr-search {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  margin-bottom: 20px;
}
.filters {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
}
.filter-pill {
  padding: 8px 13px;
  border: none;
  border-radius: 8px;
  background: transparent;
  font-size: 13.5px;
  font-weight: 600;
  color: var(--muted);
}
.filter-pill.on {
  background: var(--text);
  color: var(--card);
}
.tr-search .input {
  flex: 1;
  min-width: 0;
}
.btn-dark {
  background: var(--text);
  border-color: var(--text);
  color: var(--card);
}
.tr-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}
.tr-card {
  display: block;
  background: var(--card);
  border: 1px solid var(--border-soft);
  border-radius: 14px;
  overflow: hidden;
  transition: 0.16s;
}
.tr-card:hover {
  border-color: var(--primary);
  box-shadow: 0 6px 20px -6px rgba(0, 113, 227, 0.2);
  transform: translateY(-2px);
}
.tr-thumb {
  aspect-ratio: 4 / 3;
  background: var(--hover);
  overflow: hidden;
}
.tr-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.tr-thumb-empty {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40px;
  opacity: 0.4;
}
.tr-body {
  padding: 13px 14px 15px;
}
.tr-title {
  font-size: 15px;
  font-weight: 700;
  margin-bottom: 6px;
}
.tr-route {
  font-size: 13px;
  color: var(--primary);
  font-weight: 600;
  margin-bottom: 8px;
  line-height: 1.4;
}
.arrow {
  color: var(--muted);
}
.tr-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12.5px;
  color: var(--muted);
}
.center {
  text-align: center;
  padding: 40px 0;
}
@media (max-width: 900px) {
  .tr-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
@media (max-width: 520px) {
  .tr-grid {
    grid-template-columns: 1fr;
  }
  .tr-search {
    flex-wrap: wrap;
  }
}
</style>
