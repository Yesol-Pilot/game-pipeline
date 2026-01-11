"""
실시간 밸런싱 도구
게임 파라미터 원격 조정
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field


@dataclass
class BalanceConfig:
    """밸런스 설정"""
    config_id: str
    game_id: str
    version: int
    
    # 게임 플레이 파라미터
    gameplay: Dict[str, Any] = field(default_factory=dict)
    
    # 경제 파라미터
    economy: Dict[str, Any] = field(default_factory=dict)
    
    # 난이도 파라미터
    difficulty: Dict[str, Any] = field(default_factory=dict)
    
    # 광고 파라미터
    ads: Dict[str, Any] = field(default_factory=dict)
    
    created_at: datetime = None
    published: bool = False
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


class BalanceManager:
    """실시간 밸런싱 매니저"""
    
    # 기본 밸런스 템플릿
    DEFAULT_TEMPLATES = {
        "runner": {
            "gameplay": {
                "player_speed": 400.0,
                "jump_height": 400.0,
                "gravity": 980.0,
                "obstacle_gap_min": 300,
                "obstacle_gap_max": 600
            },
            "economy": {
                "coin_value": 1,
                "coin_spawn_rate": 0.3,
                "revive_cost": 50
            },
            "difficulty": {
                "initial_speed": 1.0,
                "speed_increase_rate": 0.01,
                "max_speed_multiplier": 2.0
            },
            "ads": {
                "interstitial_frequency": 3,
                "rewarded_multiplier": 2
            }
        },
        "clicker": {
            "gameplay": {
                "base_click_value": 1,
                "click_animation_duration": 0.1
            },
            "economy": {
                "upgrade_cost_multiplier": 1.5,
                "prestige_bonus": 0.1,
                "offline_efficiency": 0.5
            },
            "difficulty": {
                "target_time_to_prestige": 3600
            },
            "ads": {
                "rewarded_multiplier": 2,
                "rewarded_duration": 300
            }
        },
        "match3": {
            "gameplay": {
                "grid_size": 8,
                "min_match": 3,
                "fall_speed": 500.0,
                "swap_duration": 0.2
            },
            "economy": {
                "score_per_gem": 10,
                "combo_multiplier": 1.5,
                "move_cost": 50
            },
            "difficulty": {
                "initial_moves": 30,
                "target_score_multiplier": 1.2
            },
            "ads": {
                "extra_moves_reward": 5
            }
        }
    }
    
    def __init__(self, data_dir: str = "balance"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.configs: Dict[str, BalanceConfig] = {}
        self._load_configs()
    
    def _load_configs(self) -> None:
        """저장된 설정 로드"""
        for file in self.data_dir.glob("*.json"):
            if file.name.startswith("config_"):
                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if data.get("created_at"):
                        data["created_at"] = datetime.fromisoformat(data["created_at"])
                    config = BalanceConfig(**data)
                    self.configs[config.config_id] = config
    
    def _save_config(self, config: BalanceConfig) -> None:
        """설정 저장"""
        data = {
            "config_id": config.config_id,
            "game_id": config.game_id,
            "version": config.version,
            "gameplay": config.gameplay,
            "economy": config.economy,
            "difficulty": config.difficulty,
            "ads": config.ads,
            "created_at": config.created_at.isoformat(),
            "published": config.published
        }
        
        filepath = self.data_dir / f"config_{config.config_id}.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def create_config(self, game_id: str, template_type: str = None) -> BalanceConfig:
        """새 밸런스 설정 생성"""
        config_id = f"{game_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 템플릿 적용
        template = self.DEFAULT_TEMPLATES.get(template_type, {})
        
        config = BalanceConfig(
            config_id=config_id,
            game_id=game_id,
            version=1,
            gameplay=template.get("gameplay", {}),
            economy=template.get("economy", {}),
            difficulty=template.get("difficulty", {}),
            ads=template.get("ads", {})
        )
        
        self.configs[config_id] = config
        self._save_config(config)
        return config
    
    def update_parameter(
        self,
        config_id: str,
        category: str,
        key: str,
        value: Any
    ) -> bool:
        """파라미터 업데이트"""
        if config_id not in self.configs:
            return False
        
        config = self.configs[config_id]
        
        category_map = {
            "gameplay": config.gameplay,
            "economy": config.economy,
            "difficulty": config.difficulty,
            "ads": config.ads
        }
        
        if category not in category_map:
            return False
        
        category_map[category][key] = value
        config.version += 1
        self._save_config(config)
        return True
    
    def publish_config(self, config_id: str) -> bool:
        """설정 퍼블리시 (클라이언트에 적용)"""
        if config_id not in self.configs:
            return False
        
        config = self.configs[config_id]
        config.published = True
        self._save_config(config)
        
        # 퍼블리시된 설정을 별도 파일로 저장 (클라이언트 다운로드용)
        published_path = self.data_dir / f"published_{config.game_id}.json"
        with open(published_path, "w", encoding="utf-8") as f:
            json.dump({
                "version": config.version,
                "gameplay": config.gameplay,
                "economy": config.economy,
                "difficulty": config.difficulty,
                "ads": config.ads,
                "published_at": datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
        
        return True
    
    def get_published_config(self, game_id: str) -> Optional[Dict[str, Any]]:
        """퍼블리시된 설정 조회 (클라이언트용)"""
        published_path = self.data_dir / f"published_{game_id}.json"
        
        if not published_path.exists():
            return None
        
        with open(published_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def compare_configs(self, config_id1: str, config_id2: str) -> Dict[str, Any]:
        """두 설정 비교"""
        if config_id1 not in self.configs or config_id2 not in self.configs:
            return {"error": "설정을 찾을 수 없습니다"}
        
        config1 = self.configs[config_id1]
        config2 = self.configs[config_id2]
        
        differences = {
            "gameplay": {},
            "economy": {},
            "difficulty": {},
            "ads": {}
        }
        
        for category in ["gameplay", "economy", "difficulty", "ads"]:
            dict1 = getattr(config1, category)
            dict2 = getattr(config2, category)
            
            all_keys = set(dict1.keys()) | set(dict2.keys())
            for key in all_keys:
                val1 = dict1.get(key)
                val2 = dict2.get(key)
                if val1 != val2:
                    differences[category][key] = {
                        "before": val1,
                        "after": val2
                    }
        
        return differences
    
    def generate_gdscript(self, config_id: str) -> str:
        """GDScript 설정 파일 생성"""
        if config_id not in self.configs:
            return ""
        
        config = self.configs[config_id]
        
        script = f"""extends Resource
## 자동 생성된 밸런스 설정
## 버전: {config.version}
## 생성일: {config.created_at.strftime('%Y-%m-%d %H:%M:%S')}

class_name BalanceConfig

"""
        # Gameplay
        script += "# 게임플레이\n"
        for key, value in config.gameplay.items():
            script += f"@export var {key} = {self._format_gdscript_value(value)}\n"
        
        script += "\n# 경제\n"
        for key, value in config.economy.items():
            script += f"@export var {key} = {self._format_gdscript_value(value)}\n"
        
        script += "\n# 난이도\n"
        for key, value in config.difficulty.items():
            script += f"@export var {key} = {self._format_gdscript_value(value)}\n"
        
        script += "\n# 광고\n"
        for key, value in config.ads.items():
            script += f"@export var {key} = {self._format_gdscript_value(value)}\n"
        
        return script
    
    def _format_gdscript_value(self, value: Any) -> str:
        """GDScript 값 포맷팅"""
        if isinstance(value, bool):
            return "true" if value else "false"
        elif isinstance(value, float):
            return str(value)
        elif isinstance(value, int):
            return str(value)
        elif isinstance(value, str):
            return f'"{value}"'
        else:
            return str(value)


# 사용 예시
def main():
    manager = BalanceManager("balance")
    
    # 러너 게임 설정 생성
    config = manager.create_config("game_runner_001", "runner")
    print(f"설정 생성: {config.config_id}")
    
    # 파라미터 조정
    manager.update_parameter(config.config_id, "gameplay", "jump_height", 500.0)
    manager.update_parameter(config.config_id, "economy", "coin_value", 2)
    
    # 퍼블리시
    manager.publish_config(config.config_id)
    
    # GDScript 생성
    gdscript = manager.generate_gdscript(config.config_id)
    print("\n생성된 GDScript:")
    print(gdscript)


if __name__ == "__main__":
    main()
