import os
import json
import re

class VoiceManager:
    """
    Voice Command Manager
    Handles Speech-to-Text (Whisper) and Intent Parsing
    """
    
    def __init__(self, config: dict = {}):
        self.config = config
        
    def transcribe(self, audio_file_path: str) -> str:
        """
        Transcribe audio file to text using OpenAI Whisper API
        """
        api_key = os.environ.get("OPENAI_API_KEY")
        
        if not api_key:
            print("[VoiceManager] No API Key found. Returning Mock transcription.")
            return "플레이어 속도를 좀 더 빠르게 해줘"
            
        try:
            import openai
            client = openai.OpenAI(api_key=api_key)
            
            with open(audio_file_path, "rb") as audio_file:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1", 
                    file=audio_file
                )
            return transcript.text
            
        except Exception as e:
            print(f"[VoiceManager] Transcribe Error: {e}")
            return "Error processing audio"

    def process_command(self, text: str) -> dict:
        """
        Parse text command into meaningful game modification actions
        Simple Rule-based intent parsing (could be replaced by LLM)
        """
        text = text.lower()
        action = {}
        
        # 1. 속도/점프력 관련
        if "빠르게" in text or "fast" in text or "speed" in text:
            action = {"target": "game_config", "key": "game_speed", "operation": "multiply", "value": 1.2}
        elif "느리게" in text or "slow" in text:
            action = {"target": "game_config", "key": "game_speed", "operation": "multiply", "value": 0.8}
        elif "높게" in text or "high" in text or "jump" in text:
            action = {"target": "player_stats", "key": "jump_force", "operation": "multiply", "value": 1.2}
        
        # 2. 난이도 관련
        elif "어렵게" in text or "hard" in text:
            action = {"target": "game_config", "key": "difficulty", "operation": "add", "value": 1}
        elif "쉽게" in text or "easy" in text:
            action = {"target": "game_config", "key": "difficulty", "operation": "subtract", "value": 1}
            
        # 3. 비주얼 실패 예시
        else:
            action = {"target": "unknown", "raw_text": text}
            
        return action
        
    def execute_action(self, action: dict, gdd_path: str = "gdd.json") -> bool:
        """
        Apply the action to GDD or Config file
        """
        # 실제 구현에서는 json 파일을 로드해서 수정하고 저장
        print(f"[VoiceManager] Executing Action: {action}")
        return True
