import { defineStore } from 'pinia'
import { ref } from 'vue'

import { postApi } from '@/api/post'

export const usePostStore = defineStore('post', () => {
  const items = ref([])
  const page = ref(1)
  const size = ref(10)
  const total = ref(0)
  const totalPages = ref(0)
  const loading = ref(false)

  // 목록 조회 조건 (목록 ↔ 상세 왕복 시 유지)
  const query = ref({
    page: 1,
    size: 10,
    sort: 'latest',
    search_type: 'title_content',
    keyword: '',
  })

  async function fetchList(overrides = {}) {
    loading.value = true
    query.value = { ...query.value, ...overrides }
    try {
      const params = { ...query.value }
      if (!params.keyword) {
        delete params.keyword
        delete params.search_type
      }
      const { data } = await postApi.list(params)
      items.value = data.items
      page.value = data.page
      size.value = data.size
      total.value = data.total
      totalPages.value = data.total_pages
    } finally {
      loading.value = false
    }
  }

  return {
    items,
    page,
    size,
    total,
    totalPages,
    loading,
    query,
    fetchList,
  }
})
