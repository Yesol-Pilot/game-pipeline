"""
코어 모듈 초기화
"""
from .crawler.tiktok_crawler import TikTokCrawler
from .crawler.google_trends_crawler import GoogleTrendsCrawler
from .gdd_generator.gdd_generator import GDDGenerator, GDD
from .builder.godot_builder import GodotBuilder
from .orchestrator.slack_notifier import SlackNotifier
from .asset_pipeline.asset_generator import AssetGenerator, GeneratedAsset
from .analytics.dashboard import AnalyticsDashboard, GameMetrics
from .deployer.store_uploader import GooglePlayUploader, AppStoreUploadManager
from .ab_testing.ab_manager import ABTestManager, ABTest, Variant
from .balancing.balance_manager import BalanceManager, BalanceConfig
from .code_generator.code_generator import CodeGenerator
from .pipeline import Pipeline

__all__ = [
    # 크롤러
    "TikTokCrawler",
    "GoogleTrendsCrawler",
    # GDD
    "GDDGenerator",
    "GDD",
    # 빌더
    "GodotBuilder",
    # 알림
    "SlackNotifier",
    # 자산
    "AssetGenerator",
    "GeneratedAsset",
    # 분석
    "AnalyticsDashboard",
    "GameMetrics",
    # 배포
    "GooglePlayUploader",
    "AppStoreUploadManager",
    # A/B 테스트
    "ABTestManager",
    "ABTest",
    "Variant",
    # 밸런싱
    "BalanceManager",
    "BalanceConfig",
    # 파이프라인
    "Pipeline",
    # 코드 생성
    "CodeGenerator",
]
