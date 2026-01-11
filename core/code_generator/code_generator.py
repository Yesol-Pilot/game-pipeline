import os
import re

class CodeGenerator:
    """Godot GDScript Code Generator using LLM"""
    
    def __init__(self, config: dict = {}):
        self.config = config
        
    def generate_script(self, requirement: str, base_class: str = "Node") -> str:
        """
        요구사항에 맞는 GDScript 코드 생성
        """
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return self._mock_generation(requirement, base_class)
            
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            
            model = genai.GenerativeModel('gemini-1.5-pro')
            
            prompt = f"""
            You are an expert Godot 4.2 GDScript programmer.
            Write a GDScript file that extends {base_class}.
            
            Requirement: {requirement}
            
            Rules:
            1. Use static typing (e.g. `var x: int = 10`)
            2. Follow Godot 4.2 syntax (e.g. `@export`, `super()`)
            3. Do not use Markdown code blocks. Just plain text code.
            4. Add comments in Korean.
            """
            
            response = model.generate_content(prompt)
            code = response.text
            
            # Clean up Markdown if present
            if "```gdscript" in code:
                code = code.split("```gdscript")[1].split("```")[0]
            elif "```" in code:
                code = code.split("```")[1].split("```")[0]
                
            return code.strip()
            
        except Exception as e:
            print(f"[CodeGenerator] Error: {e}")
            return self._mock_generation(requirement, base_class)

    def _mock_generation(self, requirement: str, base_class: str) -> str:
        """API 키 없을 때의 예시 코드 반환"""
        return f"""extends {base_class}

# [Mock] AI Generated Script
# Requirement: {requirement}

func _ready() -> void:
    print("AI Script Initialized")
    
func _process(delta: float) -> void:
    pass
"""
