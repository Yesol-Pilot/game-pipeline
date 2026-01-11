"""
다국어 GDD 생성 모듈
다국어 게임 기획 문서 및 스토어 등록 정보 생성
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class LocalizedContent:
    """다국어 콘텐츠"""
    locale: str  # ko-KR, en-US, ja-JP 등
    title: str
    short_description: str
    full_description: str
    keywords: List[str] = field(default_factory=list)
    release_notes: str = ""


@dataclass
class MultilingualGDD:
    """다국어 GDD"""
    game_id: str
    base_locale: str
    localizations: Dict[str, LocalizedContent]
    
    # 공통 정보 (언어 무관)
    template_type: str
    core_loop: List[str]
    mechanics: List[str]
    art_style: Dict[str, Any]
    assets_required: List[Dict[str, Any]]
    
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def get_localization(self, locale: str) -> Optional[LocalizedContent]:
        """특정 언어 콘텐츠 조회"""
        return self.localizations.get(locale)
    
    def get_or_fallback(self, locale: str) -> LocalizedContent:
        """특정 언어 또는 기본 언어 콘텐츠"""
        return self.localizations.get(locale, self.localizations.get(self.base_locale))


class MultilingualGDDGenerator:
    """다국어 GDD 생성기"""
    
    # 지원 언어
    SUPPORTED_LOCALES = {
        "ko-KR": "한국어",
        "en-US": "English",
        "ja-JP": "日本語",
        "zh-CN": "简体中文",
        "zh-TW": "繁體中文",
        "es-ES": "Español",
        "de-DE": "Deutsch",
        "fr-FR": "Français",
        "pt-BR": "Português",
        "ru-RU": "Русский",
    }
    
    # 게임 장르 번역
    GENRE_TRANSLATIONS = {
        "runner": {
            "ko-KR": "무한 러너",
            "en-US": "Endless Runner",
            "ja-JP": "エンドレスランナー",
            "zh-CN": "无尽跑酷",
        },
        "puzzle": {
            "ko-KR": "퍼즐 게임",
            "en-US": "Puzzle Game",
            "ja-JP": "パズルゲーム",
            "zh-CN": "益智游戏",
        },
        "clicker": {
            "ko-KR": "클리커 게임",
            "en-US": "Clicker Game",
            "ja-JP": "クリッカーゲーム",
            "zh-CN": "点击游戏",
        },
        "match3": {
            "ko-KR": "매치3 퍼즐",
            "en-US": "Match-3 Puzzle",
            "ja-JP": "マッチ3パズル",
            "zh-CN": "三消游戏",
        },
        "rhythm": {
            "ko-KR": "리듬 게임",
            "en-US": "Rhythm Game",
            "ja-JP": "リズムゲーム",
            "zh-CN": "节奏游戏",
        },
        "idle": {
            "ko-KR": "방치형 RPG",
            "en-US": "Idle RPG",
            "ja-JP": "放置系RPG",
            "zh-CN": "放置RPG",
        },
    }
    
    def __init__(self, config: dict):
        self.config = config
        self.llm_provider = config.get("llm_provider", "gemini")
        self.target_locales = config.get("target_locales", ["ko-KR", "en-US"])
    
    def generate_multilingual(
        self,
        base_gdd: Any,
        target_locales: List[str] = None
    ) -> MultilingualGDD:
        """
        기본 GDD에서 다국어 버전 생성
        
        Args:
            base_gdd: 기본 GDD (한국어)
            target_locales: 대상 언어 목록
        
        Returns:
            다국어 GDD
        """
        if target_locales is None:
            target_locales = self.target_locales
        
        localizations = {}
        
        for locale in target_locales:
            content = self._generate_localization(base_gdd, locale)
            localizations[locale] = content
        
        return MultilingualGDD(
            game_id=getattr(base_gdd, "game_id", f"game_{datetime.now().strftime('%Y%m%d')}"),
            base_locale="ko-KR",
            localizations=localizations,
            template_type=getattr(base_gdd, "template_type", "runner"),
            core_loop=getattr(base_gdd, "core_loop", []),
            mechanics=getattr(base_gdd, "mechanics", []),
            art_style=getattr(base_gdd, "art_style", {}),
            assets_required=getattr(base_gdd, "assets_required", [])
        )
    
    def _generate_localization(self, base_gdd: Any, locale: str) -> LocalizedContent:
        """특정 언어 콘텐츠 생성"""
        
        # 기본 정보 추출
        base_title = getattr(base_gdd, "game_title", "게임")
        template_type = getattr(base_gdd, "template_type", "runner")
        
        # 장르명 번역
        genre_name = self.GENRE_TRANSLATIONS.get(template_type, {}).get(locale, template_type)
        
        # 언어별 콘텐츠 생성 (LLM 사용 시 여기서 API 호출)
        if locale == "ko-KR":
            content = self._generate_korean(base_gdd, genre_name)
        elif locale == "en-US":
            content = self._generate_english(base_gdd, genre_name)
        elif locale == "ja-JP":
            content = self._generate_japanese(base_gdd, genre_name)
        else:
            content = self._generate_default(base_gdd, locale, genre_name)
        
        return content
    
    def _generate_korean(self, gdd: Any, genre_name: str) -> LocalizedContent:
        """한국어 콘텐츠"""
        title = getattr(gdd, "game_title", "트렌드 게임")
        
        return LocalizedContent(
            locale="ko-KR",
            title=title,
            short_description=f"중독성 강한 {genre_name}! 지금 바로 도전하세요!",
            full_description=f"""🎮 {title}

{genre_name}의 새로운 기준!

✨ 특징
• 간단한 원터치 조작
• 끝없는 도전과 기록 갱신
• 아름다운 그래픽과 사운드

🏆 지금 다운로드하고 도전하세요!""",
            keywords=["게임", genre_name, "캐주얼", "모바일", "무료"],
            release_notes="첫 번째 릴리스"
        )
    
    def _generate_english(self, gdd: Any, genre_name: str) -> LocalizedContent:
        """영어 콘텐츠"""
        title = getattr(gdd, "game_title", "Trend Game")
        # 간단한 영문 제목 변환
        en_title = title.replace("게임", "Game").replace("러너", "Runner")
        
        return LocalizedContent(
            locale="en-US",
            title=en_title,
            short_description=f"Addictive {genre_name}! Challenge yourself now!",
            full_description=f"""🎮 {en_title}

The new standard of {genre_name}!

✨ Features
• Simple one-touch controls
• Endless challenges and high scores
• Beautiful graphics and sound

🏆 Download now and start your challenge!""",
            keywords=["game", genre_name.lower(), "casual", "mobile", "free"],
            release_notes="Initial release"
        )
    
    def _generate_japanese(self, gdd: Any, genre_name: str) -> LocalizedContent:
        """일본어 콘텐츠"""
        title = getattr(gdd, "game_title", "トレンドゲーム")
        
        return LocalizedContent(
            locale="ja-JP",
            title=title,
            short_description=f"中毒性抜群の{genre_name}！今すぐチャレンジ！",
            full_description=f"""🎮 {title}

{genre_name}の新基準！

✨ 特徴
• シンプルなワンタッチ操作
• 終わりなき挑戦とハイスコア
• 美しいグラフィックとサウンド

🏆 今すぐダウンロードして挑戦しよう！""",
            keywords=["ゲーム", genre_name, "カジュアル", "モバイル", "無料"],
            release_notes="初回リリース"
        )
    
    def _generate_default(self, gdd: Any, locale: str, genre_name: str) -> LocalizedContent:
        """기본 콘텐츠 (영어 기반)"""
        en_content = self._generate_english(gdd, genre_name)
        en_content.locale = locale
        return en_content
    
    def export_store_listings(self, multilingual_gdd: MultilingualGDD) -> Dict[str, Dict]:
        """스토어 등록 정보 내보내기"""
        listings = {}
        
        for locale, content in multilingual_gdd.localizations.items():
            listings[locale] = {
                "title": content.title,
                "short_description": content.short_description[:80],
                "full_description": content.full_description,
                "keywords": content.keywords,
                "release_notes": content.release_notes
            }
        
        return listings


# 사용 예시
def main():
    from dataclasses import dataclass
    
    @dataclass
    class MockGDD:
        game_title = "트렌드 러너"
        template_type = "runner"
        core_loop = ["달리기", "점프", "장애물 회피"]
        mechanics = ["터치 점프", "더블 점프"]
        art_style = {"style": "pixel-art"}
        assets_required = []
    
    generator = MultilingualGDDGenerator({
        "target_locales": ["ko-KR", "en-US", "ja-JP"]
    })
    
    multilingual = generator.generate_multilingual(MockGDD())
    
    print("=== 다국어 GDD ===")
    for locale, content in multilingual.localizations.items():
        print(f"\n[{locale}]")
        print(f"  제목: {content.title}")
        print(f"  설명: {content.short_description}")
    
    listings = generator.export_store_listings(multilingual)
    print(f"\n스토어 등록 정보: {len(listings)}개 언어")


if __name__ == "__main__":
    main()
