"""
자동 스크린샷 생성
게임 스크린샷 및 스토어 프로모션 이미지 생성
"""

import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ScreenshotConfig:
    """스크린샷 설정"""
    width: int = 1080
    height: int = 1920
    format: str = "png"
    quality: int = 95


@dataclass
class Screenshot:
    """스크린샷 정보"""
    filename: str
    path: str
    width: int
    height: int
    category: str  # gameplay, menu, store
    created_at: datetime


class ScreenshotGenerator:
    """스크린샷 생성기"""
    
    # 스토어별 요구 사항
    STORE_REQUIREMENTS = {
        "google_play": {
            "feature_graphic": (1024, 500),
            "phone_screenshots": [(1080, 1920), (1080, 1920), (1080, 1920)],
            "tablet_screenshots": [(1920, 1200), (1920, 1200)],
        },
        "app_store": {
            "iphone_6.5": [(1284, 2778), (1284, 2778), (1284, 2778)],
            "iphone_5.5": [(1242, 2208), (1242, 2208)],
            "ipad_12.9": [(2048, 2732), (2048, 2732)],
        },
        "steam": {
            "header_capsule": (460, 215),
            "small_capsule": (231, 87),
            "main_capsule": (616, 353),
            "screenshots": [(1920, 1080), (1920, 1080), (1920, 1080), (1920, 1080)],
        }
    }
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.output_dir = Path(self.config.get("output_dir", "screenshots"))
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    async def capture_from_godot(
        self,
        project_path: str,
        scene_path: str,
        output_path: str,
        config: ScreenshotConfig = None
    ) -> Optional[Screenshot]:
        """
        Godot 프로젝트에서 스크린샷 캡처
        
        Note: Godot 헤드리스 모드로 캡처
        """
        if config is None:
            config = ScreenshotConfig()
        
        import subprocess
        
        try:
            # Godot 스크린샷 스크립트 생성
            script = f'''
extends SceneTree
func _init():
    var viewport = get_root().get_viewport()
    viewport.size = Vector2({config.width}, {config.height})
    
    # 씬 로드 및 캡처
    var scene = load("{scene_path}").instantiate()
    get_root().add_child(scene)
    
    await get_tree().create_timer(0.5).timeout
    
    var image = viewport.get_texture().get_image()
    image.save_png("{output_path}")
    
    quit()
'''
            
            script_path = Path(project_path) / "_screenshot_script.gd"
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(script)
            
            # Godot 실행
            result = subprocess.run([
                "godot", "--headless",
                "--path", project_path,
                "--script", str(script_path),
                "--quit"
            ], capture_output=True, timeout=30)
            
            # 스크립트 정리
            script_path.unlink(missing_ok=True)
            
            if Path(output_path).exists():
                return Screenshot(
                    filename=Path(output_path).name,
                    path=output_path,
                    width=config.width,
                    height=config.height,
                    category="gameplay",
                    created_at=datetime.now()
                )
            
        except FileNotFoundError:
            print("Godot를 찾을 수 없습니다. 시뮬레이션 모드로 전환.")
            return self._generate_placeholder(output_path, config)
        except Exception as e:
            print(f"스크린샷 캡처 오류: {e}")
        
        return None
    
    def _generate_placeholder(
        self,
        output_path: str,
        config: ScreenshotConfig
    ) -> Screenshot:
        """플레이스홀더 이미지 생성"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # 그라데이션 배경
            img = Image.new('RGB', (config.width, config.height))
            draw = ImageDraw.Draw(img)
            
            for y in range(config.height):
                r = int(30 + (y / config.height) * 50)
                g = int(20 + (y / config.height) * 40)
                b = int(60 + (y / config.height) * 80)
                draw.line([(0, y), (config.width, y)], fill=(r, g, b))
            
            # 텍스트
            text = f"Screenshot\n{config.width}x{config.height}"
            try:
                font = ImageFont.truetype("arial.ttf", 48)
            except:
                font = ImageFont.load_default()
            
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (config.width - text_width) // 2
            y = (config.height - text_height) // 2
            draw.text((x, y), text, fill=(255, 255, 255), font=font)
            
            img.save(output_path)
            
        except ImportError:
            # PIL 없으면 빈 파일
            Path(output_path).touch()
        
        return Screenshot(
            filename=Path(output_path).name,
            path=output_path,
            width=config.width,
            height=config.height,
            category="placeholder",
            created_at=datetime.now()
        )
    
    def generate_store_assets(
        self,
        game_id: str,
        store: str,
        base_screenshots: List[str] = None
    ) -> Dict[str, List[Screenshot]]:
        """
        스토어용 자산 생성
        
        Args:
            game_id: 게임 ID
            store: 스토어 이름 (google_play, app_store, steam)
            base_screenshots: 기본 스크린샷 경로들
        
        Returns:
            카테고리별 스크린샷
        """
        if store not in self.STORE_REQUIREMENTS:
            print(f"지원하지 않는 스토어: {store}")
            return {}
        
        requirements = self.STORE_REQUIREMENTS[store]
        results = {}
        
        store_dir = self.output_dir / game_id / store
        store_dir.mkdir(parents=True, exist_ok=True)
        
        for category, sizes in requirements.items():
            results[category] = []
            
            if isinstance(sizes, tuple):
                # 단일 이미지
                sizes = [sizes]
            
            for i, size in enumerate(sizes):
                width, height = size
                filename = f"{category}_{i+1}.png"
                output_path = str(store_dir / filename)
                
                config = ScreenshotConfig(width=width, height=height)
                screenshot = self._generate_placeholder(output_path, config)
                screenshot.category = category
                results[category].append(screenshot)
        
        return results
    
    def generate_promo_image(
        self,
        game_title: str,
        tagline: str,
        output_path: str,
        width: int = 1200,
        height: int = 630
    ) -> Optional[Screenshot]:
        """
        프로모션 이미지 생성 (소셜 미디어용)
        """
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            img = Image.new('RGB', (width, height))
            draw = ImageDraw.Draw(img)
            
            # 그라데이션 배경
            for y in range(height):
                r = int(20 + (y / height) * 60)
                g = int(10 + (y / height) * 40)
                b = int(80 + (y / height) * 100)
                draw.line([(0, y), (width, y)], fill=(r, g, b))
            
            # 제목
            try:
                title_font = ImageFont.truetype("arial.ttf", 72)
                tagline_font = ImageFont.truetype("arial.ttf", 36)
            except:
                title_font = ImageFont.load_default()
                tagline_font = title_font
            
            # 제목 중앙 배치
            bbox = draw.textbbox((0, 0), game_title, font=title_font)
            title_x = (width - (bbox[2] - bbox[0])) // 2
            draw.text((title_x, height // 3), game_title, fill=(255, 255, 255), font=title_font)
            
            # 태그라인
            bbox = draw.textbbox((0, 0), tagline, font=tagline_font)
            tagline_x = (width - (bbox[2] - bbox[0])) // 2
            draw.text((tagline_x, height // 2), tagline, fill=(200, 200, 200), font=tagline_font)
            
            img.save(output_path)
            
            return Screenshot(
                filename=Path(output_path).name,
                path=output_path,
                width=width,
                height=height,
                category="promo",
                created_at=datetime.now()
            )
            
        except ImportError:
            print("PIL 필요: pip install Pillow")
            return None


# 사용 예시
def main():
    generator = ScreenshotGenerator({"output_dir": "screenshots"})
    
    # 스토어 자산 생성
    assets = generator.generate_store_assets("game_001", "google_play")
    
    print("=== 생성된 자산 ===")
    for category, screenshots in assets.items():
        print(f"\n{category}:")
        for ss in screenshots:
            print(f"  - {ss.filename} ({ss.width}x{ss.height})")
    
    # 프로모션 이미지
    promo = generator.generate_promo_image(
        "트렌드 러너",
        "중독성 강한 무한 러너 게임!",
        "screenshots/promo.png"
    )
    
    if promo:
        print(f"\n프로모션 이미지: {promo.filename}")


if __name__ == "__main__":
    main()
