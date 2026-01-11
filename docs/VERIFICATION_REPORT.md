# 📋 게임 파이프라인 검증 및 개선 이행 보고서

**작성일**: 2026-01-11
**대상 프로젝트**: Yesol-Pilot/game-pipeline

## 1. 개요
본 보고서는 "게임 파이프라인 검증 및 개선 제안" 문서에서 제기된 개선 사항들에 대한 구현 및 적용 결과를 명시합니다.

## 2. 이행 내역 요약

| 평가 영역 | 핵심 점검 항목 | 이행 상태 | 구현 세부 사항 |
| :--- | :--- | :---: | :--- |
| **1. CI/CD** | 헤드리스 빌드 명령어 | ✅ 완료 | `pipeline.yml` 내 `godot --headless --export-release` 적용 |
| | Android SDK 연동 | ✅ 완료 | `barichello/godot-ci:4.2` Docker 이미지 사용으로 사전 구성 완료 |
| | Docker/캐싱 | ✅ 완료 | `.godot` 폴더 캐싱 및 Docker 컨테이너 기반 빌드 환경 구축 (`.github/workflows/pipeline.yml`) |
| **2. 아키텍처** | 리소스 기반 설계 | ✅ 완료 | `templates/_core/resources/` 내 `CharacterStats`, `GameConfig` 베이스 클래스 구현 |
| | 의존성 주입 | ✅ 완료 | 템플릿 가이드라인 반영 (문서화) |
| | 이벤트 버스 | ✅ 완료 | `templates/_core/autoloads/` 내 `combat_events.gd`, `ui_events.gd` 구현으로 도메인 분리 |
| **3. 보안** | Keystore 관리 | ✅ 완료 | Base64 인코딩된 Keystore를 GitHub Secrets에서 디코딩하여 주입하는 로직 구현 |
| | 비밀번호 보호 | ✅ 완료 | `templates/template_runner/export_presets.cfg` 내 민감 정보 플레이스홀더 처리 |
| **4. 관리** | 프로젝트 구조 | ✅ 완료 | `templates/_core` 디렉토리 구조화 (`resources`, `autoloads`) |

## 3. 상세 구현 내용

### 3.1 CI/CD 파이프라인 강화 (`.github/workflows/pipeline.yml`)
- **Docker 컨테이너 도입**: `barichello/godot-ci:4.2` 이미지를 사용하여 일관된 빌드 환경(Android SDK, JDK 포함)을 보장했습니다.
- **캐싱 전략**: 빌드 속도 최적화를 위해 `~/.local/share/godot/archives` 및 `.godot` 임포트 캐싱을 적용했습니다.
- **안드로이드 빌드 파이프라인**:
  - `secrets.ANDROID_KEYSTORE_BASE64`를 디코딩하여 `release.keystore` 생성.
  - `sed` 명령어를 주석으로 포함하여 추후 실제 Secrets 연동 시 `export_presets.cfg` 주입 가이드 제공.
  - `godot --headless --export-release "Android"` 명령어 표준화.

### 3.2 리소스 기반 아키텍처 도입
- **데이터와 로직 분리**:
  - `CharacterStats` (`templates/_core/resources/character_stats.gd`): 체력, 공격력, 스킨 등 캐릭터 데이터를 리소스로 정의.
  - `GameConfig` (`templates/_core/resources/game_config.gd`): 오디오, 게임플레이 설정을 관리하는 전역 리소스 정의.
- 이를 통해 리스킨(Reskin) 및 밸런스 조정 시 코드를 수정하지 않고 리소스 파일(`.tres`)만 교체 가능하도록 개선했습니다.

### 3.3 이벤트 버스 시스템 확장
- **도메인별 분리**: 단일 이벤트 버스의 비대화를 방지하고 결합도를 낮추기 위해 역할을 분리했습니다.
  - `CombatEvents` (`templates/_core/autoloads/combat_events.gd`): 공격, 피격, 사망, 레벨업 등 게임플레이 로직 신호.
  - `UIEvents` (`templates/_core/autoloads/ui_events.gd`): 점수 갱신, 팝업, 화면 전환 등 UI 관련 신호.

### 3.4 보안 및 배포 설정
- **`export_presets.cfg` 보안**: `templates/template_runner/export_presets.cfg` 파일에서 `keystore/release_password` 등의 필드를 비워두어 민감 정보 커밋을 방지했습니다.
- **CI 연동 준비**: GitHub Actions에서 동적으로 비밀번호를 주입할 수 있는 구조를 마련했습니다.

## 4. 향후 권장 사항
- **실제 배포 시**: GitHub Repository Settings에 `ANDROID_KEYSTORE_BASE64`, `ANDROID_KEYSTORE_ALIAS`, `ANDROID_KEYSTORE_PASSWORD` Secrets를 반드시 등록해야 합니다.
- **테스트 커버리지**: 새로운 아키텍처가 적용된 템플릿에 대한 단위 테스트(`GdUnit4` 등 활용) 추가를 고려할 수 있습니다.
