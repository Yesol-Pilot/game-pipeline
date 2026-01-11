import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

class AutoPatcher:
    """
    Automatically modifies game configuration based on market sentiment.
    """
    
    def __init__(self, games_dir: str = "games"):
        self.games_dir = Path(games_dir)
        
    def create_patch(self, gdd_path: str, sentiments: Dict[str, float]) -> Dict[str, Any]:
        """
        Apply patch to GDD based on sentiments.
        """
        patch_note = []
        changes = {}
        
        try:
            with open(gdd_path, "r", encoding="utf-8") as f:
                gdd = json.load(f)
        except Exception as e:
            print(f"[AutoPatcher] Failed to load GDD: {e}")
            return {"success": False, "error": str(e)}
            
        # Logic: Difficulty Adjustment
        difficulty = gdd.get("difficulty", {})
        if not difficulty: difficulty = {"level": 1.0}
        
        current_level = difficulty.get("level", 1.0)
        
        if sentiments.get("difficulty", 0) > 0.5:
            # Too Hard -> Reduce Difficulty
            new_level = max(0.5, current_level * 0.8)
            patch_note.append(f"난이도 하향 조정 ({current_level:.1f} -> {new_level:.1f})")
            difficulty["level"] = new_level
            changes["difficulty"] = new_level
            
        elif sentiments.get("boredom", 0) > 0.5:
            # Boring -> Increase Game Speed or Spawn Rate
            game_speed = gdd.get("game_config", {}).get("game_speed", 1.0)
            new_speed = game_speed * 1.2
            patch_note.append(f"게임 속도 상향 ({game_speed:.1f} -> {new_speed:.1f})")
            
            if "game_config" not in gdd: gdd["game_config"] = {}
            gdd["game_config"]["game_speed"] = new_speed
            changes["game_speed"] = new_speed

        # Apply Changes
        gdd["difficulty"] = difficulty
        gdd["last_patched"] = datetime.now().isoformat()
        gdd["patch_notes"] = gdd.get("patch_notes", []) + patch_note
        
        # Save
        with open(gdd_path, "w", encoding="utf-8") as f:
            json.dump(gdd, f, indent=2, ensure_ascii=False)
            
        print(f"[AutoPatcher] Patch Applied: {patch_note}")
        
        return {
            "success": True,
            "patch_note": "\n".join(patch_note),
            "changes": changes
        }
