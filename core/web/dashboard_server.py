"""
웹 관리자 대시보드
FastAPI 기반 REST API 및 관리 UI
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import json
import sys
from pathlib import Path

# 코어 모듈 경로 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

app = FastAPI(
    title="게임 파이프라인 관리자",
    description="초자동화 게임 개발 파이프라인 관리 API",
    version="1.0.0"
)


# ===== Pydantic 모델 =====

class TrendRequest(BaseModel):
    keywords: List[str]
    template_type: str = "runner"


class GDDResponse(BaseModel):
    game_id: str
    game_title: str
    template_type: str
    created_at: str
    status: str


class BuildRequest(BaseModel):
    game_id: str
    platforms: List[str] = ["android", "html5"]


class ABTestRequest(BaseModel):
    name: str
    description: str
    game_id: str
    variants: List[Dict[str, Any]]


class BalanceUpdateRequest(BaseModel):
    config_id: str
    category: str
    key: str
    value: Any


# ===== 상태 저장 (메모리) =====

games_db: Dict[str, Dict] = {}
builds_db: Dict[str, Dict] = {}


# ===== API 엔드포인트 =====

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """대시보드 메인 페이지"""
    return """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>게임 파이프라인 대시보드</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; background: #0a0a0f; color: #fff; }
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        header { display: flex; justify-content: space-between; align-items: center; padding: 20px 0; border-bottom: 1px solid #333; }
        header h1 { color: #00d9ff; }
        .stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin: 30px 0; }
        .stat-card { background: linear-gradient(135deg, #1a1a2e, #16213e); padding: 25px; border-radius: 15px; }
        .stat-card h2 { font-size: 2.5em; color: #00d9ff; }
        .stat-card p { color: #888; margin-top: 5px; }
        .section { margin: 30px 0; }
        .section h3 { color: #00d9ff; margin-bottom: 15px; }
        .btn { background: #00d9ff; color: #000; border: none; padding: 12px 24px; border-radius: 8px; cursor: pointer; font-weight: bold; }
        .btn:hover { background: #00b8d4; }
        .btn-secondary { background: #333; color: #fff; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 15px; text-align: left; border-bottom: 1px solid #222; }
        th { color: #00d9ff; }
        .status-running { color: #4caf50; }
        .status-pending { color: #ff9800; }
        .status-failed { color: #f44336; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🎮 게임 파이프라인</h1>
            <button class="btn" onclick="createGame()">+ 새 게임 생성</button>
        </header>
        
        <div class="stats">
            <div class="stat-card">
                <h2 id="total-games">0</h2>
                <p>총 게임</p>
            </div>
            <div class="stat-card">
                <h2 id="total-builds">0</h2>
                <p>총 빌드</p>
            </div>
            <div class="stat-card">
                <h2 id="active-tests">0</h2>
                <p>활성 A/B 테스트</p>
            </div>
            <div class="stat-card">
                <h2 id="total-revenue">$0</h2>
                <p>총 수익</p>
            </div>
        </div>
        
        <div class="section">
            <h3>최근 게임</h3>
            <table>
                <thead>
                    <tr>
                        <th>게임명</th>
                        <th>템플릿</th>
                        <th>상태</th>
                        <th>생성일</th>
                        <th>작업</th>
                    </tr>
                </thead>
                <tbody id="games-table">
                    <tr><td colspan="5" style="text-align:center;color:#666">게임이 없습니다</td></tr>
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <h3>빠른 작업</h3>
            <button class="btn" onclick="runPipeline()">🚀 전체 파이프라인 실행</button>
            <button class="btn btn-secondary" onclick="viewAnalytics()">📊 분석 보기</button>
            <button class="btn btn-secondary" onclick="manageABTests()">🔬 A/B 테스트</button>
            <button class="btn btn-secondary" onclick="balanceSettings()">⚖️ 밸런싱</button>
        </div>
    </div>
    
    <script>
        async function loadStats() {
            try {
                const res = await fetch('/api/stats');
                const data = await res.json();
                document.getElementById('total-games').textContent = data.total_games;
                document.getElementById('total-builds').textContent = data.total_builds;
                document.getElementById('active-tests').textContent = data.active_tests;
                document.getElementById('total-revenue').textContent = '$' + data.total_revenue.toLocaleString();
            } catch (e) {
                console.error('통계 로드 실패:', e);
            }
        }
        
        async function loadGames() {
            try {
                const res = await fetch('/api/games');
                const games = await res.json();
                const tbody = document.getElementById('games-table');
                
                if (games.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;color:#666">게임이 없습니다</td></tr>';
                    return;
                }
                
                tbody.innerHTML = games.map(g => `
                    <tr>
                        <td>${g.title}</td>
                        <td>${g.template_type}</td>
                        <td class="status-${g.status}">${g.status}</td>
                        <td>${new Date(g.created_at).toLocaleDateString()}</td>
                        <td>
                            <button class="btn btn-secondary" onclick="buildGame('${g.id}')">빌드</button>
                        </td>
                    </tr>
                `).join('');
            } catch (e) {
                console.error('게임 로드 실패:', e);
            }
        }
        
        function createGame() { alert('게임 생성 다이얼로그 (구현 예정)'); }
        function runPipeline() { alert('파이프라인 실행 (구현 예정)'); }
        function viewAnalytics() { window.location.href = '/analytics'; }
        function manageABTests() { window.location.href = '/ab-tests'; }
        function balanceSettings() { window.location.href = '/balance'; }
        function buildGame(id) { alert('빌드 시작: ' + id); }
        
        loadStats();
        loadGames();
    </script>
</body>
</html>
"""


@app.get("/api/stats")
async def get_stats():
    """통계 조회"""
    return {
        "total_games": len(games_db),
        "total_builds": len(builds_db),
        "active_tests": 0,
        "total_revenue": 0
    }


@app.get("/api/games")
async def list_games():
    """게임 목록 조회"""
    return [
        {
            "id": game_id,
            "title": data.get("title", "Unknown"),
            "template_type": data.get("template_type", ""),
            "status": data.get("status", "pending"),
            "created_at": data.get("created_at", "")
        }
        for game_id, data in games_db.items()
    ]


@app.post("/api/games")
async def create_game(request: TrendRequest, background_tasks: BackgroundTasks):
    """새 게임 생성"""
    game_id = f"game_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    games_db[game_id] = {
        "title": f"트렌드 게임 {len(games_db) + 1}",
        "template_type": request.template_type,
        "keywords": request.keywords,
        "status": "pending",
        "created_at": datetime.now().isoformat()
    }
    
    # 백그라운드에서 GDD 생성
    background_tasks.add_task(generate_gdd_task, game_id, request)
    
    return {"game_id": game_id, "status": "creating"}


async def generate_gdd_task(game_id: str, request: TrendRequest):
    """GDD 생성 백그라운드 태스크"""
    try:
        # 실제 구현에서는 GDDGenerator 호출
        games_db[game_id]["status"] = "gdd_ready"
    except Exception as e:
        games_db[game_id]["status"] = "failed"
        games_db[game_id]["error"] = str(e)


@app.post("/api/builds")
async def start_build(request: BuildRequest, background_tasks: BackgroundTasks):
    """빌드 시작"""
    if request.game_id not in games_db:
        raise HTTPException(status_code=404, detail="게임을 찾을 수 없습니다")
    
    build_id = f"build_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    builds_db[build_id] = {
        "game_id": request.game_id,
        "platforms": request.platforms,
        "status": "building",
        "started_at": datetime.now().isoformat()
    }
    
    return {"build_id": build_id, "status": "building"}


@app.get("/api/builds/{build_id}")
async def get_build_status(build_id: str):
    """빌드 상태 조회"""
    if build_id not in builds_db:
        raise HTTPException(status_code=404, detail="빌드를 찾을 수 없습니다")
    
    return builds_db[build_id]


@app.get("/analytics", response_class=HTMLResponse)
async def analytics_page():
    """분석 페이지"""
    return """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>분석 - 게임 파이프라인</title>
    <style>
        body { font-family: sans-serif; background: #0a0a0f; color: #fff; padding: 20px; }
        h1 { color: #00d9ff; }
        a { color: #00d9ff; }
    </style>
</head>
<body>
    <h1>📊 분석 대시보드</h1>
    <p>게임 성과 분석 (구현 예정)</p>
    <p><a href="/">← 대시보드로 돌아가기</a></p>
</body>
</html>
"""


# ===== 실행 =====

def run_server(host: str = "0.0.0.0", port: int = 8000):
    """서버 실행"""
    import uvicorn
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    print("서버 시작: http://localhost:8000")
    run_server()
