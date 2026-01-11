"""
플러그인 시스템
파이프라인 확장을 위한 플러그인 아키텍처
"""

import importlib
import importlib.util
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Any, Optional, Type
from dataclasses import dataclass
from datetime import datetime


@dataclass
class PluginInfo:
    """플러그인 정보"""
    name: str
    version: str
    description: str
    author: str
    hooks: List[str]
    enabled: bool = True


class PluginBase(ABC):
    """플러그인 베이스 클래스"""
    
    # 플러그인 메타데이터 (서브클래스에서 오버라이드)
    NAME = "BasePlugin"
    VERSION = "1.0.0"
    DESCRIPTION = "Base plugin"
    AUTHOR = "Unknown"
    HOOKS = []  # 지원하는 훅 목록
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.enabled = True
    
    def get_info(self) -> PluginInfo:
        """플러그인 정보 반환"""
        return PluginInfo(
            name=self.NAME,
            version=self.VERSION,
            description=self.DESCRIPTION,
            author=self.AUTHOR,
            hooks=self.HOOKS,
            enabled=self.enabled
        )
    
    @abstractmethod
    def on_load(self) -> None:
        """플러그인 로드 시 호출"""
        pass
    
    @abstractmethod
    def on_unload(self) -> None:
        """플러그인 언로드 시 호출"""
        pass


class PluginHooks:
    """플러그인 훅 정의"""
    
    # GDD 관련
    PRE_GDD_GENERATE = "pre_gdd_generate"
    POST_GDD_GENERATE = "post_gdd_generate"
    
    # 자산 관련
    PRE_ASSET_GENERATE = "pre_asset_generate"
    POST_ASSET_GENERATE = "post_asset_generate"
    
    # 빌드 관련
    PRE_BUILD = "pre_build"
    POST_BUILD = "post_build"
    
    # 배포 관련
    PRE_DEPLOY = "pre_deploy"
    POST_DEPLOY = "post_deploy"
    
    # 분석 관련
    ON_GAME_CREATED = "on_game_created"
    ON_BUILD_COMPLETED = "on_build_completed"


class PluginManager:
    """플러그인 매니저"""
    
    def __init__(self, plugins_dir: str = "plugins"):
        self.plugins_dir = Path(plugins_dir)
        self.plugins_dir.mkdir(parents=True, exist_ok=True)
        
        self.plugins: Dict[str, PluginBase] = {}
        self.hooks: Dict[str, List[PluginBase]] = {}
    
    def discover_plugins(self) -> List[str]:
        """플러그인 검색"""
        discovered = []
        
        for file in self.plugins_dir.glob("*.py"):
            if file.name.startswith("_"):
                continue
            discovered.append(file.stem)
        
        return discovered
    
    def load_plugin(self, plugin_name: str, config: dict = None) -> bool:
        """플러그인 로드"""
        plugin_path = self.plugins_dir / f"{plugin_name}.py"
        
        if not plugin_path.exists():
            print(f"플러그인 파일 없음: {plugin_path}")
            return False
        
        try:
            # 모듈 동적 로드
            spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Plugin 클래스 찾기
            plugin_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    issubclass(attr, PluginBase) and 
                    attr is not PluginBase):
                    plugin_class = attr
                    break
            
            if plugin_class is None:
                print(f"플러그인 클래스 없음: {plugin_name}")
                return False
            
            # 인스턴스 생성
            plugin = plugin_class(config)
            plugin.on_load()
            
            self.plugins[plugin_name] = plugin
            
            # 훅 등록
            for hook in plugin.HOOKS:
                if hook not in self.hooks:
                    self.hooks[hook] = []
                self.hooks[hook].append(plugin)
            
            print(f"플러그인 로드: {plugin.NAME} v{plugin.VERSION}")
            return True
            
        except Exception as e:
            print(f"플러그인 로드 오류: {e}")
            return False
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """플러그인 언로드"""
        if plugin_name not in self.plugins:
            return False
        
        plugin = self.plugins[plugin_name]
        
        # 훅에서 제거
        for hook, plugins in self.hooks.items():
            if plugin in plugins:
                plugins.remove(plugin)
        
        plugin.on_unload()
        del self.plugins[plugin_name]
        
        print(f"플러그인 언로드: {plugin_name}")
        return True
    
    def execute_hook(self, hook_name: str, data: Any = None) -> Any:
        """훅 실행"""
        if hook_name not in self.hooks:
            return data
        
        result = data
        for plugin in self.hooks[hook_name]:
            if not plugin.enabled:
                continue
            
            try:
                handler = getattr(plugin, f"on_{hook_name}", None)
                if handler:
                    result = handler(result)
            except Exception as e:
                print(f"훅 실행 오류 ({plugin.NAME}): {e}")
        
        return result
    
    def list_plugins(self) -> List[PluginInfo]:
        """로드된 플러그인 목록"""
        return [p.get_info() for p in self.plugins.values()]
    
    def get_plugin(self, name: str) -> Optional[PluginBase]:
        """플러그인 조회"""
        return self.plugins.get(name)


# 예시 플러그인
class ExamplePlugin(PluginBase):
    """예시 플러그인"""
    
    NAME = "ExamplePlugin"
    VERSION = "1.0.0"
    DESCRIPTION = "예시 플러그인"
    AUTHOR = "Developer"
    HOOKS = [PluginHooks.POST_GDD_GENERATE, PluginHooks.ON_GAME_CREATED]
    
    def on_load(self) -> None:
        print(f"[{self.NAME}] 로드됨")
    
    def on_unload(self) -> None:
        print(f"[{self.NAME}] 언로드됨")
    
    def on_post_gdd_generate(self, gdd: Any) -> Any:
        """GDD 생성 후 처리"""
        print(f"[{self.NAME}] GDD 후처리: {getattr(gdd, 'game_title', 'Unknown')}")
        return gdd
    
    def on_on_game_created(self, game_id: str) -> str:
        """게임 생성 시"""
        print(f"[{self.NAME}] 게임 생성됨: {game_id}")
        return game_id


# 사용 예시
def main():
    manager = PluginManager("plugins")
    
    # 플러그인 검색
    discovered = manager.discover_plugins()
    print(f"발견된 플러그인: {discovered}")
    
    # 내장 플러그인 테스트
    # (실제로는 파일에서 로드)
    example = ExamplePlugin()
    manager.plugins["example"] = example
    manager.hooks[PluginHooks.POST_GDD_GENERATE] = [example]
    
    # 훅 실행
    class MockGDD:
        game_title = "테스트 게임"
    
    result = manager.execute_hook(PluginHooks.POST_GDD_GENERATE, MockGDD())
    
    # 플러그인 목록
    for info in manager.list_plugins():
        print(f"- {info.name} v{info.version}: {info.description}")


if __name__ == "__main__":
    main()
