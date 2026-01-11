"""
구글 트렌드 크롤러 모듈
pytrends를 사용한 검색 트렌드 수집
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict
import json

# pip install pytrends


@dataclass
class GoogleTrendData:
    """구글 트렌드 데이터 구조"""
    keyword: str
    interest: int  # 0-100 상대적 관심도
    related_queries: List[str]
    collected_at: datetime
    geo: str
    source: str = "google_trends"


class GoogleTrendsCrawler:
    """구글 트렌드 크롤러"""
    
    def __init__(self, config: dict):
        """
        Args:
            config: 크롤러 설정 (지역, 기간 등)
        """
        self.config = config
        self.pytrends = None
        self.geo = config.get("geo", "KR")  # 기본: 한국
        self.timeframe = config.get("timeframe", "now 1-d")  # 최근 24시간
    
    def _init_pytrends(self) -> None:
        """pytrends 초기화"""
        try:
            from pytrends.request import TrendReq
            self.pytrends = TrendReq(hl='ko-KR', tz=540)  # 한국 시간대
        except ImportError:
            print("경고: pytrends가 설치되지 않았습니다.")
            print("pip install pytrends")
            raise
    
    def validate_keywords(self, keywords: List[str]) -> List[GoogleTrendData]:
        """
        키워드 목록의 검색량 검증
        
        Args:
            keywords: 검증할 키워드 목록 (최대 5개)
        
        Returns:
            검증된 트렌드 데이터 목록
        """
        if not self.pytrends:
            self._init_pytrends()
        
        results = []
        
        # pytrends는 한 번에 최대 5개 키워드만 처리
        for i in range(0, len(keywords), 5):
            batch = keywords[i:i+5]
            batch_results = self._fetch_batch(batch)
            results.extend(batch_results)
        
        return results
    
    def _fetch_batch(self, keywords: List[str]) -> List[GoogleTrendData]:
        """키워드 배치 검색"""
        try:
            self.pytrends.build_payload(
                keywords,
                cat=0,
                timeframe=self.timeframe,
                geo=self.geo,
            )
            
            # 시간별 관심도
            interest_df = self.pytrends.interest_over_time()
            
            # 관련 검색어
            related = self.pytrends.related_queries()
            
            results = []
            for kw in keywords:
                interest = 0
                if not interest_df.empty and kw in interest_df.columns:
                    interest = int(interest_df[kw].mean())
                
                related_queries = []
                if kw in related and related[kw].get("top") is not None:
                    related_queries = related[kw]["top"]["query"].tolist()[:5]
                
                results.append(GoogleTrendData(
                    keyword=kw,
                    interest=interest,
                    related_queries=related_queries,
                    collected_at=datetime.now(),
                    geo=self.geo,
                ))
            
            return results
            
        except Exception as e:
            print(f"구글 트렌드 조회 오류: {e}")
            return []
    
    def get_realtime_trends(self) -> List[str]:
        """실시간 트렌드 키워드 조회"""
        if not self.pytrends:
            self._init_pytrends()
        
        try:
            trending = self.pytrends.realtime_trending_searches(pn='KR')
            return trending['title'].tolist()[:20]
        except Exception as e:
            print(f"실시간 트렌드 조회 오류: {e}")
            return []
    
    def cross_validate(self, tiktok_trends: List[dict]) -> List[dict]:
        """
        틱톡 트렌드와 구글 트렌드 교차 검증
        
        Args:
            tiktok_trends: 틱톡에서 수집한 트렌드 목록
        
        Returns:
            검색량이 검증된 트렌드 목록
        """
        keywords = [t.get("hashtag", "").replace("#", "") for t in tiktok_trends]
        validated = self.validate_keywords(keywords)
        
        # 관심도 50 이상인 것만 필터링
        threshold = self.config.get("interest_threshold", 50)
        
        valid_keywords = {v.keyword for v in validated if v.interest >= threshold}
        
        return [t for t in tiktok_trends 
                if t.get("hashtag", "").replace("#", "") in valid_keywords]
    
    def save_results(self, trends: List[GoogleTrendData], filepath: str) -> None:
        """결과를 JSON 파일로 저장"""
        data = [
            {
                "keyword": t.keyword,
                "interest": t.interest,
                "related_queries": t.related_queries,
                "collected_at": t.collected_at.isoformat(),
                "geo": t.geo,
                "source": t.source,
            }
            for t in trends
        ]
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


# 사용 예시
def main():
    config = {
        "geo": "KR",
        "timeframe": "now 1-d",
        "interest_threshold": 50,
    }
    
    crawler = GoogleTrendsCrawler(config)
    
    # 키워드 검증 테스트
    test_keywords = ["게임", "틱톡", "챌린지", "K팝", "AI"]
    results = crawler.validate_keywords(test_keywords)
    
    print("키워드 검증 결과:")
    for r in results:
        print(f"  - {r.keyword}: 관심도 {r.interest}")
        if r.related_queries:
            print(f"    관련 검색어: {', '.join(r.related_queries[:3])}")
    
    crawler.save_results(results, "google_trends.json")


if __name__ == "__main__":
    main()
