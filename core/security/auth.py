"""
API 인증 모듈
JWT 기반 인증
"""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import hashlib
import secrets


# 설정
SECRET_KEY = secrets.token_hex(32)  # 프로덕션에서는 환경 변수 사용
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

security = HTTPBearer()


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """액세스 토큰 생성"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> dict:
    """토큰 검증"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰이 만료되었습니다"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다"
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """현재 사용자 조회"""
    token = credentials.credentials
    payload = verify_token(token)
    return payload


def hash_password(password: str) -> str:
    """비밀번호 해싱"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """비밀번호 검증"""
    return hash_password(plain_password) == hashed_password


# API 키 인증 (간단한 방식)
class APIKeyAuth:
    """API 키 인증"""
    
    def __init__(self, valid_keys: list = None):
        self.valid_keys = valid_keys or []
    
    def add_key(self, key: str):
        """키 추가"""
        self.valid_keys.append(key)
    
    def verify(self, key: str) -> bool:
        """키 검증"""
        return key in self.valid_keys
    
    async def __call__(
        self,
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> bool:
        """FastAPI 의존성으로 사용"""
        if not self.verify(credentials.credentials):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 API 키입니다"
            )
        return True


# Rate Limiting
from collections import defaultdict
import time


class RateLimiter:
    """Rate Limiter"""
    
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)
    
    def is_allowed(self, client_id: str) -> bool:
        """요청 허용 여부 확인"""
        now = time.time()
        minute_ago = now - 60
        
        # 오래된 요청 제거
        self.requests[client_id] = [
            t for t in self.requests[client_id]
            if t > minute_ago
        ]
        
        # 허용 여부 확인
        if len(self.requests[client_id]) >= self.requests_per_minute:
            return False
        
        self.requests[client_id].append(now)
        return True
    
    async def __call__(self, request) -> bool:
        """FastAPI 미들웨어로 사용"""
        client_ip = request.client.host
        
        if not self.is_allowed(client_ip):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="요청이 너무 많습니다. 잠시 후 다시 시도하세요."
            )
        
        return True
