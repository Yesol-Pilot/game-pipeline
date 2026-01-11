# API 문서

게임 파이프라인 REST API 레퍼런스

---

## 기본 정보

- **Base URL**: `http://localhost:8000`
- **Content-Type**: `application/json`

---

## 엔드포인트

### 통계

#### GET /api/stats

전체 통계 조회

**응답 예시:**
```json
{
  "total_games": 10,
  "total_builds": 25,
  "active_tests": 2,
  "total_revenue": 1500.00
}
```

---

### 게임

#### GET /api/games

게임 목록 조회

**응답 예시:**
```json
[
  {
    "id": "game_20260111_120000",
    "title": "트렌드 러너",
    "template_type": "runner",
    "status": "gdd_ready",
    "created_at": "2026-01-11T12:00:00"
  }
]
```

#### POST /api/games

새 게임 생성

**요청:**
```json
{
  "keywords": ["#챌린지", "바이럴"],
  "template_type": "runner"
}
```

**응답:**
```json
{
  "game_id": "game_20260111_120000",
  "status": "creating"
}
```

---

### 빌드

#### POST /api/builds

빌드 시작

**요청:**
```json
{
  "game_id": "game_20260111_120000",
  "platforms": ["android", "html5"]
}
```

**응답:**
```json
{
  "build_id": "build_20260111_120100",
  "status": "building"
}
```

#### GET /api/builds/{build_id}

빌드 상태 조회

**응답:**
```json
{
  "game_id": "game_20260111_120000",
  "platforms": ["android", "html5"],
  "status": "completed",
  "started_at": "2026-01-11T12:01:00"
}
```

---

## 에러 코드

| 코드 | 설명 |
|------|------|
| 404 | 리소스를 찾을 수 없음 |
| 400 | 잘못된 요청 |
| 500 | 서버 오류 |

---

## OpenAPI 스키마

FastAPI 자동 생성: `http://localhost:8000/docs`
