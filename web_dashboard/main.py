from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import subprocess
import os
import json
from typing import List

app = FastAPI(title="Game Factory Control Center")

# 정적 파일 마운트 (CSS, JS)
# 디렉토리가 없으면 생성 (write_to_file이 자동 생성해주지만, 안전장치)
os.makedirs("web_dashboard/static", exist_ok=True)
os.makedirs("web_dashboard/templates", exist_ok=True)

app.mount("/static", StaticFiles(directory="web_dashboard/static"), name="static")

class GenerateRequest(BaseModel):
    game_name: str
    template: str
    concept: str = "auto"

@app.get("/")
async def read_index():
    return FileResponse("web_dashboard/templates/index.html")

@app.get("/api/trends")
async def get_trends():
    # 실제 pytrends 연동 대신 빠른 응답을 위한 Mock 데이터
    # Phase 10 초기 버전은 UI/UX에 집중
    return {
        "status": "success",
        "keywords": [
            {"text": "Cyberpunk", "value": 100},
            {"text": "Cat Cafe", "value": 85},
            {"text": "Space Horror", "value": 75},
            {"text": "Idle Mining", "value": 60},
            {"text": "Vampire Survivor", "value": 55},
        ]
    }

@app.post("/api/generate")
async def generate_game(request: GenerateRequest):
    print(f"🏭 Manufacturing Game: {request.game_name} ({request.template})")
    
    # CLI 명령어 실행 시뮬레이션
    # 실제로는 `python cli.py new` 를 호출
    
    try:
        # 여기서는 Mock 응답을 보내지만, 실제 구현시에는 subprocess로 cli.py 호출
        # cmd = ["python", "cli.py", "new", request.game_name, "--template", request.template]
        # subprocess.Popen(cmd, cwd="../") 
        
        return {
            "status": "success",
            "message": f"Game '{request.game_name}' generation started!",
            "details": {
                "template": request.template,
                "gdd_path": f"games/{request.game_name}/gdd.json"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status")
async def get_system_status():
    return {
        "cpu_load": 12,
        "memory_usage": 45,
        "active_pipelines": 1,
        "last_build": "Success (2 mins ago)"
    }

class VoiceCommandRequest(BaseModel):
    command: str

@app.post("/api/voice_command")
async def process_voice_command(request: VoiceCommandRequest):
    # Lazy import to avoid circular dep or missing module issues in basic env
    try:
        from core.voice.voice_manager import VoiceManager
        vm = VoiceManager()
        
        # 1. Process Intent
        action = vm.process_command(request.command)
        
        # 2. Execute (Mocking file modification for dashboard demo)
        vm.execute_action(action)
        
        return {
            "status": "success",
            "recognized_text": request.command,
            "action_taken": action
        }
    except Exception as e:
        # Fallback if core module not found
        return {
            "status": "error",
            "message": str(e),
            "fallback": "Mock Action: Increased Game Speed"
        }

if __name__ == "__main__":
    import uvicorn
    # 개발 서버 실행: python web_dashboard/main.py
    uvicorn.run(app, host="0.0.0.0", port=8000)
