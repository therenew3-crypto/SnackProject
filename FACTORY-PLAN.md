# 🏭 스낵 서비스 공장 — 개발 구조 계획서

| 항목 | 내용 |
|---|---|
| 작성일 | 2026-06-29 |
| 목적 | 바이럴 스낵 웹앱을 빠르게 양산하되, 늘어나도 관리 용이 + 서비스 간 시너지 |
| 확정 선택 | ① 브랜드 도메인 + **서브패스** · ② **Supabase 처음부터 포함** |

---

## 1. 권장 스택

| 레이어 | 선택 | 이유 |
|---|---|---|
| 프레임워크 | **Next.js (App Router)** | 정적+서버리스 하이브리드, 결과별 **동적 OG 썸네일**, API 라우트 |
| 호스팅 | **Vercel** | Next.js 안정성, 다수 도메인/리라이트 관리 쉬움 (Netlify `--prod` 이슈 회피) |
| DB/백엔드 | **Supabase** (Postgres) | 리더보드·제출·전환 저장, 기존 사용 경험 |
| 데이터 | **Python 파이프라인 + GitHub Actions(cron)** | 시세 갱신을 배포와 분리 |
| 분석 | **GA4 (+ 이벤트 스키마 통일)** | 앱별 유입·전환 비교, A/B |

> 시작은 **단일 Next.js 앱**(서브패스 라우트). 앱이 무거워지면 **Turborepo + pnpm 멀티패키지**로 승격.

## 2. 디렉터리 구조 (단일 앱, 서브패스)

```
playmoney/
  app/
    page.tsx                    # 허브 랜딩 (/) — 모든 미니앱 목록 + 교차 프로모
    ggeolmusae/page.tsx         # /ggeolmusae  (기존 껄무새 이전)
    hogu/page.tsx               # /hogu         (호구판독기)
    api/og/[app]/route.tsx      # 결과별 동적 OG 이미지
    api/data/route.ts           # 시세/계산 서버함수
    sitemap.ts  robots.ts       # SEO 자동 생성
  components/                   # 공통 UI: ResultCard, AmountSlider, AdSlot, CtaButton, ShareButton, Modal
  lib/
    ads.ts        # AdFit/AdSense 단위 config + 인터스티셜 + 노필 폴백
    share.ts      # 카톡 공유 + 결과 인코딩 URL
    og.tsx        # OG 템플릿
    analytics.ts  # GA4 이벤트 래퍼
    seo.ts        # 메타/구조화데이터 헬퍼
    supabase.ts   # 클라이언트
  data/           # 시세 JSON (cron 산출물)
  scripts/        # fetch_*.py (시세 수집)
  supabase/       # 마이그레이션(SQL): scores, submissions, events
```

신규 앱 추가 = `app/<name>/` 한 폴더 + 고유 계산로직 + 카피. 나머지는 공통 모듈 재사용.

## 3. 도메인/시너지 전략

- **브랜드 도메인 1개 + 서브패스**: `brand.kr/ggeolmusae`, `brand.kr/hogu`
- **허브 랜딩**(`/`): 미니앱 카탈로그 + 인기/신규 배지
- **교차 프로모 위젯**: 각 결과 화면 하단 "다음 테스트 →" 1~2개 추천 (트래픽 순환)
- 효과: 도메인 권위 누적(SEO↑) · 체류/재방문↑ · 광고 노출↑ (복리)

## 4. 데이터 레이어

- 정적 스냅샷(껄무새)보다 시계열이 필요한 앱(호구판독기) 대비
- 파이프라인: `Python 수집 → GitHub Actions cron → data/*.json (또는 Supabase) → 앱이 읽음`
- 배포와 데이터 갱신 분리 → 시세만 바뀌어도 재배포 불필요

## 5. 수익화 레이어

- 공통 **AdSlot 컴포넌트**(앱별 단위코드 config) — AdFit/AdSense
- **금융 제휴 CTA 컴포넌트**: "지금이라도 시작 / 포모 탈출" → 증권사 계좌개설·리밸런싱 CPA
- CTA 공통화 → 앱 전체 A/B 테스트 일괄 적용, 전환은 `events` 테이블로 추적

## 6. 로드맵

- **Phase 0 — 공장 셋업**: Next.js 앱 생성 + Supabase 연결 + 껄무새 이전 → 공통 컴포넌트/lib 추출 → 템플릿 확정
- **Phase 1 — 호구판독기**: 템플릿 위에 2호점 (양산 속도 검증)
- **Phase 2 — 시너지**: 허브 + 교차 프로모 + 통합 GA4
- **Phase 3 — 고도화**: 데이터 cron 자동화 + 제휴 A/B 최적화

## 7. 호구판독기 설계 스케치

- 입력: 종목 · 평단 · 수량 → 현재가 대비 **손실%·호구지수**
- **구조대 확률**: 역사적으로 −X% 구간 진입 후 본전 회복 비율 + 소요기간(중앙값/최악치)
- **리더보드**(Supabase): "당신은 상위 N% 호구" → 공유 유도

## 8. 껄무새 → 공장 이전 메모

- 현재 껄무새는 단일 HTML(Netlify). Phase 0에서 `app/ggeolmusae/`로 이전
- 광고/공유/OG/순위/멘트 로직을 `lib`·`components`로 추출하며 첫 템플릿화
