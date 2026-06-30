<script setup>
import { RouterLink } from 'vue-router'

const home = (hash) => ({ name: 'home', hash })
</script>

<template>
  <footer class="gfoot">
    <div class="gfoot-inner">
      <div class="gfoot-cols">
        <div class="gfoot-col">
          <div class="gfoot-h">서비스</div>
          <RouterLink :to="home('#service')">구급차 호출</RouterLink>
          <RouterLink :to="home('#service')">공정 배차</RouterLink>
          <RouterLink :to="home('#service')">실시간 관제</RouterLink>
          <RouterLink :to="home('#service')">AI 의료기록</RouterLink>
        </div>
        <div class="gfoot-col">
          <div class="gfoot-h">연구·데이터</div>
          <RouterLink :to="home('#data')">멀티모달 데이터</RouterLink>
          <RouterLink :to="home('#data')">R&D 협력</RouterLink>
          <RouterLink :to="home('#data')">Vision AI</RouterLink>
          <RouterLink :to="home('#data')">생체정보 관제</RouterLink>
        </div>
        <div class="gfoot-col">
          <div class="gfoot-h">회사</div>
          <RouterLink :to="home('#company')">회사소개</RouterLink>
          <RouterLink :to="home('#partner')">치료적 외출</RouterLink>
          <RouterLink :to="home('#partner')">파트너십</RouterLink>
          <RouterLink :to="home('#partner')">채용</RouterLink>
        </div>
        <div class="gfoot-col">
          <div class="gfoot-h">고객지원</div>
          <RouterLink :to="{ name: 'posts' }">게시판</RouterLink>
          <RouterLink :to="home('#partner')">도입 문의</RouterLink>
          <span>광주광역시 동구</span>
          <span>남문로 600</span>
        </div>
      </div>
      <div class="gfoot-legal">
        <div>주식회사 달구 · 대표 박시은 · 광주광역시 동구 남문로 600(소태동)</div>
        <div>
          Copyright © 2026 Dalgoo Inc. 모든 권리 보유. · 민간 최초 AI 구급차 운영
          기업
        </div>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.gfoot {
  background: var(--bg);
  border-top: 1px solid var(--border);
  padding: 56px 0 40px;
  font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, 'Segoe UI',
    sans-serif;
}
.gfoot-inner {
  max-width: 1120px;
  margin: 0 auto;
  padding: 0 22px;
}
.gfoot-cols {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
  padding-bottom: 36px;
}
.gfoot-col {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.gfoot-h {
  font-weight: 700;
  margin-bottom: 4px;
  font-size: 14px;
  color: var(--text);
}
.gfoot-col a,
.gfoot-col span {
  color: var(--muted);
  font-size: 13.5px;
}
.gfoot-col a:hover {
  color: var(--primary);
}
.gfoot-legal {
  border-top: 1px solid var(--border);
  padding-top: 22px;
  color: var(--muted);
  font-size: 12.5px;
  line-height: 1.7;
}

@media (max-width: 760px) {
  .gfoot-cols {
    grid-template-columns: 1fr 1fr;
  }
}
</style>
