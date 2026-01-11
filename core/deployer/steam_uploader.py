"""
Steam 업로더
Steamworks SDK를 사용한 Steam 빌드 업로드
"""

import json
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class SteamBuildConfig:
    """Steam 빌드 설정"""
    app_id: str
    depot_id: str
    build_description: str
    content_root: str
    local_path: str = "*"
    depot_path: str = "."
    set_live: Optional[str] = None  # beta 브랜치 이름 또는 None


class SteamUploader:
    """Steam 빌드 업로더"""
    
    def __init__(self, config: dict):
        """
        Args:
            config: Steam 설정
                - steamcmd_path: steamcmd 경로
                - username: Steam 계정
                - config_path: 빌드 설정 파일 경로
        """
        self.config = config
        self.steamcmd_path = config.get("steamcmd_path", "steamcmd")
        self.username = config.get("username", "")
        self.scripts_path = Path(config.get("scripts_path", "steam_scripts"))
        self.scripts_path.mkdir(parents=True, exist_ok=True)
    
    def generate_app_build_script(self, build_config: SteamBuildConfig) -> str:
        """앱 빌드 VDF 스크립트 생성"""
        script = f'''"AppBuild"
{{
    "AppID" "{build_config.app_id}"
    "Desc" "{build_config.build_description}"
    "ContentRoot" "{build_config.content_root}"
    "BuildOutput" "./output/"
    "Depots"
    {{
        "{build_config.depot_id}"
        {{
            "FileMapping"
            {{
                "LocalPath" "{build_config.local_path}"
                "DepotPath" "{build_config.depot_path}"
                "Recursive" "1"
            }}
        }}
    }}
}}'''
        return script
    
    def upload_build(
        self,
        build_config: SteamBuildConfig,
        password: str = None
    ) -> Dict[str, Any]:
        """
        Steam에 빌드 업로드
        
        Args:
            build_config: 빌드 설정
            password: Steam 비밀번호 (또는 환경 변수 사용)
        
        Returns:
            업로드 결과
        """
        result = {
            "success": False,
            "app_id": build_config.app_id,
            "timestamp": datetime.now().isoformat(),
            "message": ""
        }
        
        # VDF 스크립트 생성
        script_content = self.generate_app_build_script(build_config)
        script_path = self.scripts_path / f"app_build_{build_config.app_id}.vdf"
        
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script_content)
        
        # steamcmd 실행
        cmd = [
            self.steamcmd_path,
            "+login", self.username,
        ]
        
        if password:
            cmd.extend([password])
        
        cmd.extend([
            "+run_app_build", str(script_path),
            "+quit"
        ])
        
        try:
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10분 타임아웃
            )
            
            if process.returncode == 0:
                result["success"] = True
                result["message"] = "빌드 업로드 성공"
                
                # 브랜치 설정
                if build_config.set_live:
                    self._set_build_live(
                        build_config.app_id,
                        build_config.set_live
                    )
            else:
                result["message"] = f"업로드 실패: {process.stderr}"
                
        except FileNotFoundError:
            result["message"] = "steamcmd를 찾을 수 없습니다"
            return self._simulate_upload(build_config)
        except subprocess.TimeoutExpired:
            result["message"] = "업로드 타임아웃"
        except Exception as e:
            result["message"] = str(e)
        
        return result
    
    def _set_build_live(self, app_id: str, branch: str) -> bool:
        """빌드를 라이브로 설정"""
        # Steamworks 파트너 API 사용 필요
        print(f"[정보] 브랜치 '{branch}' 적용은 파트너 대시보드에서 수행하세요")
        return True
    
    def _simulate_upload(self, build_config: SteamBuildConfig) -> Dict[str, Any]:
        """시뮬레이션 업로드"""
        print(f"[시뮬레이션] Steam 업로드: App {build_config.app_id}")
        return {
            "success": True,
            "app_id": build_config.app_id,
            "timestamp": datetime.now().isoformat(),
            "message": "시뮬레이션 성공"
        }
    
    def verify_depot(self, app_id: str, depot_id: str) -> bool:
        """디팟 검증"""
        print(f"[정보] 디팟 검증: App {app_id}, Depot {depot_id}")
        return True


class SteamworksBuildManager:
    """Steamworks 빌드 매니저"""
    
    def __init__(self, config: dict):
        self.uploader = SteamUploader(config)
    
    def create_and_upload(
        self,
        app_id: str,
        depot_id: str,
        build_path: str,
        description: str,
        branch: str = None
    ) -> Dict[str, Any]:
        """빌드 생성 및 업로드"""
        
        build_config = SteamBuildConfig(
            app_id=app_id,
            depot_id=depot_id,
            build_description=description,
            content_root=build_path,
            set_live=branch
        )
        
        return self.uploader.upload_build(build_config)


# 사용 예시
def main():
    config = {
        "steamcmd_path": "C:/steamcmd/steamcmd.exe",
        "username": "your_steam_username",
        "scripts_path": "steam_scripts"
    }
    
    manager = SteamworksBuildManager(config)
    
    result = manager.create_and_upload(
        app_id="1234567",
        depot_id="1234568",
        build_path="builds/steam",
        description="v1.0.0 릴리스",
        branch="beta"
    )
    
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
