"""
슬랙 알림 모듈
n8n 워크플로우와 연동하여 GDD 승인 요청 전송
"""

import json
import hmac
import hashlib
import time
from dataclasses import asdict
from typing import Optional, Dict, Any
import urllib.request
import urllib.parse


class SlackNotifier:
    """슬랙 알림 및 승인 요청"""
    
    def __init__(self, config: dict):
        """
        Args:
            config: 슬랙 설정 (웹훅 URL, 채널 등)
        """
        self.config = config
        self.webhook_url = config.get("webhook_url", "")
        self.signing_secret = config.get("signing_secret", "")
        self.channel = config.get("channel", "#game-approvals")
    
    def send_approval_request(self, gdd: Any, callback_url: str) -> bool:
        """
        GDD 승인 요청 전송
        
        Args:
            gdd: 게임 기획 문서 객체
            callback_url: 승인/반려 콜백 URL (n8n 웹훅)
        
        Returns:
            전송 성공 여부
        """
        if not self.webhook_url:
            print("슬랙 웹훅 URL이 설정되지 않았습니다")
            return False
        
        # Block Kit 메시지 생성
        blocks = self._build_blocks(gdd, callback_url)
        payload = {
            "channel": self.channel,
            "blocks": blocks,
            "text": f"새 게임 기획안: {gdd.game_title}"
        }
        
        return self._send_message(payload)
    
    def _build_blocks(self, gdd: Any, callback_url: str) -> list:
        """슬랙 Block Kit 메시지 생성"""
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🎮 새 게임 기획안: {gdd.game_title}",
                    "emoji": True
                }
            },
            {"type": "divider"},
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*템플릿:*\n{gdd.template_type}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*생성 시간:*\n{gdd.created_at[:16]}"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*코어 루프:*\n" + "\n".join([f"• {step}" for step in gdd.core_loop])
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*메카닉:*\n" + ", ".join(gdd.mechanics)
                }
            },
            {"type": "divider"},
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "✅ 승인 및 빌드",
                            "emoji": True
                        },
                        "style": "primary",
                        "action_id": "approve_gdd",
                        "value": json.dumps({"action": "approve", "game_title": gdd.game_title})
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "❌ 반려",
                            "emoji": True
                        },
                        "style": "danger",
                        "action_id": "reject_gdd",
                        "value": json.dumps({"action": "reject", "game_title": gdd.game_title})
                    }
                ]
            }
        ]
        
        return blocks
    
    def _send_message(self, payload: dict) -> bool:
        """슬랙 웹훅으로 메시지 전송"""
        try:
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                self.webhook_url,
                data=data,
                headers={"Content-Type": "application/json"}
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                return response.status == 200
                
        except Exception as e:
            print(f"슬랙 메시지 전송 실패: {e}")
            return False
    
    def verify_signature(self, body: bytes, timestamp: str, signature: str) -> bool:
        """
        슬랙 요청 서명 검증 (HMAC SHA-256)
        
        Args:
            body: 요청 본문
            timestamp: X-Slack-Request-Timestamp 헤더
            signature: X-Slack-Signature 헤더
        
        Returns:
            서명 유효 여부
        """
        if not self.signing_secret:
            return False
        
        # 타임스탬프 검증 (5분 이내)
        if abs(time.time() - float(timestamp)) > 60 * 5:
            return False
        
        # 서명 계산
        sig_basestring = f"v0:{timestamp}:{body.decode('utf-8')}"
        computed_signature = "v0=" + hmac.new(
            self.signing_secret.encode("utf-8"),
            sig_basestring.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(computed_signature, signature)
    
    def send_build_result(self, game_title: str, success: bool, details: str) -> bool:
        """빌드 결과 알림 전송"""
        if not self.webhook_url:
            return False
        
        emoji = "✅" if success else "❌"
        status = "성공" if success else "실패"
        
        payload = {
            "channel": self.channel,
            "text": f"{emoji} *{game_title}* 빌드 {status}\n{details}"
        }
        
        return self._send_message(payload)


# 사용 예시
def main():
    config = {
        "webhook_url": "",  # 슬랙 웹훅 URL 입력
        "signing_secret": "",  # 슬랙 앱 Signing Secret
        "channel": "#game-approvals"
    }
    
    notifier = SlackNotifier(config)
    
    # 테스트 GDD (모의 객체)
    class MockGDD:
        game_title = "테스트 러너"
        template_type = "runner"
        core_loop = ["달리기", "점프", "회피", "점수 획득"]
        mechanics = ["터치 점프", "더블 점프"]
        created_at = "2026-01-10T20:00:00"
    
    gdd = MockGDD()
    
    if config["webhook_url"]:
        success = notifier.send_approval_request(gdd, "https://example.com/callback")
        print(f"승인 요청 전송: {'성공' if success else '실패'}")
    else:
        print("웹훅 URL이 설정되지 않아 테스트를 건너뜁니다")


if __name__ == "__main__":
    main()
