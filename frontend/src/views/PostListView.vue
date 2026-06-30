<script setup>
import { onMounted, reactive } from 'vue'

import Pagination from '@/components/Pagination.vue'
import PostCard from '@/components/PostCard.vue'
import { usePostStore } from '@/stores/post'

const store = usePostStore()

const search = reactive({
  search_type: store.query.search_type || 'title_content',
  keyword: store.query.keyword || '',
  sort: store.query.sort || 'latest',
})

function applySearch() {
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
        <input
          v-model="search.keyword"
          class="input"
          placeholder="검색어를 입력하세요"
          @keyup.enter="applySearch"
        />
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
