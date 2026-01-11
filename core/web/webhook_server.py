"""
웹훅 서버
GitHub/GitLab 웹훅 연동
"""

from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import hmac
import hashlib
import json
from datetime import datetime
from typing import Dict, Any, Optional


app = FastAPI(title="게임 파이프라인 웹훅")


class WebhookHandler:
    """웹훅 핸들러"""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.github_secret = self.config.get("github_secret", "")
        self.gitlab_token = self.config.get("gitlab_token", "")
    
    def verify_github_signature(self, payload: bytes, signature: str) -> bool:
        """GitHub 서명 검증"""
        if not self.github_secret:
            return True  # 시크릿 없으면 스킵
        
        expected = "sha256=" + hmac.new(
            self.github_secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected, signature)
    
    def verify_gitlab_token(self, token: str) -> bool:
        """GitLab 토큰 검증"""
        if not self.gitlab_token:
            return True
        return token == self.gitlab_token
    
    async def handle_push(self, data: dict) -> dict:
        """푸시 이벤트 처리"""
        branch = data.get("ref", "").replace("refs/heads/", "")
        commits = data.get("commits", [])
        
        print(f"📥 Push: {branch} ({len(commits)} commits)")
        
        # main/master 브랜치면 자동 빌드
        if branch in ["main", "master"]:
            return await self._trigger_build(data)
        
        return {"status": "ignored", "branch": branch}
    
    async def handle_release(self, data: dict) -> dict:
        """릴리스 이벤트 처리"""
        action = data.get("action", "")
        release = data.get("release", {})
        tag = release.get("tag_name", "")
        
        print(f"🏷️ Release: {tag} ({action})")
        
        if action == "published":
            return await self._trigger_deploy(data)
        
        return {"status": "ignored", "action": action}
    
    async def handle_issue(self, data: dict) -> dict:
        """이슈 이벤트 처리"""
        action = data.get("action", "")
        issue = data.get("issue", {})
        title = issue.get("title", "")
        
        print(f"📋 Issue: {title} ({action})")
        
        return {"status": "logged", "action": action}
    
    async def _trigger_build(self, data: dict) -> dict:
        """빌드 트리거"""
        from core.builder.godot_builder import GodotBuilder
        
        print("🔨 자동 빌드 시작...")
        
        # 실제 빌드 로직
        # builder = GodotBuilder({})
        # builder.build(...)
        
        return {"status": "build_triggered"}
    
    async def _trigger_deploy(self, data: dict) -> dict:
        """배포 트리거"""
        print("🚀 자동 배포 시작...")
        
        return {"status": "deploy_triggered"}


# 전역 핸들러
handler = WebhookHandler()


@app.post("/webhook/github")
async def github_webhook(request: Request, background_tasks: BackgroundTasks):
    """GitHub 웹훅 엔드포인트"""
    
    # 서명 검증
    signature = request.headers.get("X-Hub-Signature-256", "")
    payload = await request.body()
    
    if not handler.verify_github_signature(payload, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # 이벤트 처리
    event = request.headers.get("X-GitHub-Event", "")
    data = json.loads(payload)
    
    result = {"event": event, "received_at": datetime.now().isoformat()}
    
    if event == "push":
        result.update(await handler.handle_push(data))
    elif event == "release":
        result.update(await handler.handle_release(data))
    elif event == "issues":
        result.update(await handler.handle_issue(data))
    else:
        result["status"] = "unhandled"
    
    return JSONResponse(result)


@app.post("/webhook/gitlab")
async def gitlab_webhook(request: Request, background_tasks: BackgroundTasks):
    """GitLab 웹훅 엔드포인트"""
    
    # 토큰 검증
    token = request.headers.get("X-Gitlab-Token", "")
    
    if not handler.verify_gitlab_token(token):
        raise HTTPException(status_code=401, detail="Invalid token")
    
    data = await request.json()
    event = data.get("object_kind", "")
    
    result = {"event": event, "received_at": datetime.now().isoformat()}
    
    if event == "push":
        result.update(await handler.handle_push(data))
    elif event == "tag_push":
        result.update(await handler.handle_release(data))
    else:
        result["status"] = "unhandled"
    
    return JSONResponse(result)


@app.get("/webhook/health")
async def health():
    """헬스 체크"""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


def run_webhook_server(host: str = "0.0.0.0", port: int = 9000):
    """웹훅 서버 실행"""
    import uvicorn
    print(f"🔗 웹훅 서버: http://{host}:{port}")
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_webhook_server()
