"""
자산 생성 모듈
Stability AI (Stable Diffusion) API를 사용한 게임 자산 자동 생성
"""

import base64
import json
import urllib.request
import urllib.parse
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any


@dataclass
class GeneratedAsset:
    """생성된 자산 정보"""
    asset_id: str
    asset_type: str
    prompt: str
    file_path: str
    generated_at: datetime
    seed: Optional[int] = None


class AssetGenerator:
    """자산 생성기 - Stability AI API 연동"""
    
    def __init__(self, config: dict):
        """
        Args:
            config: API 설정 (api_key, style_strength 등)
        """
        self.config = config
        self.api_key = config.get("api_key", "")
        self.api_host = config.get("api_host", "https://api.stability.ai")
        self.style_strength = config.get("style_strength", 0.5)
        self.negative_prompt = config.get(
            "negative_prompt", 
            "blurry, inconsistent, mixed styles, low quality, watermark"
        )
    
    def generate_sprite(
        self,
        prompt: str,
        output_path: str,
        width: int = 512,
        height: int = 512,
        style_preset: str = "pixel-art"
    ) -> Optional[GeneratedAsset]:
        """
        스프라이트 이미지 생성
        
        Args:
            prompt: 이미지 생성 프롬프트
            output_path: 출력 파일 경로
            width: 이미지 너비
            height: 이미지 높이
            style_preset: 스타일 프리셋 (pixel-art, anime, photographic 등)
        
        Returns:
            생성된 자산 정보 또는 None
        """
        if not self.api_key:
            print("경고: Stability AI API 키가 설정되지 않았습니다")
            return self._generate_placeholder(prompt, output_path)
        
        try:
            # API 요청 생성
            full_prompt = self._build_prompt(prompt, style_preset)
            
            result = self._call_api(
                full_prompt,
                width=width,
                height=height,
                style_preset=style_preset
            )
            
            if result:
                # 이미지 저장
                Path(output_path).parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, "wb") as f:
                    f.write(result["image_data"])
                
                return GeneratedAsset(
                    asset_id=Path(output_path).stem,
                    asset_type="sprite",
                    prompt=full_prompt,
                    file_path=output_path,
                    generated_at=datetime.now(),
                    seed=result.get("seed")
                )
            
        except Exception as e:
            print(f"자산 생성 오류: {e}")
        
        return self._generate_placeholder(prompt, output_path)
    
    def generate_spritesheet(
        self,
        prompt: str,
        output_path: str,
        frames: int = 4,
        width: int = 512,
        height: int = 128
    ) -> Optional[GeneratedAsset]:
        """
        스프라이트 시트 생성
        
        Args:
            prompt: 기본 프롬프트
            output_path: 출력 파일 경로
            frames: 프레임 수
            width: 전체 너비
            height: 높이
        """
        spritesheet_prompt = (
            f"A sprite sheet of {prompt}, side view, {frames} frames, "
            f"white background, separate elements, game asset"
        )
        
        return self.generate_sprite(
            spritesheet_prompt,
            output_path,
            width=width,
            height=height,
            style_preset="pixel-art"
        )
    
    def generate_from_gdd(
        self,
        gdd: Any,
        output_dir: str
    ) -> List[GeneratedAsset]:
        """
        GDD의 assets_required를 기반으로 모든 자산 생성
        
        Args:
            gdd: 게임 기획 문서
            output_dir: 출력 디렉토리
        
        Returns:
            생성된 자산 목록
        """
        generated = []
        output_path = Path(output_dir)
        
        # 아트 스타일 추출
        art_style = ""
        if hasattr(gdd, "art_style") and gdd.art_style:
            art_style = gdd.art_style.get("style_prompt", "")
        
        # 캐릭터 DNA 추출
        character_dna = ""
        if hasattr(gdd, "character_dna") and gdd.character_dna:
            character_dna = gdd.character_dna.get("main_character", "")
        
        # 각 자산 생성
        for asset in getattr(gdd, "assets_required", []):
            asset_id = asset.get("asset_id", "unknown")
            asset_type = asset.get("asset_type", "sprite")
            base_prompt = asset.get("generation_prompt", asset.get("prompt_template", ""))
            filename = asset.get("filename", f"{asset_id}.png")
            
            # 프롬프트 변수 치환
            prompt = base_prompt
            prompt = prompt.replace("{character_dna}", character_dna)
            prompt = prompt.replace("{art_style}", art_style)
            
            # 파일 경로
            file_path = str(output_path / "assets" / "sprites" / filename)
            
            # 자산 유형에 따른 생성
            if asset_type == "spritesheet":
                result = self.generate_spritesheet(prompt, file_path)
            else:
                result = self.generate_sprite(prompt, file_path)
            
            if result:
                generated.append(result)
                print(f"  ✓ 생성됨: {asset_id}")
            else:
                print(f"  ✗ 실패: {asset_id}")
        
        return generated
    
    def _build_prompt(self, base_prompt: str, style_preset: str) -> str:
        """전체 프롬프트 구성"""
        style_additions = {
            "pixel-art": "pixel art style, 8-bit, retro game",
            "anime": "anime style, cel shaded, vibrant colors",
            "photographic": "photorealistic, high detail",
            "digital-art": "digital art, clean lines, game asset",
        }
        
        style_text = style_additions.get(style_preset, "")
        
        return f"{base_prompt}, {style_text}, white background, transparent"
    
    def _call_api(
        self,
        prompt: str,
        width: int,
        height: int,
        style_preset: str
    ) -> Optional[Dict[str, Any]]:
        """Stability AI API 호출"""
        url = f"{self.api_host}/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        body = {
            "text_prompts": [
                {"text": prompt, "weight": 1},
                {"text": self.negative_prompt, "weight": -1}
            ],
            "cfg_scale": 7,
            "width": width,
            "height": height,
            "samples": 1,
            "steps": 30,
            "style_preset": style_preset
        }
        
        try:
            data = json.dumps(body).encode("utf-8")
            req = urllib.request.Request(url, data=data, headers=headers, method="POST")
            
            with urllib.request.urlopen(req, timeout=60) as response:
                result = json.loads(response.read().decode("utf-8"))
                
                if result.get("artifacts"):
                    artifact = result["artifacts"][0]
                    return {
                        "image_data": base64.b64decode(artifact["base64"]),
                        "seed": artifact.get("seed")
                    }
        
        except Exception as e:
            print(f"API 호출 오류: {e}")
        
        return None
    
    def _generate_placeholder(
        self,
        prompt: str,
        output_path: str
    ) -> GeneratedAsset:
        """
        플레이스홀더 이미지 생성 (API 미사용 시)
        간단한 색상 사각형 PNG 생성
        """
        # 간단한 1x1 PNG 생성 (실제로는 더 큰 이미지 필요)
        # 여기서는 빈 파일 생성
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).touch()
        
        return GeneratedAsset(
            asset_id=Path(output_path).stem,
            asset_type="placeholder",
            prompt=prompt,
            file_path=output_path,
            generated_at=datetime.now()
        )
    
    def remove_background(self, input_path: str, output_path: str) -> bool:
        """
        배경 제거 (rembg 사용)
        
        pip install rembg 필요
        """
        try:
            from rembg import remove
            from PIL import Image
            
            input_img = Image.open(input_path)
            output_img = remove(input_img)
            output_img.save(output_path)
            return True
            
        except ImportError:
            print("경고: rembg가 설치되지 않았습니다. pip install rembg")
            return False
        except Exception as e:
            print(f"배경 제거 오류: {e}")
            return False


# 사용 예시
def main():
    config = {
        "api_key": "",  # Stability AI API 키
        "style_strength": 0.5,
        "negative_prompt": "blurry, low quality, watermark"
    }
    
    generator = AssetGenerator(config)
    
    # 단일 스프라이트 생성 테스트
    result = generator.generate_sprite(
        prompt="a cute robot character running",
        output_path="test_sprite.png",
        style_preset="pixel-art"
    )
    
    if result:
        print(f"생성 완료: {result.file_path}")
    else:
        print("생성 실패")


if __name__ == "__main__":
    main()
