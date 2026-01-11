# 📚 초자동화 게임 개발 파이프라인 - 종합 문서

## 목차
1. [프로젝트 개요](#프로젝트-개요)
2. [시스템 아키텍처](#시스템-아키텍처)
3. [모듈 상세](#모듈-상세)
4. [템플릿 가이드](#템플릿-가이드)
5. [API 레퍼런스](#api-레퍼런스)
6. [배포 가이드](#배포-가이드)

---

## 프로젝트 개요

### 비전
**트렌드 수집 → GDD 생성 → 자산 생성 → Godot 빌드 → 스토어 배포**까지 완전 자동화된 하이퍼 캐주얼 게임 개발 파이프라인

### 핵심 특징
- 🔍 **자동 트렌드 분석**: TikTok, Google Trends 실시간 수집
- 🤖 **AI 기반 GDD 생성**: Gemini/GPT를 활용한 게임 기획 문서 자동 생성
- 🎨 **AI 이미지 생성**: Stability AI를 통한 게임 자산 자동 생성
- 🔨 **자동 빌드**: Godot 엔진 헤드리스 빌드
- 🚀 **멀티 스토어 배포**: Google Play, iOS App Store, Steam 자동 업로드
- 📊 **실시간 분석**: A/B 테스트, 밸런싱, 성과 추적

### 기술 스택
| 분류 | 기술 |
|------|------|
| 언어 | Python 3.10+ |
| 게임 엔진 | Godot 4.2 |
| 웹 프레임워크 | FastAPI |
| LLM | Gemini API |
| 이미지 생성 | Stability AI |
| 컨테이너 | Docker |
| 오케스트레이션 | n8n |

---

## 시스템 아키텍처

### 전체 흐름

```
┌─────────────────────────────────────────────────────────────────────┐
│                         데이터 수집 레이어                            │
├─────────────────────────────────────────────────────────────────────┤
│  TikTok Crawler  ──┐                                                │
│                    ├──▶  Trend Analyzer  ──▶  GDD Generator        │
│  Google Trends   ──┘                              │                 │
└───────────────────────────────────────────────────┼─────────────────┘
                                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         승인 레이어 (HITL)                           │
├─────────────────────────────────────────────────────────────────────┤
│  Slack Notifier  ◀──▶  n8n Workflow  ◀──▶  Human Approval          │
└───────────────────────────────────────────────────┼─────────────────┘
                                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         생성 레이어                                  │
├─────────────────────────────────────────────────────────────────────┤
│  Asset Generator (Stability AI)  ──▶  Template Engine  ──▶  Build  │
└───────────────────────────────────────────────────┼─────────────────┘
                                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         배포 레이어                                  │
├─────────────────────────────────────────────────────────────────────┤
│  Google Play  │  iOS App Store  │  Steam                           │
└───────────────────────────────────────────────────┼─────────────────┘
                                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         운영 레이어                                  │
├─────────────────────────────────────────────────────────────────────┤
│  Analytics  │  A/B Testing  │  Balancing  │  Monitoring            │
└─────────────────────────────────────────────────────────────────────┘
```

### 디렉토리 구조

```
game-pipeline/
├── core/                      # 코어 모듈 (17개)
│   ├── crawler/              # 트렌드 수집
│   │   ├── tiktok_crawler.py
│   │   └── google_trends_crawler.py
│   ├── gdd_generator/        # GDD 생성
│   │   ├── gdd_generator.py
│   │   └── multilingual_gdd.py
│   ├── asset_pipeline/       # 자산 생성
│   │   ├── asset_generator.py
│   │   └── screenshot_generator.py
│   ├── builder/              # Godot 빌드
│   │   └── godot_builder.py
│   ├── deployer/             # 스토어 배포
│   │   ├── store_uploader.py     (Google Play)
│   │   ├── ios_uploader.py       (App Store)
│   │   └── steam_uploader.py     (Steam)
│   ├── orchestrator/         # 워크플로우
│   │   └── slack_notifier.py
│   ├── analytics/            # 분석
│   │   └── dashboard.py
│   ├── ab_testing/           # A/B 테스트
│   │   └── ab_manager.py
│   ├── balancing/            # 밸런싱
│   │   └── balance_manager.py
│   ├── web/                  # 웹 서버
│   │   ├── dashboard_server.py
│   │   └── webhook_server.py
│   ├── monitoring/           # 모니터링
│   │   └── metrics.py
│   ├── security/             # 보안
│   │   └── auth.py
│   ├── plugins/              # 플러그인
│   │   └── plugin_manager.py
│   ├── cache/                # 캐싱
│   │   └── cache_manager.py
│   └── pipeline.py           # 통합 파이프라인
│
├── templates/                 # 게임 템플릿 (6종)
│   ├── _core/                # 공통 코어
│   ├── template_runner/      # 무한 러너
│   ├── template_puzzle/      # 물리 퍼즐
│   ├── template_clicker/     # 클리커
│   ├── template_match3/      # 매치3
│   ├── template_rhythm/      # 리듬 게임
│   └── template_idle/        # 방치형 RPG
│
├── config/                    # 설정
│   ├── project_config.json
│   ├── n8n_workflow_template.json
│   └── grafana_dashboard.json
│
├── schemas/                   # JSON 스키마
│   ├── gdd_schema.json
│   └── template_config_schema.json
│
├── docs/                      # 문서
│   ├── GUIDE.md
│   ├── ARCHITECTURE.md
│   ├── API.md
│   └── FULL_DOCUMENTATION.md
│
├── tests/                     # 테스트
│   ├── test_core.py
│   └── test_integration.py
│
├── cli.py                     # CLI 도구
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pyproject.toml
└── README.md
```

---

## 모듈 상세

### 1. 크롤러 (crawler/)

#### TikTokCrawler
TikTok Creative Center에서 트렌딩 해시태그 수집

```python
from core.crawler import TikTokCrawler

crawler = TikTokCrawler()
trends = await crawler.get_trending_hashtags(region="KR", limit=20)
# [{"hashtag": "#챌린지", "view_count": 1000000}, ...]
```

#### GoogleTrendsCrawler
Google Trends API를 통한 검색 트렌드 수집

```python
from core.crawler import GoogleTrendsCrawler

crawler = GoogleTrendsCrawler()
trends = crawler.get_realtime_trends(geo="KR")
```

---

### 2. GDD 생성기 (gdd_generator/)

#### GDDGenerator
LLM을 활용한 게임 기획 문서 자동 생성

```python
from core.gdd_generator import GDDGenerator

generator = GDDGenerator({"api_key": "..."})
gdd = generator.generate_from_trends(tiktok_trends, google_trends, "runner")
generator.save_gdd(gdd, "output/game_gdd.json")
```

#### MultilingualGDDGenerator
다국어 GDD 및 스토어 등록 정보 생성

```python
from core.gdd_generator.multilingual_gdd import MultilingualGDDGenerator

generator = MultilingualGDDGenerator({"target_locales": ["ko-KR", "en-US", "ja-JP"]})
multilingual = generator.generate_multilingual(base_gdd)
listings = generator.export_store_listings(multilingual)
```

---

### 3. 자산 파이프라인 (asset_pipeline/)

#### AssetGenerator
Stability AI를 통한 게임 자산 생성

```python
from core.asset_pipeline import AssetGenerator

generator = AssetGenerator({"api_key": "..."})
result = generator.generate_sprite("cute robot character", "output/robot.png")
```

#### ScreenshotGenerator
스토어용 스크린샷 자동 생성

```python
from core.asset_pipeline.screenshot_generator import ScreenshotGenerator

generator = ScreenshotGenerator()
assets = generator.generate_store_assets("game_001", "google_play")
```

---

### 4. 빌더 (builder/)

#### GodotBuilder
Godot 엔진 헤드리스 빌드

```python
from core.builder import GodotBuilder

builder = GodotBuilder({"godot_path": "godot"})
result = builder.build("project/path", "android", "builds/android")
```

---

### 5. 배포 (deployer/)

#### GooglePlayUploader
Google Play Console API 연동

```python
from core.deployer import GooglePlayUploader

uploader = GooglePlayUploader({"credentials_path": "..."})
version = uploader.upload_apk("com.example.game", "game.apk", "internal")
```

#### AppStoreConnectUploader
iOS App Store Connect API 연동

```python
from core.deployer.ios_uploader import AppStoreConnectUploader

uploader = AppStoreConnectUploader({...})
uploader.upload_ipa("game.ipa", "com.example.game")
```

#### SteamUploader
Steam steamcmd 연동

```python
from core.deployer.steam_uploader import SteamworksBuildManager

manager = SteamworksBuildManager({...})
result = manager.create_and_upload("1234567", "1234568", "builds/steam", "v1.0.0")
```

---

### 6. 분석 및 운영

#### AnalyticsDashboard
게임 성과 추적

```python
from core.analytics import AnalyticsDashboard

dashboard = AnalyticsDashboard()
dashboard.track_game_created("game_001", "My Game", "runner")
report = dashboard.generate_summary_report()
```

#### ABTestManager
A/B 테스트 관리

```python
from core.ab_testing import ABTestManager

manager = ABTestManager()
test = manager.create_test("Jump Height Test", "...", "game_001", variants)
variant = manager.assign_variant(test.test_id, "user_123")
```

#### BalanceManager
실시간 게임 밸런싱

```python
from core.balancing import BalanceManager

manager = BalanceManager()
config = manager.create_config("game_001", "runner")
manager.update_parameter(config.config_id, "gameplay", "jump_height", 500)
manager.publish_config(config.config_id)
```

---

## 템플릿 가이드

### 공통 구조

모든 템플릿은 다음 구조를 따릅니다:

```
template_xxx/
├── project.godot          # Godot 프로젝트 설정
├── template_config.json   # 템플릿 메타데이터
├── scenes/                # 씬 파일
│   ├── main.tscn
│   └── game.tscn
├── scripts/               # GDScript
│   ├── main.gd
│   └── game_manager.gd
└── skins/                 # 스킨 시스템
    └── default/
```

### 템플릿 유형

| 템플릿 | 설명 | 핵심 메카닉 |
|--------|------|-------------|
| runner | 무한 러너 | 점프, 장애물 회피 |
| puzzle | 물리 퍼즐 | 발사, 파괴 |
| clicker | 클리커 | 클릭, 업그레이드 |
| match3 | 매치3 | 스와이프, 매칭 |
| rhythm | 리듬 게임 | 노트, 판정 |
| idle | 방치형 RPG | 자동 전투, 레벨업 |

---

## API 레퍼런스

### REST API

Base URL: `http://localhost:8000`

#### 게임 관리

| 메서드 | 엔드포인트 | 설명 |
|--------|-----------|------|
| GET | /api/games | 게임 목록 |
| POST | /api/games | 새 게임 생성 |
| POST | /api/builds | 빌드 시작 |
| GET | /api/builds/{id} | 빌드 상태 |
| GET | /api/stats | 통계 조회 |

#### 웹훅

| 엔드포인트 | 설명 |
|-----------|------|
| POST /webhook/github | GitHub 이벤트 |
| POST /webhook/gitlab | GitLab 이벤트 |

---

## 배포 가이드

### Docker 배포

```bash
# 환경 변수 설정
cp .env.example .env
# .env 파일 편집

# 컨테이너 시작
docker-compose up -d

# 서비스 확인
# 대시보드: http://localhost:8000
# n8n: http://localhost:5678
```

### 수동 설치

```bash
# 의존성 설치
pip install -r requirements.txt
playwright install chromium

# 웹 대시보드 실행
python core/web/dashboard_server.py

# CLI 사용
python cli.py --help
```

---

## CLI 명령어

```bash
# 새 게임 생성
python cli.py new MyGame -t runner

# 빌드
python cli.py build games/MyGame -p android html5

# 배포
python cli.py deploy builds/game.apk -s google_play

# 대시보드 실행
python cli.py serve --port 8000

# 테스트
python cli.py test --coverage

# 린트
python cli.py lint --fix
```

---

## 라이선스

MIT License

---

*문서 생성일: 2026-01-11*
