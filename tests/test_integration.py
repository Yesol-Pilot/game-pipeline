"""
통합 테스트 - 전체 파이프라인 흐름
"""

import pytest
import json
from pathlib import Path
from datetime import datetime
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestPipelineIntegration:
    """파이프라인 통합 테스트"""
    
    @pytest.fixture
    def pipeline_config(self, tmp_path):
        """테스트용 파이프라인 설정"""
        config = {
            "gemini_api_key": "",
            "stability_api_key": "",
            "output_dir": str(tmp_path / "output"),
            "templates_dir": str(Path(__file__).parent.parent / "templates")
        }
        
        config_path = tmp_path / "config.json"
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f)
        
        return config_path
    
    def test_gdd_to_build_flow(self, tmp_path):
        """GDD 생성 → 빌드 흐름 테스트"""
        from core.gdd_generator.gdd_generator import GDDGenerator, GDD
        
        # GDD 생성
        generator = GDDGenerator({"provider": "test"})
        
        gdd = generator.generate_from_trends(
            [{"hashtag": "#테스트", "view_count": 1000}],
            [{"keyword": "테스트", "interest": 80}],
            "runner"
        )
        
        assert gdd is not None
        assert gdd.template_type == "runner"
        
        # GDD 저장
        gdd_path = tmp_path / "test_gdd.json"
        generator.save_gdd(gdd, str(gdd_path))
        
        assert gdd_path.exists()
    
    def test_asset_generation_flow(self, tmp_path):
        """자산 생성 흐름 테스트"""
        from core.asset_pipeline.asset_generator import AssetGenerator
        
        generator = AssetGenerator({"api_key": ""})
        
        output_path = str(tmp_path / "test_sprite.png")
        result = generator.generate_sprite(
            prompt="test character",
            output_path=output_path
        )
        
        assert result is not None
        assert Path(output_path).exists()
    
    def test_analytics_flow(self, tmp_path):
        """분석 흐름 테스트"""
        from core.analytics.dashboard import AnalyticsDashboard
        
        dashboard = AnalyticsDashboard(str(tmp_path / "analytics"))
        
        # 게임 추적
        dashboard.track_game_created("game_001", "테스트 게임", "runner")
        dashboard.track_build("game_001", True)
        dashboard.track_asset_generation("game_001", True)
        
        # 결과 확인
        report = dashboard.generate_summary_report()
        assert "총 게임 수: 1" in report
    
    def test_ab_testing_flow(self, tmp_path):
        """A/B 테스트 흐름 테스트"""
        from core.ab_testing.ab_manager import ABTestManager
        
        manager = ABTestManager(str(tmp_path / "ab_tests"))
        
        # 테스트 생성
        test = manager.create_test(
            name="점프 높이",
            description="테스트",
            game_id="game_001",
            variants=[
                {"name": "A", "weight": 0.5},
                {"name": "B", "weight": 0.5}
            ]
        )
        
        assert test is not None
        manager.start_test(test.test_id)
        
        # 유저 할당
        variant = manager.assign_variant(test.test_id, "user_001")
        assert variant is not None
    
    def test_balance_config_flow(self, tmp_path):
        """밸런싱 흐름 테스트"""
        from core.balancing.balance_manager import BalanceManager
        
        manager = BalanceManager(str(tmp_path / "balance"))
        
        # 설정 생성
        config = manager.create_config("game_001", "runner")
        assert config.gameplay.get("player_speed") == 400.0
        
        # 파라미터 수정
        manager.update_parameter(config.config_id, "gameplay", "jump_height", 500.0)
        
        # 퍼블리시
        manager.publish_config(config.config_id)
        
        published = manager.get_published_config("game_001")
        assert published is not None


class TestModuleImports:
    """모듈 임포트 테스트"""
    
    def test_core_imports(self):
        """코어 모듈 임포트"""
        from core import (
            TikTokCrawler,
            GoogleTrendsCrawler,
            GDDGenerator,
            GodotBuilder,
            SlackNotifier,
            AssetGenerator,
        )
        
        assert TikTokCrawler is not None
        assert GoogleTrendsCrawler is not None
        assert GDDGenerator is not None
    
    def test_analytics_imports(self):
        """분석 모듈 임포트"""
        from core.analytics import AnalyticsDashboard, GameMetrics
        
        assert AnalyticsDashboard is not None
    
    def test_plugin_imports(self):
        """플러그인 모듈 임포트"""
        from core.plugins import PluginManager, PluginBase, PluginHooks
        
        assert PluginManager is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
