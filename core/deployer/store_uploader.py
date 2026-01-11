"""
Google Play 스토어 자동 업로드 모듈
Google Play Developer API 연동
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ReleaseInfo:
    """릴리스 정보"""
    package_name: str
    version_code: int
    version_name: str
    release_notes: Dict[str, str]  # {language_code: notes}
    track: str = "internal"  # internal, alpha, beta, production


class GooglePlayUploader:
    """Google Play 스토어 업로더"""
    
    def __init__(self, config: dict):
        """
        Args:
            config: API 설정 (서비스 계정 키 경로 등)
        """
        self.config = config
        self.credentials_path = config.get("credentials_path", "")
        self.service = None
    
    def _init_service(self) -> bool:
        """Google Play API 서비스 초기화"""
        try:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build
            
            if not self.credentials_path or not Path(self.credentials_path).exists():
                print("경고: 서비스 계정 키 파일이 없습니다")
                return False
            
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path,
                scopes=['https://www.googleapis.com/auth/androidpublisher']
            )
            
            self.service = build('androidpublisher', 'v3', credentials=credentials)
            return True
            
        except ImportError:
            print("경고: google-api-python-client가 설치되지 않았습니다")
            print("pip install google-api-python-client google-auth")
            return False
        except Exception as e:
            print(f"API 초기화 오류: {e}")
            return False
    
    def upload_apk(
        self,
        package_name: str,
        apk_path: str,
        track: str = "internal"
    ) -> Optional[int]:
        """
        APK 업로드
        
        Args:
            package_name: 앱 패키지명 (예: com.example.game)
            apk_path: APK 파일 경로
            track: 릴리스 트랙 (internal/alpha/beta/production)
        
        Returns:
            버전 코드 또는 None
        """
        if not self.service and not self._init_service():
            return self._simulate_upload(apk_path)
        
        try:
            edits = self.service.edits()
            
            # 1. 편집 세션 생성
            edit_request = edits.insert(body={}, packageName=package_name)
            edit = edit_request.execute()
            edit_id = edit['id']
            
            # 2. APK 업로드
            with open(apk_path, 'rb') as apk_file:
                apk_response = edits.apks().upload(
                    packageName=package_name,
                    editId=edit_id,
                    media_body=apk_path
                ).execute()
            
            version_code = apk_response['versionCode']
            
            # 3. 트랙에 할당
            edits.tracks().update(
                packageName=package_name,
                editId=edit_id,
                track=track,
                body={
                    'releases': [{
                        'versionCodes': [version_code],
                        'status': 'completed'
                    }]
                }
            ).execute()
            
            # 4. 편집 커밋
            edits.commit(packageName=package_name, editId=edit_id).execute()
            
            return version_code
            
        except Exception as e:
            print(f"업로드 오류: {e}")
            return None
    
    def upload_aab(
        self,
        package_name: str,
        aab_path: str,
        track: str = "internal"
    ) -> Optional[int]:
        """
        AAB (Android App Bundle) 업로드
        """
        if not self.service and not self._init_service():
            return self._simulate_upload(aab_path)
        
        try:
            edits = self.service.edits()
            
            edit_request = edits.insert(body={}, packageName=package_name)
            edit = edit_request.execute()
            edit_id = edit['id']
            
            # AAB 업로드 (bundles 엔드포인트 사용)
            with open(aab_path, 'rb') as aab_file:
                bundle_response = edits.bundles().upload(
                    packageName=package_name,
                    editId=edit_id,
                    media_body=aab_path
                ).execute()
            
            version_code = bundle_response['versionCode']
            
            edits.tracks().update(
                packageName=package_name,
                editId=edit_id,
                track=track,
                body={
                    'releases': [{
                        'versionCodes': [version_code],
                        'status': 'completed'
                    }]
                }
            ).execute()
            
            edits.commit(packageName=package_name, editId=edit_id).execute()
            
            return version_code
            
        except Exception as e:
            print(f"AAB 업로드 오류: {e}")
            return None
    
    def update_listing(
        self,
        package_name: str,
        language: str,
        title: str,
        short_desc: str,
        full_desc: str
    ) -> bool:
        """스토어 등록 정보 업데이트"""
        if not self.service and not self._init_service():
            return self._simulate_listing_update()
        
        try:
            edits = self.service.edits()
            
            edit = edits.insert(body={}, packageName=package_name).execute()
            edit_id = edit['id']
            
            edits.listings().update(
                packageName=package_name,
                editId=edit_id,
                language=language,
                body={
                    'title': title,
                    'shortDescription': short_desc,
                    'fullDescription': full_desc
                }
            ).execute()
            
            edits.commit(packageName=package_name, editId=edit_id).execute()
            return True
            
        except Exception as e:
            print(f"등록 정보 업데이트 오류: {e}")
            return False
    
    def _simulate_upload(self, file_path: str) -> int:
        """시뮬레이션 업로드 (API 없을 때)"""
        print(f"[시뮬레이션] 업로드: {file_path}")
        return 1  # 가상 버전 코드
    
    def _simulate_listing_update(self) -> bool:
        """시뮬레이션 등록 정보 업데이트"""
        print("[시뮬레이션] 등록 정보 업데이트")
        return True


class AppStoreUploadManager:
    """앱스토어 업로드 매니저 (Google Play + 향후 iOS)"""
    
    def __init__(self, config: dict):
        self.config = config
        self.google_play = GooglePlayUploader(config.get("google_play", {}))
    
    def upload_game(
        self,
        game_id: str,
        build_path: str,
        package_name: str,
        release_info: ReleaseInfo
    ) -> Dict[str, Any]:
        """
        게임 업로드 (멀티 플랫폼)
        
        Args:
            game_id: 게임 ID
            build_path: 빌드 파일 경로
            package_name: 패키지명
            release_info: 릴리스 정보
        
        Returns:
            업로드 결과
        """
        result = {
            "game_id": game_id,
            "timestamp": datetime.now().isoformat(),
            "platforms": {}
        }
        
        # Google Play 업로드
        if build_path.endswith('.apk'):
            version_code = self.google_play.upload_apk(
                package_name,
                build_path,
                release_info.track
            )
        elif build_path.endswith('.aab'):
            version_code = self.google_play.upload_aab(
                package_name,
                build_path,
                release_info.track
            )
        else:
            version_code = None
        
        result["platforms"]["google_play"] = {
            "success": version_code is not None,
            "version_code": version_code,
            "track": release_info.track
        }
        
        # 릴리스 노트 업데이트
        for lang, notes in release_info.release_notes.items():
            self.google_play.update_listing(
                package_name,
                lang,
                release_info.version_name,
                notes[:80],  # short desc 제한
                notes
            )
        
        return result


# 사용 예시
def main():
    config = {
        "google_play": {
            "credentials_path": "config/google_play_credentials.json"
        }
    }
    
    manager = AppStoreUploadManager(config)
    
    release_info = ReleaseInfo(
        package_name="com.example.trendrunner",
        version_code=1,
        version_name="1.0.0",
        release_notes={
            "ko-KR": "첫 번째 릴리스",
            "en-US": "First release"
        },
        track="internal"
    )
    
    result = manager.upload_game(
        game_id="game_001",
        build_path="builds/game.apk",
        package_name="com.example.trendrunner",
        release_info=release_info
    )
    
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
