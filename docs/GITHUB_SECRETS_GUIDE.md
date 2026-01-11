# 🔑 GitHub Secrets 설정 가이드

구축된 CI/CD 파이프라인(`pipeline.yml`)이 안드로이드 빌드 및 배포를 수행하려면 GitHub Repository에 보안 키(Secrets)를 등록해야 합니다.

## 1. Secrets 등록 위치
1. GitHub 리포지토리로 이동: [Yesol-Pilot/game-pipeline](https://github.com/Yesol-Pilot/game-pipeline)
2. 상단 탭 **Settings** 클릭
3. 좌측 메뉴 **Secrets and variables** > **Actions** 클릭
4. **New repository secret** 버튼 클릭하여 아래 항목들을 추가

## 2. 필수 Secrets 목록

| Secret 이름 | 설명 | 예시 값/생성 방법 |
| :--- | :--- | :--- |
| `ANDROID_KEYSTORE_BASE64` | Base64로 인코딩된 Keystore 파일 내용 | (아래 생성 방법 참고) |
| `ANDROID_KEYSTORE_ALIAS` | Keystore 별칭(Alias) | `release_user` |
| `ANDROID_KEYSTORE_PASSWORD` | Keystore 비밀번호 | `my_secure_password` |
| `SLACK_WEBHOOK_URL` | (선택) 빌드 알림용 슬랙 웹훅 | `https://hooks.slack.com/...` |

## 3. ANDROID_KEYSTORE_BASE64 생성 방법

안드로이드 앱 서명을 위한 Keystore(`.keystore` 또는 `.jks`) 파일을 Base64 문자열로 변환해야 합니다.

### Windows (PowerShell)
```powershell
# 1. Keystore가 없다면 생성 (이미 있다면 건너뛰기)
keytool -genkey -v -keystore release.keystore -alias release_user -keyalg RSA -keysize 2048 -validity 10000

# 2. Base64로 인코딩하여 클립보드에 복사
$content = [System.Convert]::ToBase64String([System.IO.File]::ReadAllBytes("release.keystore"))
Set-Clipboard $content
# 이제 GitHub Secret 값 입력창에 붙여넣기 (Ctrl+V) 하세요.
```

### Mac / Linux
```bash
# 1. Keystore가 없다면 생성
keytool -genkey -v -keystore release.keystore -alias release_user -keyalg RSA -keysize 2048 -validity 10000

# 2. Base64로 인코딩하여 클립보드에 복사 (Mac)
base64 -i release.keystore | pbcopy

# 2. Base64로 인코딩 (Linux)
base64 release.keystore -w 0
# 출력된 긴 문자열을 복사하세요.
```

## 4. 검증 방법
1. 위 Secrets를 모두 등록합니다.
2. GitHub **Actions** 탭으로 이동합니다.
3. 좌측 **Workflows**에서 **게임 파이프라인 CI/CD**를 선택합니다.
4. **Run workflow** 버튼을 누르고, `Template Type`을 선택하여 실행합니다.
5. `build` 단계에서 에러 없이 `Android 빌드`가 성공하는지 확인합니다.
