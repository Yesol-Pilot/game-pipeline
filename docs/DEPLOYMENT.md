# 🚀 설치 및 배포 가이드

## 목차
1. [로컬 개발 환경](#로컬-개발-환경)
2. [Docker 배포](#docker-배포)
3. [프로덕션 배포](#프로덕션-배포)
4. [API 키 설정](#api-키-설정)
5. [n8n 워크플로우 설정](#n8n-워크플로우-설정)

---

## 로컬 개발 환경

### 요구 사항
- Python 3.10+
- Godot Engine 4.2
- Chrome/Chromium (크롤링용)

### 설치

```bash
# 1. 저장소 클론
git clone https://github.com/Yesol-Pilot/game-pipeline.git
cd game-pipeline

# 2. 가상환경 생성 (권장)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 의존성 설치
pip install -r requirements.txt

# 4. Playwright 브라우저 설치
playwright install chromium

# 5. 환경 변수 설정
cp .env.example .env
# .env 파일 편집하여 API 키 입력
```

### 실행

```bash
# 웹 대시보드
python cli.py serve

# 또는 직접 실행
python core/web/dashboard_server.py

# CLI 명령어
python cli.py --help
```

---

## Docker 배포

### 단일 컨테이너

```bash
# 이미지 빌드
docker build -t game-pipeline .

# 컨테이너 실행
docker run -d -p 8000:8000 \
  -e GEMINI_API_KEY=your_key \
  -e STABILITY_API_KEY=your_key \
  game-pipeline
```

### Docker Compose (권장)

```bash
# 환경 변수 설정
cp .env.example .env
# .env 파일 편집

# 모든 서비스 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 서비스 중지
docker-compose down
```

### 서비스 구성

| 서비스 | 포트 | 설명 |
|--------|------|------|
| pipeline | 8000 | 메인 대시보드 |
| n8n | 5678 | 워크플로우 자동화 |
| redis | 6379 | 캐싱 |

---

## 프로덕션 배포

### 클라우드 배포 (AWS/GCP/Azure)

#### 1. 인프라 준비

```yaml
# 권장 사양
- CPU: 2+ cores
- RAM: 4GB+
- Storage: 20GB+ SSD
- OS: Ubuntu 22.04 LTS
```

#### 2. Docker Compose 배포

```bash
# 서버에서 실행
git clone https://github.com/Yesol-Pilot/game-pipeline.git
cd game-pipeline

# 프로덕션 환경 변수
cp .env.example .env.production
# 편집: 실제 API 키 입력

# 시작
docker-compose --env-file .env.production up -d
```

#### 3. Nginx 리버스 프록시

```nginx
server {
    listen 80;
    server_name pipeline.example.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### 4. SSL 설정 (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d pipeline.example.com
```

---

## API 키 설정

### 필수 API 키

| 서비스 | 용도 | 발급 |
|--------|------|------|
| Gemini API | GDD 생성 | [Google AI Studio](https://makersuite.google.com/) |
| Stability AI | 이미지 생성 | [Stability AI](https://platform.stability.ai/) |
| Slack | 알림 | [Slack API](https://api.slack.com/) |

### 선택 API 키

| 서비스 | 용도 | 발급 |
|--------|------|------|
| Google Play | 배포 | [Play Console](https://play.google.com/console) |
| App Store Connect | iOS 배포 | [App Store Connect](https://appstoreconnect.apple.com/) |
| Steam | Steam 배포 | [Steamworks](https://partner.steamgames.com/) |

### 설정 방법

#### config/project_config.json
```json
{
  "gemini": {
    "api_key": "YOUR_GEMINI_API_KEY"
  },
  "stability_ai": {
    "api_key": "YOUR_STABILITY_API_KEY"
  },
  "slack": {
    "webhook_url": "https://hooks.slack.com/services/..."
  }
}
```

#### .env 파일
```env
GEMINI_API_KEY=your_gemini_api_key
STABILITY_API_KEY=your_stability_api_key
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
```

---

## n8n 워크플로우 설정

### 1. n8n 접속
- URL: http://localhost:5678
- 기본 계정: admin / (env에서 설정한 비밀번호)

### 2. 워크플로우 임포트
1. Settings → Import Workflow
2. `config/n8n_workflow_template.json` 업로드
3. Save

### 3. 슬랙 연동 설정
1. Slack 노드 선택
2. Credentials 설정
3. 웹훅 URL, 서명 시크릿 입력

### 4. 워크플로우 활성화
- 워크플로우 상단의 Active 토글 ON

---

## 문제 해결

### Playwright 오류

```bash
# 의존성 설치 (Linux)
sudo apt-get install libatk1.0-0 libatk-bridge2.0-0 libcups2 \
  libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 \
  libxrandr2 libgbm1 libasound2

# 브라우저 재설치
playwright install chromium --with-deps
```

### Docker 빌드 오류

```bash
# 캐시 없이 빌드
docker-compose build --no-cache

# 로그 확인
docker-compose logs pipeline
```

### API 연결 오류

```bash
# API 키 확인
python -c "import os; print(os.environ.get('GEMINI_API_KEY', 'Not set'))"

# 네트워크 테스트
curl -I https://generativelanguage.googleapis.com
```

---

## 모니터링

### Prometheus 메트릭
- 엔드포인트: http://localhost:8000/metrics

### Grafana 대시보드
- `config/grafana_dashboard.json` 임포트

### 헬스 체크
```bash
curl http://localhost:8000/api/stats
```
