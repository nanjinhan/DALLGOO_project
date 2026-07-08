<script setup>
import { onMounted, onUnmounted, ref } from 'vue'

import ImageSlot from '@/components/company/ImageSlot.vue'
import MapEmbed from '@/components/company/MapEmbed.vue'
import WelcomePopup from '@/components/WelcomePopup.vue'

// 상단 스크롤 진행률 표시줄(Scroll Progress Bar)
const progress = ref(0)
function onScroll() {
  const max = document.documentElement.scrollHeight - window.innerHeight
  progress.value = max > 0 ? Math.min(100, (window.scrollY / max) * 100) : 0
}

// 스크롤 등장 애니메이션 — 뷰포트에 들어오면 위로 떠오르고, 나가면 리셋(다시 들어오면 재생)
const root = ref(null)
let io = null

onMounted(() => {
  window.addEventListener('scroll', onScroll, { passive: true })
  onScroll()

  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  if (reduce || !root.value) return

  const selector =
    '.lp-eyebrow, .lp-h1, .lp-h2, .lp-lead, .lp-badge, .lp-actions, ' +
    '.lp-links-row, .stats, .phone, .dash, .ai-card, .trio-card, ' +
    '.outing-img, .svc, .info, .why'
  const els = root.value.querySelectorAll(selector)
  els.forEach((el) => el.classList.add('reveal'))

  io = new IntersectionObserver(
    (entries) => {
      // 들어오면 add, 나가면 remove → 스크롤할 때마다 다시 애니메이션
      entries.forEach((e) => {
        e.target.classList.toggle('reveal-in', e.isIntersecting)
      })
    },
    { threshold: 0.15, rootMargin: '0px 0px -12% 0px' },
  )
  els.forEach((el) => io.observe(el))
})

onUnmounted(() => {
  window.removeEventListener('scroll', onScroll)
  io && io.disconnect()
})

const dataCards = [
  {
    icon: '🩺',
    title: '생체 신호',
    desc: 'ECG·SpO₂·혈압을 시계열로 축적해 악화 예측 모델의 기반을 만듭니다.',
  },
  {
    icon: '👁',
    title: '현장 영상',
    desc: 'Vision AI가 처치 행위를 인식해 정형 데이터로 라벨링합니다.',
  },
  {
    icon: '📑',
    title: '의료 기록',
    desc: '구급활동일지를 표준 스키마로 통합해 연구 환경에 안전하게 제공합니다.',
  },
]

const services = [
  {
    no: '01',
    tag: '공정 배차',
    icon: '🚑',
    title: '구급차 호출 & 배차',
    desc: '앱으로 가장 가까운 구급차를 호출하고, 투명한 기준으로 배차합니다. 모든 배차 이력과 상태 정보가 체계적으로 기록되어 현장의 효율과 신뢰를 높입니다.',
  },
  {
    no: '02',
    tag: '관제',
    icon: '💓',
    title: '실시간 생체정보 모니터링',
    desc: '이송 중 심박·산소포화도·혈압을 실시간으로 의료진과 병원에 공유합니다. 도착 전에 준비를 시작해 골든타임을 지킵니다.',
  },
  {
    no: '03',
    tag: 'AI',
    icon: '✦',
    title: 'Vision AI 기반 의료기록 자동화',
    desc: '현장 영상과 음성을 인식해 구급활동일지를 자동 작성하고, 멀티모달 데이터로 정제해 연구·고도화에 활용합니다. 재고관리까지 한 흐름으로 묶습니다.',
  },
]

const companyInfo = [
  ['대표자', '박시은'],
  ['설립일', '2024년 8월 20일'],
  ['본사', '광주광역시 북구 치촌마을길 1-6 (인공지능 산업융합 사업단 512호)'],
  ['업종', '소프트웨어 개발·공급 · 앰뷸런스 서비스업'],
  ['규모', '중소기업 · 임직원 약 10~12명'],
  ['분류', '벤처기업 · 특허 보유 · 딥테크 초기창업패키지 선정'],
]

// 오시는 길 — 두 곳(본사 / 이송본부) 탭
const locations = [
  {
    key: 'hq',
    label: '본사',
    address: '광주광역시 북구 치촌마을길 1-6',
    detail: '인공지능 산업융합 사업단 512호',
    transit: [
      { ic: '🚌', k: '버스정류장', v: '인공지능융합사업단 인근 정류장 하차' },
      { ic: '🚗', k: '자가용', v: '건물 내 주차장 이용 가능 (방문 시 주차 지원)' },
    ],
  },
  {
    key: 'transport',
    label: '이송본부',
    address: '광주광역시 동구 남문로 600',
    detail: '2층',
    transit: [
      { ic: '🚇', k: '지하철 역', v: '소태역(광주 도시철도 1호선) 1번 출구 도보 2분' },
      { ic: '🚌', k: '버스정류장', v: '소태역시외버스정류소 (남문로 575)' },
    ],
  },
]
const activeLoc = ref('hq')
</script>

<template>
  <div class="lp" ref="root">
    <!-- 입장 팝업 (오늘 하루 보지 않기 / 닫기) -->
    <WelcomePopup />

    <!-- 스크롤 진행률 표시줄 -->
    <div class="scroll-progress" :style="{ width: progress + '%' }" />

    <main id="top">
      <!-- ===== 히어로 ===== -->
      <section class="lp-section hero">
        <div class="lp-container lp-center">
          <p class="lp-eyebrow">달구</p>
          <h1 class="lp-h1">응급의료의<br />미래를 잇다</h1>
          <p class="lp-lead">
            공정 배차부터 AI 의료기록 자동화까지.<br />
            구급차를 데이터가 흐르는 응급의료 플랫폼으로 다시 설계합니다.
          </p>
          <div class="lp-actions lp-mt-m">
            <a href="#service" class="lp-btn lp-btn--primary">더 알아보기 ›</a>
            <a href="#partner" class="lp-btn lp-btn--ghost">도입 문의 ›</a>
          </div>
        </div>
        <div class="lp-container lp-container--wide lp-mt-l">
          <ImageSlot
            video="/images/hero.mp4"
            src="/images/hero.jpg"
            ratio="21 / 9"
            label="구급차 / 현장 히어로 (영상 또는 사진)"
            hint="(21:9)"
            path="public/images/hero.mp4 또는 hero.jpg"
          />
        </div>
      </section>

      <!-- ===== 비전 / 통계 (다크) ===== -->
      <section id="mission" class="lp-section lp-section--dark lp-center">
        <div class="lp-container">
          <span class="lp-badge">민간 최초 · AI 구급차 운영</span>
          <h2 class="lp-h2 lp-mt-m">차량이 아니라,<br />응급의료의 표준을 만듭니다</h2>
          <p class="lp-lead">
            병원·공공기관·민간업체와 함께 긴급이송의 새로운 기준을 설계하는<br />
            광주 기반 응급의료 플랫폼 기업, 달구입니다.
          </p>
          <div class="lp-links-row lp-mt-m">
            <a href="#company" class="lp-link">달구의 비전 알아보기</a>
          </div>

          <div class="stats">
            <div class="stat">
              <div class="stat-num">2024</div>
              <div class="stat-label">설립 · 광주광역시 동구</div>
            </div>
            <div class="stat">
              <div class="stat-num">3축</div>
              <div class="stat-label">배차 · 모니터링 · AI 기록</div>
            </div>
            <div class="stat">
              <div class="stat-num">딥테크</div>
              <div class="stat-label">초기창업패키지 선정 · 벤처기업</div>
            </div>
          </div>
        </div>
      </section>

      <!-- ===== 회사소개 ===== -->
      <section id="company" class="lp-section lp-center">
        <div class="lp-container lp-head">
          <p class="lp-eyebrow">회사소개</p>
          <h2 class="lp-h2">주식회사 달구</h2>
          <p class="lp-lead" style="margin: 0 auto">
            광주 기반의 응급의료·구급차 플랫폼 기업. 응급이송 서비스를 디지털로
            다시 설계합니다.
          </p>
        </div>

        <div class="lp-container">
          <div class="lp-card info">
            <div v-for="row in companyInfo" :key="row[0]" class="info-row">
              <div class="info-k">{{ row[0] }}</div>
              <div class="info-v">{{ row[1] }}</div>
            </div>
          </div>

          <div class="why">
            <h3 class="lp-h3">왜 달구인가</h3>
            <p>
              응급의료는 지역 편차, 정보 비대칭, 기록의 단절, 배차의 비효율이
              생기기 쉬운 영역입니다. 달구는 이를 앱과 데이터로 다시 설계합니다.
              IT를 덧씌우는 수준이 아니라, 서비스 설계 자체를 새로 짭니다.
            </p>
            <p>
              지금까지 얼마를 벌었는지보다, 응급의료 시장에서 어떤 표준을 만들 수
              있는지가 더 중요한 회사입니다. 가능성과 과제가 동시에 큰, 응급의료
              디지털 전환의 실험입니다.
            </p>
            <div class="lp-links-row lp-mt-m">
              <a href="#service" class="lp-link">서비스 살펴보기</a>
            </div>
          </div>
        </div>
      </section>

      <!-- ===== 사회공헌 / 치료적 외출 (분할) ===== -->
      <section id="csr" class="lp-section lp-section--soft">
        <div class="lp-container lp-container--wide outing">
          <div class="outing-text">
            <p class="lp-eyebrow">사회공헌 · 치료적 외출</p>
            <h2 class="lp-h2">병상 밖에도,<br />일상이 있어야 합니다</h2>
            <p class="lp-lead">
              장기 입원 환자가 잠시 세상과 다시 만날 수 있도록. 달구는 이송
              서비스를 사회적 가치와 잇습니다.
            </p>
            <div class="lp-links-row lp-mt-m">
              <a href="#partner" class="lp-link">치료적 외출 이야기</a>
            </div>
          </div>
          <div class="outing-img">
            <ImageSlot
              video="/images/outing.mp4"
              src="/images/outing.jpg"
              ratio="4 / 3"
              label="치료적 외출 (영상 또는 사진)"
              path="public/images/outing.mp4 또는 outing.jpg"
            />
          </div>
        </div>
      </section>

      <!-- ===== 오시는 길 ===== -->
      <section id="location" class="lp-section lp-center">
        <div class="lp-container lp-head">
          <p class="lp-eyebrow">오시는 길</p>
          <h2 class="lp-h2">달구를 만나러 오세요</h2>
        </div>

        <div class="lp-container">
          <!-- 위치 탭 -->
          <div class="loc-tabs">
            <button
              v-for="l in locations"
              :key="l.key"
              class="loc-tab"
              :class="{ on: activeLoc === l.key }"
              @click="activeLoc = l.key"
            >
              {{ l.label }}
            </button>
          </div>

          <template v-for="l in locations" :key="l.key">
            <div v-if="activeLoc === l.key" class="loc-panel">
              <h3 class="loc-name">{{ l.label }}</h3>
              <p class="loc-addr">{{ l.address }}, {{ l.detail }}</p>

              <MapEmbed :address="l.address" height="360px" style="margin: 14px 0" />

              <div class="loc-ways">
                <div v-for="w in l.transit" :key="w.k" class="loc-way">
                  <div class="loc-way-h">{{ w.ic }} {{ w.k }}</div>
                  <div class="loc-way-v">{{ w.v }}</div>
                </div>
              </div>

              <div class="lp-links-row lp-mt-m" style="justify-content: center">
                <a
                  class="lp-link"
                  :href="`https://map.kakao.com/link/search/${l.address}`"
                  target="_blank"
                  rel="noopener"
                >
                  카카오맵에서 크게 보기 ›
                </a>
              </div>
            </div>
          </template>
        </div>
      </section>

      <!-- ===== 1. 구급차 호출 (아이폰 목업) ===== -->
      <section id="service" class="lp-section lp-center">
        <div class="lp-container lp-head">
          <h2 class="lp-h2">구급차 호출, 더 빠르고 공정하게</h2>
          <p class="lp-lead">
            전화 한 통이 아니라 앱 한 번으로. 가장 가까운 구급차를 투명한 기준으로
            배차하고, 모든 이력을 기록으로 남깁니다.
          </p>
          <div class="lp-links-row">
            <a href="#service" class="lp-link">앱 알아보기</a>
            <a href="#service" class="lp-link">배차 기준 보기</a>
          </div>
        </div>

        <div class="phone">
          <div class="phone-notch" />
          <div class="phone-screen">
            <div class="ph-status">
              <span>9:41</span>
              <span class="ph-status-r">●●● ▮</span>
            </div>
            <div class="ph-head">
              <div class="ph-loc">광주광역시 동구 남문로</div>
              <div class="ph-title">구급차 호출</div>
            </div>
            <div class="ph-map">
              <svg class="ph-map-svg" viewBox="0 0 280 250" preserveAspectRatio="xMidYMid slice">
                <!-- 도로 (반듯한 격자) -->
                <g stroke="#dee1e6" stroke-linecap="round">
                  <line x1="-10" y1="86" x2="290" y2="86" stroke-width="20" />
                  <line x1="-10" y1="182" x2="290" y2="182" stroke-width="15" />
                  <line x1="64" y1="-10" x2="64" y2="260" stroke-width="14" />
                  <line x1="188" y1="-10" x2="188" y2="260" stroke-width="17" />
                </g>
                <!-- 경로 (도로를 따라 깔끔하게) -->
                <polyline
                  points="64,206 64,86 188,86"
                  fill="none"
                  stroke="#0071e3"
                  stroke-width="4"
                  stroke-dasharray="0.1 10"
                  stroke-linecap="round"
                />
                <!-- 출발 지점 -->
                <circle cx="64" cy="206" r="7" fill="#0071e3" stroke="#fff" stroke-width="3.5" />
                <!-- 구급차 -->
                <circle cx="188" cy="86" r="20" fill="#fff" class="amb-bubble" />
                <text x="188" y="93" font-size="20" text-anchor="middle">🚑</text>
              </svg>
            </div>
            <div class="ph-card">
              <div class="ph-card-top">
                <span class="ph-card-label">가장 가까운 구급차</span>
                <span class="ph-card-tag">공정배차 매칭</span>
              </div>
              <div class="ph-eta"><b>4분</b> 예상 도착 · 2.1km</div>
              <button class="ph-confirm">배차 확정</button>
            </div>
          </div>
        </div>
      </section>

      <!-- ===== 2. 실시간 모니터링 (대시보드) ===== -->
      <section id="monitoring" class="lp-section lp-section--soft lp-center">
        <div class="lp-container lp-head">
          <h2 class="lp-h2">이송 중에도, 환자 곁을 지킵니다</h2>
          <p class="lp-lead">
            실시간 생체정보 모니터링으로 심박·산소포화도·혈압을 의료진과 병원이
            동시에 확인합니다. 도착 전에 준비가 시작됩니다.
          </p>
          <div class="lp-links-row">
            <a href="#service" class="lp-link">관제 시스템 알아보기</a>
          </div>
        </div>

        <div class="lp-container lp-container--wide">
          <div class="dash">
            <div class="dash-head">
              <span class="dash-live"><i /> 실시간 관제 · 광주 12-가</span>
              <span class="dash-eta">병원 인계까지 04:12</span>
            </div>
            <div class="dash-grid">
              <div class="vital vital--wide">
                <div class="vital-k">심전도 · ECG</div>
                <div class="ecg-wrap">
                  <svg class="ecg" viewBox="0 0 240 60" preserveAspectRatio="none">
                    <g class="ecg-track">
                      <path class="ecg-line" d="M0,30 H28 L33,30 L38,23 L43,30 L52,30 L57,33 L61,9 L65,40 L69,30 L80,24 L92,30 H120" />
                      <path class="ecg-line" transform="translate(120,0)" d="M0,30 H28 L33,30 L38,23 L43,30 L52,30 L57,33 L61,9 L65,40 L69,30 L80,24 L92,30 H120" />
                      <path class="ecg-line" transform="translate(240,0)" d="M0,30 H28 L33,30 L38,23 L43,30 L52,30 L57,33 L61,9 L65,40 L69,30 L80,24 L92,30 H120" />
                    </g>
                  </svg>
                </div>
              </div>
              <div class="vital">
                <div class="vital-k">심박수</div>
                <div class="vital-v"><b>92</b><span>bpm</span></div>
              </div>
              <div class="vital">
                <div class="vital-k">산소포화도</div>
                <div class="vital-v"><b class="blue">97</b><span>%</span></div>
              </div>
              <div class="vital">
                <div class="vital-k">혈압</div>
                <div class="vital-v sm">128/82</div>
              </div>
              <div class="vital">
                <div class="vital-k">호흡수</div>
                <div class="vital-v sm">18</div>
              </div>
              <div class="vital">
                <div class="vital-k">체온</div>
                <div class="vital-v sm">36.8°</div>
              </div>
              <div class="vital">
                <div class="vital-k">의식</div>
                <div class="vital-v sm green">A</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ===== Vision AI (다크) ===== -->
      <section id="ai-record" class="lp-section lp-section--dark lp-center">
        <div class="lp-container lp-head">
          <p class="lp-eyebrow">Vision AI</p>
          <h2 class="lp-h2">구급활동, AI가 기록합니다</h2>
          <p class="lp-lead">
            현장 영상과 음성을 인식해 구급활동일지를 자동으로 작성합니다. 대원은
            처치에, 기록은 AI에 맡깁니다.
          </p>
          <div class="lp-links-row">
            <a href="#data" class="lp-link">자동기록 기술 보기</a>
          </div>
        </div>

        <div class="lp-container">
          <div class="ai-card">
            <div class="ai-top">
              <span class="ai-title">구급활동일지 · 자동 생성</span>
              <span class="ai-badge">✦ AI 자동기록</span>
            </div>
            <div class="ai-grid">
              <div><div class="ai-k">발생 시각</div><div class="ai-v">14:23 · 동구 소태동</div></div>
              <div><div class="ai-k">주요 증상</div><div class="ai-v">흉통 · 호흡곤란</div></div>
              <div><div class="ai-k">현장 처치</div><div class="ai-v">산소 공급 · ECG 부착</div></div>
              <div><div class="ai-k">이송 병원</div><div class="ai-v">조선대학교병원</div></div>
            </div>
            <div class="ai-summary">
              <b>AI 요약</b> · 50대 남성, 흉통 호소. 산소포화도 97% 유지, ECG
              정상동율동. 안정 상태로 전문의 인계 권고.
            </div>
          </div>
        </div>
      </section>

      <!-- ===== 데이터 (3 카드) ===== -->
      <section id="data" class="lp-section lp-center">
        <div class="lp-container lp-head">
          <h2 class="lp-h2">데이터가 다음 환자를 살립니다</h2>
          <p class="lp-lead">
            구급차에서 모인 생체·영상·기록을 멀티모달 커스텀 데이터로 정제해,
            응급의료 연구와 기술 고도화를 지원합니다.
          </p>
          <div class="lp-links-row">
            <a href="#partner" class="lp-link">연구·데이터 협력</a>
          </div>
        </div>

        <div class="lp-container lp-container--wide">
          <div class="trio">
            <div v-for="c in dataCards" :key="c.title" class="lp-card trio-card">
              <div class="trio-ic">{{ c.icon }}</div>
              <h3 class="lp-h3">{{ c.title }}</h3>
              <p class="trio-desc">{{ c.desc }}</p>
            </div>
          </div>
        </div>
      </section>

      <!-- ===== 파트너 CTA ===== -->
      <section id="partner" class="lp-section lp-center">
        <div class="lp-container">
          <h2 class="lp-h2">응급의료의 표준, 함께 만드시겠어요?</h2>
          <p class="lp-lead">병원·공공기관·민간업체 파트너십을 기다립니다.</p>
          <div class="lp-actions lp-mt-m">
            <a href="#partner" class="lp-btn lp-btn--primary">도입 문의 ›</a>
            <a href="#company" class="lp-btn lp-btn--ghost">회사 알아보기 ›</a>
          </div>
        </div>
      </section>

      <!-- ===== 서비스 3축 상세 ===== -->
      <section id="pillars" class="lp-section lp-section--soft">
        <div class="lp-container lp-center lp-head">
          <p class="lp-eyebrow">서비스</p>
          <h2 class="lp-h2">하나의 플랫폼, 세 개의 축</h2>
          <p class="lp-lead" style="margin: 0 auto">
            호출과 배차, 실시간 모니터링, AI 기록까지. 달구는 응급이송의 전 과정을
            하나로 잇습니다.
          </p>
        </div>

        <div class="lp-container lp-container--wide svc-list">
          <div v-for="s in services" :key="s.no" class="lp-card svc">
            <div class="svc-ic">{{ s.icon }}</div>
            <div class="svc-body">
              <div class="svc-tag">{{ s.no }} · {{ s.tag }}</div>
              <h3 class="lp-h3">{{ s.title }}</h3>
              <p class="svc-desc">{{ s.desc }}</p>
            </div>
          </div>
        </div>
      </section>

      <!-- ===== 다크 전환 ===== -->
      <section class="lp-section lp-section--dark lp-section--tight lp-center">
        <div class="lp-container">
          <h2 class="lp-h2">소프트웨어와 구급차, 하나의 회사에서</h2>
          <p class="lp-lead">
            소프트웨어만 만드는 곳도, 차량만 운영하는 곳도 아닙니다. 달구는 현장과
            데이터를 동시에 책임지는 도메인 특화형 기술기업입니다.
          </p>
          <div class="lp-actions lp-mt-m">
            <a href="#top" class="lp-btn lp-btn--primary">홈으로 ›</a>
          </div>
        </div>
      </section>

    </main>
  </div>
</template>

<style scoped>
/* 섹션 앵커가 sticky 네비에 가리지 않도록 */
.lp :deep(section[id]),
.lp main {
  scroll-margin-top: 70px;
}
#top {
  scroll-margin-top: 0;
}

/* ===== 히어로 ===== */
.hero {
  padding-top: clamp(70px, 9vw, 110px);
  padding-bottom: clamp(48px, 7vw, 80px);
}

/* ===== 통계 ===== */
.stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  margin-top: 64px;
  border-top: 1px solid rgba(255, 255, 255, 0.12);
  padding-top: 44px;
}
.stat + .stat {
  border-left: 1px solid rgba(255, 255, 255, 0.12);
}
.stat-num {
  font-size: clamp(34px, 5vw, 56px);
  font-weight: 800;
  letter-spacing: -0.03em;
  line-height: 1;
}
.stat-label {
  margin-top: 12px;
  font-size: 14px;
  color: #a1a1a6;
}

/* ===== 아이폰 목업 ===== */
.phone {
  width: 310px;
  margin: 8px auto 0;
  background: #0b0b0d;
  border-radius: 46px;
  padding: 11px;
  box-shadow: 0 30px 60px -20px rgba(0, 0, 0, 0.35);
  position: relative;
}
.phone-notch {
  position: absolute;
  top: 11px;
  left: 50%;
  transform: translateX(-50%);
  width: 110px;
  height: 24px;
  background: #0b0b0d;
  border-radius: 0 0 16px 16px;
  z-index: 3;
}
.phone-screen {
  background: #fff;
  border-radius: 36px;
  overflow: hidden;
  text-align: left;
}
.ph-status {
  display: flex;
  justify-content: space-between;
  padding: 12px 22px 4px;
  font-size: 13px;
  font-weight: 600;
}
.ph-status-r {
  letter-spacing: 1px;
  font-size: 11px;
}
.ph-head {
  padding: 8px 22px 12px;
}
.ph-loc {
  font-size: 12px;
  color: var(--c-text-3);
}
.ph-title {
  font-size: 22px;
  font-weight: 800;
  letter-spacing: -0.02em;
}
.ph-map {
  position: relative;
  height: 250px;
  background: #eef0f3;
  overflow: hidden;
}
.ph-map-svg {
  display: block;
  width: 100%;
  height: 100%;
}
.amb-bubble {
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.18));
}
.ph-card {
  padding: 16px 20px 20px;
}
.ph-card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.ph-card-label {
  font-size: 15px;
  font-weight: 700;
}
.ph-card-tag {
  font-size: 11px;
  color: var(--c-text-3);
}
.ph-eta {
  margin: 6px 0 14px;
  font-size: 14px;
  color: var(--c-text-2);
}
.ph-eta b {
  font-size: 26px;
  color: var(--c-primary);
  margin-right: 4px;
  letter-spacing: -0.02em;
}
.ph-confirm {
  width: 100%;
  padding: 14px;
  border: none;
  border-radius: 14px;
  background: var(--c-primary);
  color: #fff;
  font-size: 15px;
  font-weight: 700;
}

/* ===== 관제 대시보드 ===== */
.dash {
  background: #fff;
  border-radius: var(--r-lg);
  padding: 26px;
  box-shadow: 0 10px 40px -16px rgba(0, 0, 0, 0.12);
  text-align: left;
}
.dash-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px;
}
.dash-live {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 700;
  font-size: 15px;
}
.dash-live i {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--c-green);
  box-shadow: 0 0 0 4px rgba(52, 199, 89, 0.18);
}
.dash-eta {
  font-size: 13px;
  color: var(--c-text-3);
}
.dash-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}
.vital {
  background: var(--c-bg-soft);
  border-radius: 14px;
  padding: 16px;
}
.vital--wide {
  grid-column: span 2;
  grid-row: span 1;
}
.vital-k {
  font-size: 12px;
  color: var(--c-text-3);
  margin-bottom: 10px;
}
.vital-v {
  display: flex;
  align-items: baseline;
  gap: 4px;
}
.vital-v b {
  font-size: 30px;
  font-weight: 800;
  letter-spacing: -0.02em;
}
.vital-v span {
  font-size: 13px;
  color: var(--c-text-3);
}
.vital-v.sm {
  font-size: 22px;
  font-weight: 800;
}
.vital-v .blue {
  color: var(--c-primary);
}
.vital-v.green {
  color: var(--c-green);
}
.ecg-wrap {
  width: 100%;
  height: 48px;
  overflow: hidden;
}
.ecg {
  width: 100%;
  height: 100%;
}
.ecg-line {
  fill: none;
  stroke: #ff3b30;
  stroke-width: 2;
  stroke-linejoin: round;
  stroke-linecap: round;
  vector-effect: non-scaling-stroke;
}
/* 파형이 왼쪽으로 흐르며 실시간 모니터처럼 움직임 */
.ecg-track {
  animation: ecg-scroll 2.4s linear infinite;
  will-change: transform;
}
@keyframes ecg-scroll {
  from {
    transform: translateX(0);
  }
  to {
    transform: translateX(-120px);
  }
}
@media (prefers-reduced-motion: reduce) {
  .ecg-track {
    animation: none;
  }
}

/* ===== AI 카드 ===== */
.ai-card {
  background: #fff;
  color: var(--c-text);
  border-radius: var(--r-lg);
  padding: 26px 28px;
  text-align: left;
  max-width: 720px;
  margin: 0 auto;
  box-shadow: 0 20px 60px -20px rgba(0, 0, 0, 0.5);
}
.ai-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--c-line-soft);
}
.ai-title {
  font-weight: 700;
  font-size: 16px;
}
.ai-badge {
  font-size: 12px;
  font-weight: 700;
  color: var(--c-primary);
  background: rgba(0, 113, 227, 0.1);
  padding: 6px 12px;
  border-radius: 980px;
}
.ai-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px 24px;
  padding: 18px 0;
}
.ai-k {
  font-size: 12px;
  color: var(--c-text-3);
  margin-bottom: 4px;
}
.ai-v {
  font-size: 15px;
  font-weight: 600;
}
.ai-summary {
  background: var(--c-bg-soft);
  border-radius: 12px;
  padding: 14px 16px;
  font-size: 13.5px;
  color: var(--c-text-2);
  line-height: 1.5;
}
.ai-summary b {
  color: var(--c-primary);
}

/* ===== 데이터 3 카드 ===== */
.trio {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 18px;
  text-align: left;
}
.trio-ic {
  font-size: 28px;
  margin-bottom: 14px;
}
.trio-desc {
  font-size: 14.5px;
  color: var(--c-text-2);
  line-height: 1.55;
  margin: 0;
}

/* ===== 사회공헌 분할 ===== */
.outing {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 48px;
  align-items: center;
}
.outing-text {
  text-align: left;
}

/* ===== 서비스 상세 카드 ===== */
.svc-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.svc {
  display: flex;
  gap: 24px;
  align-items: flex-start;
  text-align: left;
}
.svc-ic {
  font-size: 30px;
  flex-shrink: 0;
  width: 52px;
  height: 52px;
  display: grid;
  place-items: center;
  background: var(--c-bg-soft);
  border-radius: 16px;
}
.svc-tag {
  font-size: 13px;
  font-weight: 700;
  color: var(--c-text-3);
  margin-bottom: 6px;
}
.svc-desc {
  font-size: 15px;
  color: var(--c-text-2);
  line-height: 1.6;
  margin: 0;
}

/* ===== 회사 정보 테이블 ===== */
.info {
  text-align: left;
  padding: 10px 30px;
}
.info-row {
  display: grid;
  grid-template-columns: 140px 1fr;
  padding: 18px 0;
  border-bottom: 1px solid var(--c-line-soft);
}
.info-row:last-child {
  border-bottom: none;
}
.info-k {
  color: var(--c-text-3);
  font-size: 15px;
}
.info-v {
  font-weight: 600;
  font-size: 15px;
}
.why {
  max-width: 760px;
  margin: 56px auto 0;
  text-align: center;
}
.why p {
  font-size: clamp(15px, 1.9vw, 18px);
  line-height: 1.7;
  color: var(--c-text-2);
  margin: 0 0 16px;
}

/* ===== 스크롤 진행률 표시줄 ===== */
.scroll-progress {
  position: fixed;
  top: 0;
  left: 0;
  height: 3px;
  width: 0;
  background: linear-gradient(90deg, var(--c-primary), #2997ff);
  z-index: 200;
  transition: width 0.08s linear;
}

/* ===== 스크롤 등장 애니메이션 ===== */
.reveal {
  opacity: 0;
  transform: translateY(26px);
  transition:
    opacity 0.6s cubic-bezier(0.22, 0.61, 0.36, 1),
    transform 0.6s cubic-bezier(0.22, 0.61, 0.36, 1);
  will-change: opacity, transform;
}
.reveal-in {
  opacity: 1;
  transform: none;
}
/* 같은 행 카드들은 살짝 시차를 두고 */
.trio-card.reveal:nth-child(2) {
  transition-delay: 0.08s;
}
.trio-card.reveal:nth-child(3) {
  transition-delay: 0.16s;
}
.svc-list .svc.reveal:nth-child(2) {
  transition-delay: 0.07s;
}
.svc-list .svc.reveal:nth-child(3) {
  transition-delay: 0.14s;
}

/* ===== 반응형 ===== */
@media (max-width: 820px) {
  .nav-menu {
    display: none;
  }
  .dash-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .vital--wide {
    grid-column: span 2;
  }
  .trio,
  .outing,
  .foot-cols {
    grid-template-columns: 1fr;
  }
  .ai-grid {
    grid-template-columns: 1fr;
  }
  .stats {
    grid-template-columns: 1fr;
    gap: 28px;
  }
  .stat + .stat {
    border-left: none;
    border-top: 1px solid rgba(255, 255, 255, 0.12);
    padding-top: 28px;
  }
}

/* ===== 오시는 길 — 위치 탭 ===== */
.loc-tabs {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-bottom: 22px;
}
.loc-tab {
  padding: 9px 24px;
  border: none;
  border-radius: 999px;
  background: var(--hover);
  font-size: 15px;
  font-weight: 700;
  color: var(--muted);
  transition: 0.15s;
}
.loc-tab.on {
  background: var(--primary);
  color: #fff;
}
.loc-panel {
  text-align: left;
}
.loc-name {
  font-size: 18px;
  font-weight: 800;
  margin: 0 0 6px;
}
.loc-addr {
  color: var(--muted);
  font-size: 14.5px;
  margin: 0;
}
.loc-ways {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
.loc-way {
  background: var(--bg);
  border-radius: 12px;
  padding: 14px 16px;
}
.loc-way-h {
  font-size: 14px;
  font-weight: 700;
  margin-bottom: 6px;
}
.loc-way-v {
  font-size: 13.5px;
  color: var(--muted);
  line-height: 1.5;
}
@media (max-width: 620px) {
  .loc-ways {
    grid-template-columns: 1fr;
  }
}
</style>
