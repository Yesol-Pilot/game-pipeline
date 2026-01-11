# 🎮 초자동화 게임 개발 파이프라인

트렌드 수집 → GDD 생성 → 자산 생성 → Godot 빌드 → 스토어 배포까지 완전 자동화

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Godot](https://img.shields.io/badge/Godot-4.2-478cbf.svg)](https://godotengine.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## ⚡ 빠른 시작

```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. 새 게임 생성
python cli.py new MyGame -t runner

# 3. 대시보드 실행
python cli.py serve
# → http://localhost:8000
```

---

## 📁 프로젝트 구조

```
core/                    # 17개 모듈
├── crawler/            # TikTok/Google 트렌드
├── gdd_generator/      # GDD + 다국어
├── asset_pipeline/     # 이미지 + 스크린샷
├── builder/            # Godot 빌드
├── deployer/           # Google/iOS/Steam
├── orchestrator/       # 슬랙 알림
├── analytics/          # 분석
├── ab_testing/         # A/B 테스트
├── balancing/          # 밸런싱
├── web/                # FastAPI + 웹훅
├── monitoring/         # Prometheus
├── security/           # JWT
├── plugins/            # 플러그인
├── cache/              # 캐싱
└── pipeline.py         # 통합

templates/ (6종)
├── runner, puzzle, clicker
└── match3, rhythm, idle
```

---

## 🛠️ CLI 명령어

| 명령어 | 설명 |
|--------|------|
| `python cli.py new NAME -t runner` | 새 게임 생성 |
| `python cli.py build PROJECT -p android` | 빌드 |
| `python cli.py deploy BUILD -s google_play` | 배포 |
| `python cli.py serve` | 대시보드 |
| `python cli.py test --coverage` | 테스트 |
| `python cli.py lint --fix` | 코드 정리 |

---

## 🐳 Docker

```bash
cp .env.example .env
docker-compose up -d

# 대시보드: http://localhost:8000
# n8n: http://localhost:5678
```

---

## 📚 문서

- [상세 가이드](docs/GUIDE.md)
- [아키텍처](docs/ARCHITECTURE.md)
- [API 문서](docs/API.md)

---

## 🚀 워크플로우

```
TikTok/Google → GDD(LLM) → Slack승인 → 자산(AI) → Godot빌드 → 스토어
     ↓            ↓           ↓           ↓           ↓
   트렌드       기획서       HITL       이미지      APK/IPA
```

---

## 📄 라이선스

MIT License
