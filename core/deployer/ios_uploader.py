"""
iOS App Store Connect 업로더
App Store Connect API 연동
"""

import json
import jwt
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class AppStoreRelease:
    """App Store 릴리스 정보"""
    bundle_id: str
    version: str
    build_number: str
    release_notes: Dict[str, str]  # {locale: notes}
    submit_for_review: bool = False


class AppStoreConnectUploader:
    """App Store Connect API 업로더"""
    
    def __init__(self, config: dict):
        """
        Args:
            config: API 설정
                - issuer_id: Issuer ID
                - key_id: Key ID
                - private_key_path: .p8 파일 경로
        """
        self.config = config
        self.issuer_id = config.get("issuer_id", "")
        self.key_id = config.get("key_id", "")
        self.private_key_path = config.get("private_key_path", "")
        self.base_url = "https://api.appstoreconnect.apple.com/v1"
        self._token = None
        self._token_expiry = 0
    
    def _generate_token(self) -> Optional[str]:
        """JWT 토큰 생성"""
        if not self.private_key_path or not Path(self.private_key_path).exists():
            print("경고: Private key 파일이 없습니다")
            return None
        
        try:
            with open(self.private_key_path, "r") as f:
                private_key = f.read()
            
            now = int(time.time())
            expiry = now + 20 * 60  # 20분 유효
            
            payload = {
                "iss": self.issuer_id,
                "iat": now,
                "exp": expiry,
                "aud": "appstoreconnect-v1"
            }
            
            token = jwt.encode(
                payload,
                private_key,
                algorithm="ES256",
                headers={"kid": self.key_id}
            )
            
            self._token = token
            self._token_expiry = expiry
            return token
            
        except ImportError:
            print("경고: PyJWT가 설치되지 않았습니다")
            print("pip install PyJWT cryptography")
            return None
        except Exception as e:
            print(f"토큰 생성 오류: {e}")
            return None
    
    def _get_headers(self) -> Dict[str, str]:
        """API 요청 헤더"""
        now = int(time.time())
        if not self._token or now >= self._token_expiry - 60:
            self._generate_token()
        
        return {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json"
        }
    
    def upload_ipa(
        self,
        ipa_path: str,
        bundle_id: str
    ) -> Optional[str]:
        """
        IPA 업로드 (altool 또는 Transporter 사용)
        
        Note: API로 직접 업로드는 불가, altool CLI 필요
        """
        if not Path(ipa_path).exists():
            print(f"IPA 파일 없음: {ipa_path}")
            return None
        
        # macOS에서 altool 사용
        import subprocess
        
        try:
            # xcrun altool로 업로드
            result = subprocess.run([
                "xcrun", "altool",
                "--upload-app",
                "-f", ipa_path,
                "-t", "ios",
                "--apiKey", self.key_id,
                "--apiIssuer", self.issuer_id
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("IPA 업로드 성공")
                return "uploaded"
            else:
                print(f"업로드 실패: {result.stderr}")
                return None
                
        except FileNotFoundError:
            print("경고: xcrun을 찾을 수 없습니다 (macOS 필요)")
            return self._simulate_upload(ipa_path)
        except Exception as e:
            print(f"업로드 오류: {e}")
            return None
    
    def create_version(
        self,
        app_id: str,
        version: str,
        release_notes: Dict[str, str]
    ) -> Optional[str]:
        """새 앱 버전 생성"""
        if not self._token and not self._generate_token():
            return self._simulate_version_create()
        
        import urllib.request
        
        url = f"{self.base_url}/appStoreVersions"
        
        body = {
            "data": {
                "type": "appStoreVersions",
                "attributes": {
                    "platform": "IOS",
                    "versionString": version
                },
                "relationships": {
                    "app": {
                        "data": {
                            "type": "apps",
                            "id": app_id
                        }
                    }
                }
            }
        }
        
        try:
            data = json.dumps(body).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=data,
                headers=self._get_headers(),
                method="POST"
            )
            
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode("utf-8"))
                version_id = result["data"]["id"]
                
                # 릴리스 노트 업데이트
                for locale, notes in release_notes.items():
                    self._update_localization(version_id, locale, notes)
                
                return version_id
                
        except Exception as e:
            print(f"버전 생성 오류: {e}")
            return None
    
    def _update_localization(
        self,
        version_id: str,
        locale: str,
        what_is_new: str
    ) -> bool:
        """릴리스 노트 업데이트"""
        import urllib.request
        
        # 먼저 localization ID 조회 필요
        url = f"{self.base_url}/appStoreVersions/{version_id}/appStoreVersionLocalizations"
        
        try:
            req = urllib.request.Request(url, headers=self._get_headers())
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode("utf-8"))
                
                for loc in result.get("data", []):
                    if loc["attributes"]["locale"] == locale:
                        loc_id = loc["id"]
                        return self._patch_localization(loc_id, what_is_new)
            
            return False
            
        except Exception as e:
            print(f"Localization 오류: {e}")
            return False
    
    def _patch_localization(self, loc_id: str, what_is_new: str) -> bool:
        """Localization 패치"""
        import urllib.request
        
        url = f"{self.base_url}/appStoreVersionLocalizations/{loc_id}"
        
        body = {
            "data": {
                "type": "appStoreVersionLocalizations",
                "id": loc_id,
                "attributes": {
                    "whatsNew": what_is_new
                }
            }
        }
        
        try:
            data = json.dumps(body).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=data,
                headers=self._get_headers(),
                method="PATCH"
            )
            
            with urllib.request.urlopen(req) as response:
                return response.status == 200
                
        except Exception as e:
            print(f"패치 오류: {e}")
            return False
    
    def submit_for_review(self, version_id: str) -> bool:
        """심사 제출"""
        if not self._token and not self._generate_token():
            return self._simulate_submit()
        
        import urllib.request
        
        url = f"{self.base_url}/appStoreVersionSubmissions"
        
        body = {
            "data": {
                "type": "appStoreVersionSubmissions",
                "relationships": {
                    "appStoreVersion": {
                        "data": {
                            "type": "appStoreVersions",
                            "id": version_id
                        }
                    }
                }
            }
        }
        
        try:
            data = json.dumps(body).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=data,
                headers=self._get_headers(),
                method="POST"
            )
            
            with urllib.request.urlopen(req) as response:
                return response.status == 201
                
        except Exception as e:
            print(f"심사 제출 오류: {e}")
            return False
    
    def _simulate_upload(self, path: str) -> str:
        """시뮬레이션 업로드"""
        print(f"[시뮬레이션] iOS 업로드: {path}")
        return "simulated"
    
    def _simulate_version_create(self) -> str:
        """시뮬레이션 버전 생성"""
        print("[시뮬레이션] 버전 생성")
        return "sim_version_001"
    
    def _simulate_submit(self) -> bool:
        """시뮬레이션 심사 제출"""
        print("[시뮬레이션] 심사 제출")
        return True


# 사용 예시
def main():
    config = {
        "issuer_id": "YOUR_ISSUER_ID",
        "key_id": "YOUR_KEY_ID",
        "private_key_path": "config/AuthKey_XXXX.p8"
    }
    
    uploader = AppStoreConnectUploader(config)
    
    # IPA 업로드
    result = uploader.upload_ipa(
        ipa_path="builds/game.ipa",
        bundle_id="com.example.game"
    )
    
    print(f"업로드 결과: {result}")


if __name__ == "__main__":
    main()
