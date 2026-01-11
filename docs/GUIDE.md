# 📖 사용 가이드

초자동화 게임 개발 파이프라인의 상세 사용 가이드입니다.

---

## 목차

1. [환경 설정](#1-환경-설정)
2. [API 키 발급](#2-api-키-발급)
3. [첫 게임 생성](#3-첫-게임-생성)
4. [n8n 워크플로우 설정](#4-n8n-워크플로우-설정)
5. [Godot 빌드](#5-godot-빌드)
6. [문제 해결](#6-문제-해결)

---

## 1. 환경 설정

### Python 환경

```bash
# Python 3.10 이상 권장
python --version

# 가상 환경 생성 (선택)
python -m venv venv
.\venv\Scripts\activate  # Windows

# 의존성 설치
pip install -r requirements.txt

# Playwright 브라우저 설치
playwright install chromium
```

### Godot 설치

1. [Godot 4.2](https://godotengine.org/download) 다운로드
2. 환경 변수 PATH에 추가  
   또는 `config/project_config.json`의 `godot_path`에 전체 경로 입력

```json
{
  "godot": {
    "godot_path": "C:/Godot/Godot_v4.2-stable_win64.exe"
  }
}
```

---

## 2. API 키 발급

### Gemini API (GDD 생성용)

1. [Google AI Studio](https://aistudio.google.com/) 접속
2. "Get API Key" 클릭
3. API 키 복사

```json
{
  "llm": {
    "api_key": "AIza..."
  }
}
```

### Stability AI (이미지 생성용)

1. [Stability AI](https://platform.stability.ai/) 가입
2. API Keys 메뉴에서 키 생성
3. 크레딧 구매 또는 무료 크레딧 사용

```json
{
  "image_generation": {
    "api_key": "sk-..."
  }
}
```

### 슬랙 웹훅 (알림용)

1. [Slack API](https://api.slack.com/apps) 접속
2. "Create New App" → "From scratch"
3. "Incoming Webhooks" 활성화
4. 웹훅 URL 복사

```json
{
  "orchestration": {
    "slack": {
      "webhook_url": "https://hooks.slack.com/services/..."
    }
  }
}
```

---

## 3. 첫 게임 생성

### 테스트 실행

```bash
python create_first_game.py
```

결과 확인:
- `test_output/gdd.json` - 생성된 GDD
- `test_output/game_YYYYMMDD_HHMMSS/` - 복사된 템플릿
- `test_output/report.txt` - 리포트

### 전체 파이프라인 실행

```bash
python -c "
from core import Pipeline
import asyncio

async def main():
    pipeline = Pipeline('config/project_config.json')
    result = await pipeline.run('runner')
    print(pipeline.generate_report(result))

asyncio.run(main())
"
```

---

## 4. n8n 워크플로우 설정

### n8n 설치

```bash
# Docker 사용
docker run -d --name n8n -p 5678:5678 n8nio/n8n

# 또는 npm 사용
npm install n8n -g
n8n start
```

### 워크플로우 임포트

1. n8n 대시보드 접속 (http://localhost:5678)
2. Settings → Import from File
3. `config/n8n_workflow_template.json` 선택
4. 슬랙 크레덴셜 연결
5. 활성화

### 환경 변수

n8n 환경 변수 설정:
```
SLACK_SIGNING_SECRET=your_signing_secret
```

---

## 5. Godot 빌드

### 헤드리스 에셋 임포트

```bash
godot --headless --editor --path ./games/runner/프로젝트명 --quit
```

### 내보내기 (Android APK)

```bash
godot --headless --path ./games/runner/프로젝트명 --export-release "Android" ./builds/game.apk
```

### 내보내기 (HTML5)

```bash
godot --headless --path ./games/runner/프로젝트명 --export-release "Web" ./builds/index.html
```

> ⚠️ 사전 설정:
> - `export_presets.cfg` 파일 필요
> - Android: keystore 설정 필요
> - HTML5: 추가 설정 불필요

---

## 6. 문제 해결

### 틱톡 크롤링 실패

**증상**: `TimeoutError` 또는 빈 결과

**해결**:
1. `playwright install chromium` 재실행
2. 프록시 설정 확인
3. 타겟 URL 변경 (사이트 구조 변경 시)

### GDD 생성 오류

**증상**: 빈 GDD 또는 파싱 오류

**해결**:
1. API 키 확인
2. 할당량 확인 (무료 티어 제한)
3. `temperature` 값 조정 (0.5~0.9)

### Godot 빌드 실패

**증상**: `FileNotFoundError` 또는 빈 출력

**해결**:
1. Godot 경로 확인 (`godot --version`)
2. `export_presets.cfg` 존재 확인
3. 메인 씬 설정 확인

### 슬랙 알림 미수신

**증상**: 메시지 전송 실패

**해결**:
1. 웹훅 URL 확인
2. 채널 권한 확인
3. 네트워크 방화벽 확인

---

## 추가 리소스

- [Godot 문서](https://docs.godotengine.org/)
- [n8n 문서](https://docs.n8n.io/)
- [Stability AI 문서](https://platform.stability.ai/docs/)
- [프로젝트 마스터룰](MASTER_RULES.md)
