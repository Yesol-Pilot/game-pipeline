"""
A/B 테스트 시스템
게임 변형 테스트 및 성과 비교
"""

import json
import random
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict, field


@dataclass
class Variant:
    """A/B 테스트 변형"""
    variant_id: str
    name: str
    weight: float = 0.5  # 트래픽 비율
    config: Dict[str, Any] = field(default_factory=dict)
    
    # 성과 지표
    impressions: int = 0
    conversions: int = 0
    revenue: float = 0.0


@dataclass
class ABTest:
    """A/B 테스트 정의"""
    test_id: str
    name: str
    description: str
    game_id: str
    variants: List[Variant]
    
    status: str = "draft"  # draft, running, completed
    created_at: datetime = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


class ABTestManager:
    """A/B 테스트 매니저"""
    
    def __init__(self, data_dir: str = "ab_tests"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.tests: Dict[str, ABTest] = {}
        self._load_tests()
    
    def _load_tests(self) -> None:
        """저장된 테스트 로드"""
        tests_file = self.data_dir / "tests.json"
        if tests_file.exists():
            with open(tests_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                for test_id, test_data in data.items():
                    # Variant 객체 복원
                    variants = [Variant(**v) for v in test_data.pop("variants", [])]
                    
                    # datetime 복원
                    for dt_field in ["created_at", "started_at", "ended_at"]:
                        if test_data.get(dt_field):
                            test_data[dt_field] = datetime.fromisoformat(test_data[dt_field])
                    
                    self.tests[test_id] = ABTest(variants=variants, **test_data)
    
    def _save_tests(self) -> None:
        """테스트 저장"""
        data = {}
        for test_id, test in self.tests.items():
            test_dict = {
                "test_id": test.test_id,
                "name": test.name,
                "description": test.description,
                "game_id": test.game_id,
                "status": test.status,
                "variants": [asdict(v) for v in test.variants],
                "created_at": test.created_at.isoformat() if test.created_at else None,
                "started_at": test.started_at.isoformat() if test.started_at else None,
                "ended_at": test.ended_at.isoformat() if test.ended_at else None,
            }
            data[test_id] = test_dict
        
        with open(self.data_dir / "tests.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def create_test(
        self,
        name: str,
        description: str,
        game_id: str,
        variants: List[Dict[str, Any]]
    ) -> ABTest:
        """새 A/B 테스트 생성"""
        test_id = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        variant_objs = [
            Variant(
                variant_id=f"{test_id}_v{i}",
                name=v.get("name", f"변형 {i+1}"),
                weight=v.get("weight", 1.0 / len(variants)),
                config=v.get("config", {})
            )
            for i, v in enumerate(variants)
        ]
        
        test = ABTest(
            test_id=test_id,
            name=name,
            description=description,
            game_id=game_id,
            variants=variant_objs
        )
        
        self.tests[test_id] = test
        self._save_tests()
        return test
    
    def start_test(self, test_id: str) -> bool:
        """테스트 시작"""
        if test_id not in self.tests:
            return False
        
        test = self.tests[test_id]
        test.status = "running"
        test.started_at = datetime.now()
        self._save_tests()
        return True
    
    def stop_test(self, test_id: str) -> bool:
        """테스트 종료"""
        if test_id not in self.tests:
            return False
        
        test = self.tests[test_id]
        test.status = "completed"
        test.ended_at = datetime.now()
        self._save_tests()
        return True
    
    def assign_variant(self, test_id: str, user_id: str) -> Optional[Variant]:
        """
        유저에게 변형 할당 (결정적 해싱 사용)
        
        Args:
            test_id: 테스트 ID
            user_id: 유저 ID
        
        Returns:
            할당된 변형
        """
        if test_id not in self.tests:
            return None
        
        test = self.tests[test_id]
        if test.status != "running":
            return None
        
        # 유저 ID 기반 결정적 해싱
        hash_input = f"{test_id}:{user_id}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        bucket = (hash_value % 1000) / 1000.0  # 0.0 ~ 1.0
        
        # 가중치 기반 변형 선택
        cumulative = 0.0
        for variant in test.variants:
            cumulative += variant.weight
            if bucket < cumulative:
                variant.impressions += 1
                self._save_tests()
                return variant
        
        # 폴백: 마지막 변형
        test.variants[-1].impressions += 1
        self._save_tests()
        return test.variants[-1]
    
    def track_conversion(self, test_id: str, variant_id: str, revenue: float = 0.0) -> None:
        """전환 추적"""
        if test_id not in self.tests:
            return
        
        test = self.tests[test_id]
        for variant in test.variants:
            if variant.variant_id == variant_id:
                variant.conversions += 1
                variant.revenue += revenue
                self._save_tests()
                break
    
    def get_results(self, test_id: str) -> Optional[Dict[str, Any]]:
        """테스트 결과 조회"""
        if test_id not in self.tests:
            return None
        
        test = self.tests[test_id]
        
        results = {
            "test_id": test.test_id,
            "name": test.name,
            "status": test.status,
            "variants": []
        }
        
        for v in test.variants:
            conv_rate = v.conversions / v.impressions if v.impressions > 0 else 0
            arpu = v.revenue / v.conversions if v.conversions > 0 else 0
            
            results["variants"].append({
                "variant_id": v.variant_id,
                "name": v.name,
                "impressions": v.impressions,
                "conversions": v.conversions,
                "conversion_rate": f"{conv_rate:.2%}",
                "revenue": v.revenue,
                "arpu": arpu
            })
        
        # 승자 결정
        if test.status == "completed" and test.variants:
            winner = max(test.variants, key=lambda x: x.conversions / max(x.impressions, 1))
            results["winner"] = winner.variant_id
        
        return results
    
    def generate_report(self, test_id: str) -> str:
        """테스트 리포트 생성"""
        results = self.get_results(test_id)
        if not results:
            return "테스트를 찾을 수 없습니다."
        
        report = f"""
╔══════════════════════════════════════════════════╗
║              A/B 테스트 결과                       ║
╚══════════════════════════════════════════════════╝

📋 테스트 정보
  - ID: {results['test_id']}
  - 이름: {results['name']}
  - 상태: {results['status']}

📊 변형별 성과
"""
        for v in results["variants"]:
            report += f"""
  [{v['name']}]
    - 노출: {v['impressions']:,}
    - 전환: {v['conversions']:,}
    - 전환율: {v['conversion_rate']}
    - 수익: ${v['revenue']:,.2f}
    - ARPU: ${v['arpu']:.2f}
"""
        
        if results.get("winner"):
            report += f"\n🏆 승자: {results['winner']}"
        
        return report


# 사용 예시
def main():
    manager = ABTestManager("ab_tests")
    
    # 테스트 생성
    test = manager.create_test(
        name="점프 높이 테스트",
        description="점프 높이가 리텐션에 미치는 영향",
        game_id="game_001",
        variants=[
            {"name": "낮은 점프", "weight": 0.5, "config": {"jump_height": 300}},
            {"name": "높은 점프", "weight": 0.5, "config": {"jump_height": 500}}
        ]
    )
    
    print(f"테스트 생성: {test.test_id}")
    
    # 테스트 시작
    manager.start_test(test.test_id)
    
    # 유저 할당 시뮬레이션
    for i in range(100):
        user_id = f"user_{i}"
        variant = manager.assign_variant(test.test_id, user_id)
        
        # 전환 시뮬레이션 (랜덤)
        if random.random() < 0.1:
            manager.track_conversion(test.test_id, variant.variant_id, random.uniform(0.5, 5.0))
    
    # 결과 출력
    print(manager.generate_report(test.test_id))


if __name__ == "__main__":
    main()
