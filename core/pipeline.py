"""
메인 파이프라인 스크립트
트렌드 수집 → GDD 생성 → 슬랙 알림 → 빌드를 통합 실행
"""

import asyncio
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

# 모듈 임포트
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from crawler.tiktok_crawler import TikTokCrawler
from crawler.google_trends_crawler import GoogleTrendsCrawler
from gdd_generator.gdd_generator import GDDGenerator, GDD
from builder.godot_builder import GodotBuilder


class Pipeline:
    """초자동화 게임 개발 파이프라인"""
    
    def __init__(self, config_path: str = "config/project_config.json"):
        """
        Args:
            config_path: 프로젝트 설정 파일 경로
        """
        self.config = self._load_config(config_path)
        self.base_path = Path(__file__).parent.parent
        
        # 모듈 초기화
        self.tiktok_crawler = TikTokCrawler(self.config.get("crawler", {}))
        self.google_crawler = GoogleTrendsCrawler(self.config.get("crawler", {}))
        self.gdd_generator = GDDGenerator(self.config.get("llm", {}))
        self.godot_builder = GodotBuilder(self.config.get("godot", {}))
    
    def _load_config(self, config_path: str) -> dict:
        """설정 파일 로드"""
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"설정 파일을 찾을 수 없습니다: {config_path}")
            return {}
    
    async def run(self, template_type: str = "runner") -> Dict[str, Any]:
        """
        전체 파이프라인 실행
        
        Args:
            template_type: 사용할 게임 템플릿 유형
        
        Returns:
            파이프라인 실행 결과
        """
        result = {
            "success": False,
            "steps": [],
            "gdd": None,
            "build_path": None,
            "error": None
        }
        
        try:
            # 1단계: 트렌드 수집
            print("\n[1/5] 트렌드 데이터 수집 중...")
            tiktok_trends = await self._fetch_tiktok_trends()
            google_trends = self._fetch_google_trends(tiktok_trends)
            result["steps"].append({"step": "트렌드 수집", "status": "완료"})
            
            # 2단계: GDD 생성
            print("[2/5] 게임 기획 문서(GDD) 생성 중...")
            gdd = self.gdd_generator.generate_from_trends(
                tiktok_trends, 
                google_trends, 
                template_type
            )
            result["gdd"] = gdd
            result["steps"].append({"step": "GDD 생성", "status": "완료"})
            
            # 3단계: 슬랙 승인 요청 (시뮬레이션)
            print("[3/5] 슬랙 승인 대기 중...")
            approved = await self._request_slack_approval(gdd)
            if not approved:
                result["error"] = "운영자가 GDD를 반려했습니다"
                result["steps"].append({"step": "슬랙 승인", "status": "반려"})
                return result
            result["steps"].append({"step": "슬랙 승인", "status": "승인"})
            
            # 4단계: 템플릿 복사 및 스킨 적용
            print("[4/5] 게임 프로젝트 생성 중...")
            project_path = self._create_game_project(gdd, template_type)
            result["steps"].append({"step": "프로젝트 생성", "status": "완료"})
            
            # 5단계: 빌드
            print("[5/5] 게임 빌드 중...")
            build_results = self.godot_builder.build_all_targets(
                str(project_path),
                str(self.base_path / "builds")
            )
            
            all_success = all(r[1] for r in build_results)
            result["build_path"] = str(self.base_path / "builds")
            result["steps"].append({
                "step": "빌드", 
                "status": "완료" if all_success else "일부 실패",
                "details": build_results
            })
            
            result["success"] = all_success
            
        except Exception as e:
            result["error"] = str(e)
            result["steps"].append({"step": "오류", "status": str(e)})
        
        return result
    
    async def _fetch_tiktok_trends(self) -> list:
        """틱톡 트렌드 수집"""
        try:
            trends = await self.tiktok_crawler.fetch_trending_hashtags(
                max_results=self.config.get("crawler", {}).get("tiktok", {}).get("max_results", 20)
            )
            return [{"hashtag": t.hashtag, "view_count": t.view_count} for t in trends]
        except Exception as e:
            print(f"틱톡 크롤링 실패: {e}")
            # 테스트용 기본 데이터 반환
            return [{"hashtag": "#테스트챌린지", "view_count": 1000000}]
    
    def _fetch_google_trends(self, tiktok_trends: list) -> list:
        """구글 트렌드로 교차 검증"""
        keywords = [t["hashtag"].replace("#", "") for t in tiktok_trends[:5]]
        
        try:
            validated = self.google_crawler.validate_keywords(keywords)
            return [{"keyword": v.keyword, "interest": v.interest} for v in validated]
        except Exception as e:
            print(f"구글 트렌드 검증 실패: {e}")
            return [{"keyword": k, "interest": 50} for k in keywords]
    
    async def _request_slack_approval(self, gdd: GDD) -> bool:
        """
        슬랙 승인 요청 (시뮬레이션)
        
        실제 구현 시 n8n 워크플로우와 연동
        """
        print(f"  - 게임 제목: {gdd.game_title}")
        print(f"  - 템플릿: {gdd.template_type}")
        print(f"  - 코어 루프: {len(gdd.core_loop)}단계")
        
        # 자동 승인 (테스트용)
        # 실제 환경에서는 웹훅 대기
        await asyncio.sleep(1)
        return True
    
    def _create_game_project(self, gdd: GDD, template_type: str) -> Path:
        """템플릿 기반 게임 프로젝트 생성"""
        template_path = self.base_path / "templates" / f"template_{template_type}"
        
        # 타임스탬프로 고유 폴더명 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = gdd.game_title.replace(" ", "_")[:20]
        project_name = f"{timestamp}_{safe_title}"
        
        # 게임 폴더 경로
        game_path = self.base_path / "games" / template_type / project_name
        
        # 템플릿 복사
        if template_path.exists():
            shutil.copytree(template_path, game_path)
        else:
            game_path.mkdir(parents=True, exist_ok=True)
        
        # GDD 저장
        gdd_path = game_path / "gdd.json"
        self.gdd_generator.save_gdd(gdd, str(gdd_path))
        
        # 스킨 설정 업데이트 (향후 자산 생성 연동)
        
        return game_path
    
    def generate_report(self, result: Dict[str, Any]) -> str:
        """실행 결과 리포트 생성"""
        report = []
        report.append("=" * 50)
        report.append("파이프라인 실행 결과")
        report.append("=" * 50)
        
        report.append(f"\n상태: {'성공' if result['success'] else '실패'}")
        
        if result.get("gdd"):
            report.append(f"\n게임 제목: {result['gdd'].game_title}")
        
        report.append("\n단계별 결과:")
        for step in result.get("steps", []):
            status_icon = "✓" if step["status"] in ["완료", "승인"] else "✗"
            report.append(f"  [{status_icon}] {step['step']}: {step['status']}")
        
        if result.get("error"):
            report.append(f"\n오류: {result['error']}")
        
        if result.get("build_path"):
            report.append(f"\n빌드 경로: {result['build_path']}")
        
        return "\n".join(report)


async def main():
    """파이프라인 테스트 실행"""
    config_path = "config/project_config.json"
    
    pipeline = Pipeline(config_path)
    result = await pipeline.run("runner")
    
    report = pipeline.generate_report(result)
    print(report)


if __name__ == "__main__":
    asyncio.run(main())
