<script setup>
import { onMounted, reactive, ref } from 'vue'

import Pagination from '@/components/Pagination.vue'
import PostCard from '@/components/PostCard.vue'
import { postApi } from '@/api/post'
import { usePostStore } from '@/stores/post'

const store = usePostStore()

const search = reactive({
  search_type: store.query.search_type || 'title_content',
  keyword: store.query.keyword || '',
  sort: store.query.sort || 'latest',
})

// --- 검색 자동완성 ---
const suggestions = ref([])
const showSuggest = ref(false)
let suggestTimer = null

function onKeywordInput() {
  clearTimeout(suggestTimer)
  const kw = search.keyword.trim()
  if (!kw) {
    suggestions.value = []
    showSuggest.value = false
    return
  }
  // 250ms 디바운스 — 타이핑 멈추면 한 번만 요청
  suggestTimer = setTimeout(async () => {
    try {
      const { data } = await postApi.suggest(kw)
      suggestions.value = data.suggestions || []
      showSuggest.value = suggestions.value.length > 0
    } catch {
      suggestions.value = []
      showSuggest.value = false
    }
  }, 250)
}

function pickSuggestion(text) {
  search.keyword = text
  showSuggest.value = false
  applySearch()
}

function hideSuggest() {
  // 클릭이 먼저 처리되도록 약간 지연
  setTimeout(() => (showSuggest.value = false), 150)
}

function applySearch() {
  showSuggest.value = false
  store.fetchList({
    page: 1,
    keyword: search.keyword,
    search_type: search.search_type,
    sort: search.sort,
  })
}

function changeSort() {
  store.fetchList({ page: 1, sort: search.sort })
}

function changePage(p) {
  store.fetchList({ page: p })
}

onMounted(() => {
  store.fetchList({
    page: 1,
    keyword: search.keyword,
    search_type: search.search_type,
    sort: search.sort,
  })
})
</script>

<template>
  <div class="list-view">
    <div class="toolbar">
      <div class="search-row">
        <select v-model="search.search_type" class="select narrow">
          <option value="title">제목</option>
          <option value="content">내용</option>
          <option value="title_content">제목+내용</option>
          <option value="author">작성자</option>
        </select>
        <div class="search-input-wrap">
          <input
            v-model="search.keyword"
            class="input"
            placeholder="검색어를 입력하세요"
            autocomplete="off"
            @input="onKeywordInput"
            @keyup.enter="applySearch"
            @focus="onKeywordInput"
            @blur="hideSuggest"
          />
          <ul v-if="showSuggest" class="suggest-list">
            <li
              v-for="(s, i) in suggestions"
              :key="i"
              @mousedown.prevent="pickSuggestion(s)"
            >
              🔍 {{ s }}
            </li>
          </ul>
        </div>
        <button class="btn btn-primary" @click="applySearch">검색</button>
      </div>
      <div class="sort-row">
        <span class="muted">총 {{ store.total }}건</span>
        <span class="spacer" />
        <select v-model="search.sort" class="select narrow" @change="changeSort">
          <option value="latest">최신순</option>
          <option value="oldest">오래된순</option>
          <option value="views">조회순</option>
          <option value="likes">좋아요순</option>
        </select>
      </div>
    </div>

    <div v-if="store.loading" class="muted center">불러오는 중…</div>
    <div v-else-if="!store.items.length" class="muted center empty">
      게시글이 없습니다.
    </div>
    <div v-else>
      <PostCard v-for="post in store.items" :key="post.id" :post="post" />
    </div>

    <Pagination
      :page="store.page"
      :total-pages="store.totalPages"
      @change="changePage"
    />
  </div>
</template>

<style scoped>
.toolbar {
  margin-bottom: 16px;
}
.search-row {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}
/* 입력칸은 늘고, 셀렉트·검색 버튼은 한 줄로 고정 */
.search-input-wrap {
  position: relative;
  flex: 1;
  min-width: 0;
}
.search-row .btn {
  flex-shrink: 0;
  white-space: nowrap;
}
/* 자동완성 드롭다운 */
.suggest-list {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  right: 0;
  z-index: 50;
  margin: 0;
  padding: 6px;
  list-style: none;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 12px;
  box-shadow: 0 8px 24px -8px rgba(0, 0, 0, 0.2);
  max-height: 280px;
  overflow-y: auto;
}
.suggest-list li {
  padding: 9px 12px;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.suggest-list li:hover {
  background: var(--hover);
  color: var(--primary);
}
.select.narrow {
  width: auto;
  min-width: 110px;
  flex-shrink: 0;
}
.sort-row {
  display: flex;
  align-items: center;
}
.center {
  text-align: center;
  padding: 40px 0;
}
</style>
