# 🔧 모듈별 상세 문서

## 코어 모듈 목록 (17개)

---

## 1. crawler/ - 트렌드 수집

### tiktok_crawler.py
**목적:** TikTok Creative Center에서 트렌딩 해시태그 수집

**클래스:**
- `TikTokCrawler`: Playwright 기반 크롤러

**주요 메서드:**
| 메서드 | 설명 | 반환 |
|--------|------|------|
| `get_trending_hashtags()` | 트렌딩 해시태그 수집 | List[Dict] |
| `_setup_browser()` | 브라우저 초기화 | None |

**사용 예:**
```python
crawler = TikTokCrawler()
trends = await crawler.get_trending_hashtags(region="KR", limit=20)
```

### google_trends_crawler.py
**목적:** Google Trends API 연동

**클래스:**
- `GoogleTrendsCrawler`: pytrends 래퍼

**주요 메서드:**
| 메서드 | 설명 |
|--------|------|
| `get_interest_over_time()` | 키워드 검색량 |
| `get_related_queries()` | 관련 검색어 |
| `get_realtime_trends()` | 실시간 트렌드 |

---

## 2. gdd_generator/ - GDD 생성

### gdd_generator.py
**목적:** LLM 기반 게임 기획 문서 생성

**클래스:**
- `GDDGenerator`: GDD 생성 엔진
- `GDD`: GDD 데이터 클래스

**주요 메서드:**
| 메서드 | 설명 |
|--------|------|
| `generate_from_trends()` | 트렌드 기반 GDD 생성 |
| `validate_gdd()` | GDD 스키마 검증 |
| `save_gdd()` | JSON 저장 |

### multilingual_gdd.py
**목적:** 다국어 GDD 생성

**지원 언어:** ko-KR, en-US, ja-JP, zh-CN 등 10개

---

## 3. asset_pipeline/ - 자산 생성

### asset_generator.py
**목적:** Stability AI 연동 이미지 생성

**클래스:**
- `AssetGenerator`: 이미지 생성기
- `GeneratedAsset`: 생성 결과

**주요 메서드:**
| 메서드 | 설명 |
|--------|------|
| `generate_sprite()` | 스프라이트 생성 |
| `generate_spritesheet()` | 스프라이트시트 생성 |
| `generate_from_gdd()` | GDD 기반 일괄 생성 |

### screenshot_generator.py
**목적:** 스토어용 스크린샷 생성

**지원 스토어:** Google Play, App Store, Steam

---

## 4. builder/ - Godot 빌드

### godot_builder.py
**목적:** Godot 엔진 헤드리스 빌드

**지원 플랫폼:** Android, iOS, HTML5, Windows, macOS, Linux

**주요 메서드:**
| 메서드 | 설명 |
|--------|------|
| `build()` | 단일 플랫폼 빌드 |
| `build_all()` | 멀티 플랫폼 빌드 |
| `import_assets()` | 에셋 임포트 |

---

## 5. deployer/ - 스토어 배포

### store_uploader.py (Google Play)
- `GooglePlayUploader`: APK/AAB 업로드
- `AppStoreUploadManager`: 통합 매니저

### ios_uploader.py (App Store)
- `AppStoreConnectUploader`: IPA 업로드, 심사 제출

### steam_uploader.py (Steam)
- `SteamUploader`: steamcmd 연동
- `SteamworksBuildManager`: 빌드 관리

---

## 6. orchestrator/ - 워크플로우

### slack_notifier.py
**목적:** 슬랙 알림 및 승인 요청

**기능:**
- Block Kit 메시지
- HMAC 서명 검증
- 승인/거절 처리

---

## 7. analytics/ - 분석

### dashboard.py
**목적:** 게임 성과 추적

**클래스:**
- `AnalyticsDashboard`: 메인 대시보드
- `GameMetrics`: 게임별 지표

**추적 지표:**
- 게임 생성 수
- 빌드 성공률
- 자산 생성 현황
- 수익/다운로드

---

## 8. ab_testing/ - A/B 테스트

### ab_manager.py
**목적:** A/B 테스트 관리

**클래스:**
- `ABTestManager`: 테스트 관리
- `ABTest`: 테스트 정의
- `Variant`: 변형 정의

**기능:**
- 결정적 유저 할당 (해싱)
- 전환 추적
- 통계 분석

---

## 9. balancing/ - 밸런싱

### balance_manager.py
**목적:** 실시간 게임 파라미터 조정

**카테고리:**
- gameplay: 게임플레이 파라미터
- economy: 경제 파라미터
- difficulty: 난이도
- ads: 광고 설정

**기능:**
- 템플릿별 기본값
- 버전 관리
- GDScript 자동 생성

---

## 10. web/ - 웹 서버

### dashboard_server.py
**목적:** FastAPI 관리자 대시보드

**엔드포인트:**
- `GET /`: 메인 대시보드
- `GET /api/stats`: 통계
- `GET /api/games`: 게임 목록
- `POST /api/games`: 게임 생성
- `POST /api/builds`: 빌드 시작

### webhook_server.py
**목적:** Git 웹훅 처리

**엔드포인트:**
- `POST /webhook/github`: GitHub 이벤트
- `POST /webhook/gitlab`: GitLab 이벤트

---

## 11. monitoring/ - 모니터링

### metrics.py
**목적:** Prometheus 메트릭 수집

**메트릭:**
- `http_requests_total`: 요청 수
- `http_request_duration_seconds`: 응답 시간
- `games_created_total`: 게임 생성
- `builds_completed_total`: 빌드 완료

---

## 12. security/ - 보안

### auth.py
**목적:** 인증 및 보안

**기능:**
- JWT 토큰 생성/검증
- 비밀번호 해싱
- API 키 인증
- Rate Limiting

---

## 13. plugins/ - 플러그인

### plugin_manager.py
**목적:** 플러그인 시스템

**훅:**
- `pre_gdd_generate` / `post_gdd_generate`
- `pre_asset_generate` / `post_asset_generate`
- `pre_build` / `post_build`
- `pre_deploy` / `post_deploy`

---

## 14. cache/ - 캐싱

### cache_manager.py
**목적:** 캐싱 레이어

**구현:**
- `MemoryCache`: 메모리 캐시
- `RedisCache`: Redis 캐시

**기능:**
- TTL 지원
- 데코레이터 캐싱
- 통계

---

## 15. pipeline.py - 통합

**목적:** 전체 파이프라인 오케스트레이션

**흐름:**
1. 트렌드 수집
2. GDD 생성
3. 슬랙 승인 요청
4. 템플릿 복사
5. 자산 생성
6. 빌드
7. 배포
