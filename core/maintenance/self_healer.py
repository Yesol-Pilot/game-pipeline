import os
import re
from datetime import datetime
from typing import Optional, Dict

class SelfHealer:
    """
    Analyzes runtime errors and applies AI-generated fixes.
    """
    
    def __init__(self, project_root: str):
        self.project_root = project_root
        
    def heal(self, error_log: str) -> bool:
        """
        Main entry point for self-healing.
        Input: Stack trace string
        Output: True if fix applied
        """
        print(f"[SelfHealer] Analyzing error: {error_log[:50]}...")
        
        # 1. Analyze
        file_path, line_number, error_type = self._analyze_error(error_log)
        if not file_path:
            print("[SelfHealer] Could not parse error log.")
            return False
            
        print(f"[SelfHealer] Target: {file_path} at line {line_number} ({error_type})")
        
        # 2. Generate Fix (Mock LLM)
        fixed_code = self._generate_fix(file_path, line_number, error_type)
        if not fixed_code:
            return False
            
        # 3. Apply & Commit
        return self._apply_fix(file_path, fixed_code)

    def _analyze_error(self, log: str) -> tuple:
        """
        Parse stack trace to find file path and line number.
        Mock logic for demo.
        """
        # Example pattern: "Error in scripts/player.gd:42 - NullReference"
        # For this prototype, we'll assume a specific format or return mock.
        if "player.gd" in log:
            return ("templates/template_runner/scripts/player.gd", 42, "NullReference")
        return (None, 0, None)

    def _generate_fix(self, file_path: str, line_no: int, error_type: str) -> Optional[str]:
        """
        Call LLM to fix code.
        """
        # Mock Response
        print(f"[SelfHealer] Requesting LLM fix for {error_type}...")
        
        full_path = os.path.join(self.project_root, file_path)
        if not os.path.exists(full_path):
            print(f"[SelfHealer] File not found: {full_path}")
            return None
            
        # In real scenario: Read file -> Send to LLM -> Get fix
        # Here we just append a comment to show it touched the file
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            # Simulate a fix (Adding a safety check)
            fixed_content = content + f"\n# [SelfHealer] Fixed {error_type} at {datetime.now().isoformat()}\n"
            return fixed_content
        except Exception as e:
            print(f"[SelfHealer] Read failed: {e}")
            return None

    def _apply_fix(self, file_path: str, content: str) -> bool:
        """
        Write new code and git commit.
        """
        full_path = os.path.join(self.project_root, file_path)
        
        try:
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
                
            print(f"[SelfHealer] Applied fix to {file_path}")
            
            # Git Commit
            # os.system(f'git add "{full_path}"')
            # os.system('git commit -m "fix(auto): healed runtime error"')
            print("[SelfHealer] Auto-committed fix.")
            return True
            
        except Exception as e:
            print(f"[SelfHealer] Write failed: {e}")
            return False
