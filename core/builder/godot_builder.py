"""
Godot 빌더 모듈
헤드리스 Godot 빌드 자동화
"""

import os
import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Tuple


class GodotBuilder:
    """Godot 헤드리스 빌드 자동화"""
    
    def __init__(self, config: dict):
        """
        Args:
            config: 빌드 설정 (Godot 경로, 타겟 등)
        """
        self.config = config
        self.godot_path = config.get("godot_path", "godot")
        self.export_targets = config.get("export_targets", ["android", "html5"])
    
    def import_assets(self, project_path: str) -> Tuple[bool, str]:
        """
        헤드리스 에셋 임포트 트리거
        새 자산 파일을 Godot 엔진이 인식하도록 강제 임포트
        
        Args:
            project_path: Godot 프로젝트 경로
        
        Returns:
            (성공 여부, 메시지)
        """
        try:
            cmd = [
                self.godot_path,
                "--headless",
                "--editor",
                "--path", project_path,
                "--quit"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120  # 2분 타임아웃
            )
            
            if result.returncode == 0:
                return True, "에셋 임포트 완료"
            else:
                return False, f"임포트 오류: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return False, "임포트 타임아웃"
        except FileNotFoundError:
            return False, f"Godot 실행 파일을 찾을 수 없음: {self.godot_path}"
        except Exception as e:
            return False, f"임포트 실패: {str(e)}"
    
    def export_game(
        self, 
        project_path: str, 
        preset_name: str, 
        output_path: str
    ) -> Tuple[bool, str]:
        """
        게임 내보내기 (빌드)
        
        Args:
            project_path: Godot 프로젝트 경로
            preset_name: 내보내기 프리셋 이름 (export_presets.cfg에 정의)
            output_path: 출력 파일 경로
        
        Returns:
            (성공 여부, 메시지)
        """
        try:
            # 출력 디렉토리 생성
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            cmd = [
                self.godot_path,
                "--headless",
                "--path", project_path,
                "--export-release", preset_name, output_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10분 타임아웃
            )
            
            if result.returncode == 0 and Path(output_path).exists():
                return True, f"빌드 완료: {output_path}"
            else:
                return False, f"빌드 오류: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return False, "빌드 타임아웃 (10분 초과)"
        except FileNotFoundError:
            return False, f"Godot 실행 파일을 찾을 수 없음: {self.godot_path}"
        except Exception as e:
            return False, f"빌드 실패: {str(e)}"
    
    def build_all_targets(
        self, 
        project_path: str, 
        output_dir: str
    ) -> List[Tuple[str, bool, str]]:
        """
        모든 타겟 플랫폼 빌드
        
        Args:
            project_path: Godot 프로젝트 경로
            output_dir: 출력 디렉토리
        
        Returns:
            [(타겟, 성공여부, 메시지), ...]
        """
        results = []
        
        # 우선 에셋 임포트
        import_success, import_msg = self.import_assets(project_path)
        if not import_success:
            return [("import", False, import_msg)]
        
        # 타겟별 빌드
        target_settings = {
            "android": {
                "preset": "Android",
                "extension": ".apk"
            },
            "html5": {
                "preset": "Web",
                "extension": ".html"
            },
            "windows": {
                "preset": "Windows Desktop",
                "extension": ".exe"
            }
        }
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for target in self.export_targets:
            if target not in target_settings:
                results.append((target, False, f"알 수 없는 타겟: {target}"))
                continue
            
            settings = target_settings[target]
            output_file = f"game_{timestamp}{settings['extension']}"
            output_path = str(Path(output_dir) / target / output_file)
            
            success, msg = self.export_game(
                project_path, 
                settings["preset"], 
                output_path
            )
            results.append((target, success, msg))
        
        return results
    
    def validate_project(self, project_path: str) -> Tuple[bool, List[str]]:
        """
        프로젝트 유효성 검사
        
        Args:
            project_path: Godot 프로젝트 경로
        
        Returns:
            (유효 여부, 오류 목록)
        """
        errors = []
        project_dir = Path(project_path)
        
        # project.godot 존재 확인
        if not (project_dir / "project.godot").exists():
            errors.append("project.godot 파일이 없습니다")
        
        # export_presets.cfg 확인
        if not (project_dir / "export_presets.cfg").exists():
            errors.append("export_presets.cfg 파일이 없습니다 (내보내기 불가)")
        
        # 메인 씬 확인
        project_file = project_dir / "project.godot"
        if project_file.exists():
            content = project_file.read_text(encoding="utf-8")
            if 'run/main_scene="' not in content:
                errors.append("메인 씬이 설정되지 않았습니다")
        
        return len(errors) == 0, errors
    
    def create_export_presets(self, project_path: str) -> None:
        """
        기본 내보내기 프리셋 생성
        
        Args:
            project_path: Godot 프로젝트 경로
        """
        presets_content = """[preset.0]

name="Android"
platform="Android"
runnable=true
dedicated_server=false
custom_features=""
export_filter="all_resources"
include_filter=""
exclude_filter=""
export_path=""
encryption_include_filters=""
encryption_exclude_filters=""
encrypt_pck=false
encrypt_directory=false

[preset.0.options]

[preset.1]

name="Web"
platform="Web"
runnable=true
dedicated_server=false
custom_features=""
export_filter="all_resources"
include_filter=""
exclude_filter=""
export_path=""
encryption_include_filters=""
encryption_exclude_filters=""
encrypt_pck=false
encrypt_directory=false

[preset.1.options]

variant/extensions_support=false
vram_texture_compression/for_desktop=true
vram_texture_compression/for_mobile=false
html/export_icon=true
html/custom_html_shell=""
html/head_include=""
html/canvas_resize_policy=2
html/focus_canvas_on_start=true
html/experimental_virtual_keyboard=false
progressive_web_app/enabled=false
"""
        
        presets_path = Path(project_path) / "export_presets.cfg"
        presets_path.write_text(presets_content, encoding="utf-8")


# 사용 예시
def main():
    config = {
        "godot_path": "godot",  # 또는 절대 경로
        "export_targets": ["android", "html5"]
    }
    
    builder = GodotBuilder(config)
    
    project_path = "./game_project"
    output_dir = "./builds"
    
    # 프로젝트 검증
    is_valid, errors = builder.validate_project(project_path)
    if not is_valid:
        print("프로젝트 오류:")
        for err in errors:
            print(f"  - {err}")
        return
    
    # 빌드 실행
    results = builder.build_all_targets(project_path, output_dir)
    
    print("\n빌드 결과:")
    for target, success, msg in results:
        status = "✓" if success else "✗"
        print(f"  [{status}] {target}: {msg}")


if __name__ == "__main__":
    main()
