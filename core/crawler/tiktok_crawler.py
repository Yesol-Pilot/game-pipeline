"""
틱톡 크리에이티브 센터 크롤러 모듈
트렌드 데이터 수집을 위한 브라우저 자동화
"""

import asyncio
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
import json

# Playwright를 사용한 브라우저 자동화
# pip install playwright playwright-stealth
# playwright install chromium


@dataclass
class TrendData:
    """트렌드 데이터 구조"""
    hashtag: str
    view_count: int
    video_count: int
    description: str
    collected_at: datetime
    source: str = "tiktok"


class TikTokCrawler:
    """틱톡 크리에이티브 센터 크롤러"""
    
    def __init__(self, config: dict):
        """
        Args:
            config: 크롤러 설정 (프록시, 타겟 섹션 등)
        """
        self.config = config
        self.browser = None
        self.page = None
        self.target_url = "https://ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag/pc/en"
    
    async def init_browser(self) -> None:
        """브라우저 초기화 (Stealth 모드)"""
        try:
            from playwright.async_api import async_playwright
            from playwright_stealth import stealth_async
            
            self.playwright = await async_playwright().start()
            
            # 프록시 설정
            launch_options = {
                "headless": True,
            }
            
            if self.config.get("proxy"):
                launch_options["proxy"] = {
                    "server": self.config["proxy"]["server"],
                    "username": self.config["proxy"].get("username"),
                    "password": self.config["proxy"].get("password"),
                }
            
            self.browser = await self.playwright.chromium.launch(**launch_options)
            self.page = await self.browser.new_page()
            
            # Stealth 모드 적용 (탐지 회피)
            await stealth_async(self.page)
            
        except ImportError:
            print("경고: playwright 또는 playwright-stealth가 설치되지 않았습니다.")
            print("pip install playwright playwright-stealth 실행 후 playwright install chromium")
            raise
    
    async def fetch_trending_hashtags(self, max_results: int = 20) -> List[TrendData]:
        """트렌딩 해시태그 수집"""
        if not self.page:
            await self.init_browser()
        
        trends = []
        
        try:
            await self.page.goto(self.target_url, wait_until="networkidle")
            await asyncio.sleep(2)  # 동적 콘텐츠 로딩 대기
            
            # 트렌드 항목 추출 (셀렉터는 실제 사이트에 맞게 조정 필요)
            items = await self.page.query_selector_all(".trending-item")
            
            for item in items[:max_results]:
                hashtag = await item.query_selector(".hashtag-name")
                view_count = await item.query_selector(".view-count")
                
                if hashtag:
                    trend = TrendData(
                        hashtag=await hashtag.inner_text(),
                        view_count=self._parse_count(await view_count.inner_text() if view_count else "0"),
                        video_count=0,
                        description="",
                        collected_at=datetime.now(),
                    )
                    trends.append(trend)
            
        except Exception as e:
            print(f"크롤링 오류: {e}")
        
        return trends
    
    def _parse_count(self, count_str: str) -> int:
        """조회수 문자열을 숫자로 변환 (예: 1.2M -> 1200000)"""
        count_str = count_str.strip().upper()
        multipliers = {"K": 1000, "M": 1000000, "B": 1000000000}
        
        for suffix, mult in multipliers.items():
            if count_str.endswith(suffix):
                return int(float(count_str[:-1]) * mult)
        
        try:
            return int(count_str.replace(",", ""))
        except ValueError:
            return 0
    
    async def close(self) -> None:
        """브라우저 종료"""
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
    
    def save_results(self, trends: List[TrendData], filepath: str) -> None:
        """결과를 JSON 파일로 저장"""
        data = [
            {
                "hashtag": t.hashtag,
                "view_count": t.view_count,
                "video_count": t.video_count,
                "description": t.description,
                "collected_at": t.collected_at.isoformat(),
                "source": t.source,
            }
            for t in trends
        ]
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


# 사용 예시
async def main():
    config = {
        "proxy": None,  # 주거용 프록시 설정 시 활성화
        "max_results": 20,
    }
    
    crawler = TikTokCrawler(config)
    
    try:
        trends = await crawler.fetch_trending_hashtags()
        print(f"수집된 트렌드: {len(trends)}개")
        
        for trend in trends[:5]:
            print(f"  - {trend.hashtag}: {trend.view_count:,}회")
        
        crawler.save_results(trends, "tiktok_trends.json")
        
    finally:
        await crawler.close()


if __name__ == "__main__":
    asyncio.run(main())
