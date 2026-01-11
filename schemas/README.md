# 스키마 정의 저장소

게임 파이프라인에서 사용되는 JSON 스키마 정의 폴더입니다.

## 📄 스키마 목록

| 파일 | 용도 |
|------|------|
| `gdd_schema.json` | 게임 기획 문서(GDD) 구조 정의 |
| `template_config_schema.json` | 템플릿 설정 파일 구조 정의 |

## 🔧 사용법

스키마를 활용한 JSON 유효성 검증:

```python
import jsonschema
import json

# 스키마 로드
with open('schemas/gdd_schema.json', 'r', encoding='utf-8') as f:
    schema = json.load(f)

# GDD 데이터 검증
jsonschema.validate(instance=gdd_data, schema=schema)
```

## ✅ LLM 프롬프트에서 활용

GDD 생성 시 스키마를 LLM 시스템 프롬프트에 포함하여 구조화된 출력을 유도합니다.
