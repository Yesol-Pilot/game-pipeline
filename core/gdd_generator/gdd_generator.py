"""
GDD 생성 모듈
LLM을 사용하여 트렌드 데이터로부터 게임 기획 문서 생성
"""

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path


@dataclass
class GDD:
    """게임 기획 문서 (Game Design Document) 구조"""
    game_title: str
    trend_source: Dict[str, Any]
    core_loop: List[str]
    mechanics: List[str]
    art_style: Dict[str, Any]
    assets_required: List[Dict[str, str]]
    monetization: Dict[str, Any]
    template_type: str
    character_dna: Optional[Dict[str, Any]] = None
    difficulty: Optional[Dict[str, float]] = None
    created_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


class GDDGenerator:
    """GDD 생성기"""
    
    def __init__(self, config: dict):
        """
        Args:
            config: LLM 설정 (provider, model, api_key 등)
        """
        self.config = config
        self.schema_path = config.get("schema_path", "schemas/gdd_schema.json")
        self._load_schema()
    
    def _load_schema(self) -> None:
        """GDD JSON 스키마 로드"""
        try:
            with open(self.schema_path, "r", encoding="utf-8") as f:
                self.schema = json.load(f)
        except FileNotFoundError:
            print(f"경고: 스키마 파일을 찾을 수 없습니다: {self.schema_path}")
            self.schema = None
    
    def generate_from_trends(
        self, 
        tiktok_trends: List[dict], 
        google_trends: List[dict],
        template_type: str = "runner"
    ) -> GDD:
        """
        트렌드 데이터로부터 GDD 생성
        
        Args:
            tiktok_trends: 틱톡 트렌드 데이터
            google_trends: 구글 트렌드 데이터
            template_type: 사용할 게임 템플릿 유형
        
        Returns:
            생성된 GDD
        """
        # 트렌드 분석
        primary_trend = self._select_primary_trend(tiktok_trends, google_trends)
        
        # LLM 프롬프트 생성
        prompt = self._build_prompt(primary_trend, template_type)
        
        # LLM 호출 (실제 구현 시 API 연동 필요)
        gdd_data = self._call_llm(prompt)
        
        # GDD 객체 생성
        return self._parse_gdd(gdd_data, primary_trend, template_type)
    
    def _select_primary_trend(
        self, 
        tiktok_trends: List[dict], 
        google_trends: List[dict]
    ) -> dict:
        """주요 트렌드 선택 (조회수 + 검색량 기준)"""
        if not tiktok_trends:
            return {"hashtag": "기본", "view_count": 0}
        
        # 교차 검증된 트렌드 중 상위 선택
        validated = []
        google_keywords = {t.get("keyword", "") for t in google_trends}
        
        for trend in tiktok_trends:
            hashtag = trend.get("hashtag", "").replace("#", "")
            if hashtag in google_keywords:
                validated.append(trend)
        
        if validated:
            return max(validated, key=lambda x: x.get("view_count", 0))
        
        return tiktok_trends[0]
    
    def _build_prompt(self, trend: dict, template_type: str) -> str:
        """LLM 프롬프트 생성"""
        template_descriptions = {
            "runner": "무한 러너 게임 (달리기, 점프, 장애물 회피)",
            "puzzle": "물리 퍼즐 게임 (드래그, 발사, 목표 달성)",
            "clicker": "클리커/방치형 게임 (터치, 업그레이드, 자동화)",
            "match3": "매치-3 게임 (스와이프, 매칭, 콤보)",
            "arcade": "아케이드 게임 (조준, 발사, 점수 경쟁)",
        }
        
        template_desc = template_descriptions.get(template_type, "하이퍼 캐주얼 게임")
        hashtag = trend.get("hashtag", "트렌드")
        
        prompt = f"""
당신은 하이퍼 캐주얼 게임 기획자입니다.
다음 트렌드를 기반으로 {template_desc}을 기획해주세요.

[트렌드 정보]
- 해시태그: {hashtag}
- 조회수: {trend.get("view_count", "N/A")}

[출력 형식]
반드시 유효한 JSON 형식으로 출력하세요.
필수 필드: game_title, core_loop, mechanics, art_style, assets_required

[게임 유형]
{template_desc}

[지시사항]
1. 트렌드를 반영한 매력적인 게임 제목 생성
2. 3-5단계의 핵심 게임 루프 정의
3. 구체적인 조작 방식 3개 이상 제시
4. 이미지 생성 API에 적합한 아트 스타일 프롬프트 작성
5. 필요한 에셋 목록 (player, obstacle, background 등)
"""
        return prompt
    
    def _call_llm(self, prompt: str) -> dict:
        """
        LLM API 호출
        
        실제 구현 시 Gemini, GPT-4 등 API 연동 필요
        """
        provider = self.config.get("provider", "gemini")
        
        # 플레이스홀더 응답 (실제 API 호출로 대체)
        placeholder_response = {
            "game_title": "트렌드 러너",
            "core_loop": [
                "플레이어가 자동으로 달린다",
                "터치 시 점프한다",
                "장애물과 충돌하면 게임 오버",
                "거리에 따라 점수 획득"
            ],
            "mechanics": [
                "화면 터치 시 점프",
                "더블 점프 가능",
                "코인 수집"
            ],
            "art_style": {
                "style_prompt": "Pixel art style, vibrant colors, cute characters",
                "color_palette": ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4"]
            },
            "assets_required": [
                {"asset_id": "player", "asset_type": "player", "generation_prompt": "A cute pixel art character running"},
                {"asset_id": "obstacle", "asset_type": "obstacle", "generation_prompt": "A pixel art obstacle"},
                {"asset_id": "background", "asset_type": "background", "generation_prompt": "A colorful pixel art background"}
            ],
            "monetization": {
                "ad_placements": ["interstitial", "rewarded"],
                "iap_items": ["광고 제거", "더블 코인"]
            }
        }
        
        return placeholder_response
    
    def _parse_gdd(self, gdd_data: dict, trend: dict, template_type: str) -> GDD:
        """GDD 객체로 파싱"""
        return GDD(
            game_title=gdd_data.get("game_title", "무제"),
            trend_source={
                "tiktok_hashtags": [trend.get("hashtag", "")],
                "collected_at": datetime.now().isoformat()
            },
            core_loop=gdd_data.get("core_loop", []),
            mechanics=gdd_data.get("mechanics", []),
            art_style=gdd_data.get("art_style", {}),
            assets_required=gdd_data.get("assets_required", []),
            monetization=gdd_data.get("monetization", {}),
            template_type=template_type,
            character_dna=gdd_data.get("character_dna"),
            difficulty=gdd_data.get("difficulty"),
        )
    
    def validate_gdd(self, gdd: GDD) -> tuple[bool, List[str]]:
        """GDD 유효성 검증"""
        errors = []
        
        if not gdd.game_title:
            errors.append("game_title 누락")
        if not gdd.core_loop or len(gdd.core_loop) < 3:
            errors.append("core_loop은 최소 3단계 필요")
        if not gdd.mechanics:
            errors.append("mechanics 누락")
        if not gdd.assets_required:
            errors.append("assets_required 누락")
        
        return len(errors) == 0, errors
    
    def save_gdd(self, gdd: GDD, filepath: str) -> None:
        """GDD를 JSON 파일로 저장"""
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(asdict(gdd), f, ensure_ascii=False, indent=2)


# 사용 예시
def main():
    config = {
        "provider": "gemini",
        "model": "gemini-1.5-pro",
        "schema_path": "schemas/gdd_schema.json"
    }
    
    generator = GDDGenerator(config)
    
    # 테스트 트렌드 데이터
    tiktok_trends = [
        {"hashtag": "#댄스챌린지", "view_count": 1500000}
    ]
    google_trends = [
        {"keyword": "댄스챌린지", "interest": 75}
    ]
    
    # GDD 생성
    gdd = generator.generate_from_trends(tiktok_trends, google_trends, "runner")
    
    # 유효성 검증
    is_valid, errors = generator.validate_gdd(gdd)
    print(f"GDD 유효성: {is_valid}")
    if errors:
        print(f"오류: {errors}")
    
    # 저장
    generator.save_gdd(gdd, "generated_gdd.json")
    print(f"GDD 저장 완료: {gdd.game_title}")


if __name__ == "__main__":
    main()
