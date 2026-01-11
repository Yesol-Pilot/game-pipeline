"""
캐싱 레이어
Redis 기반 캐싱 및 메모리 캐싱
"""

import json
import hashlib
from datetime import datetime, timedelta
from typing import Any, Optional, Dict, Callable
from functools import wraps
from dataclasses import dataclass


@dataclass
class CacheEntry:
    """캐시 항목"""
    key: str
    value: Any
    created_at: datetime
    expires_at: Optional[datetime]
    hit_count: int = 0


class MemoryCache:
    """메모리 캐시"""
    
    def __init__(self, default_ttl: int = 3600):
        """
        Args:
            default_ttl: 기본 TTL (초)
        """
        self.default_ttl = default_ttl
        self._cache: Dict[str, CacheEntry] = {}
    
    def _is_expired(self, entry: CacheEntry) -> bool:
        """만료 여부 확인"""
        if entry.expires_at is None:
            return False
        return datetime.now() > entry.expires_at
    
    def get(self, key: str) -> Optional[Any]:
        """캐시 조회"""
        if key not in self._cache:
            return None
        
        entry = self._cache[key]
        
        if self._is_expired(entry):
            del self._cache[key]
            return None
        
        entry.hit_count += 1
        return entry.value
    
    def set(self, key: str, value: Any, ttl: int = None) -> None:
        """캐시 저장"""
        if ttl is None:
            ttl = self.default_ttl
        
        expires_at = datetime.now() + timedelta(seconds=ttl) if ttl > 0 else None
        
        self._cache[key] = CacheEntry(
            key=key,
            value=value,
            created_at=datetime.now(),
            expires_at=expires_at
        )
    
    def delete(self, key: str) -> bool:
        """캐시 삭제"""
        if key in self._cache:
            del self._cache[key]
            return True
        return False
    
    def clear(self) -> None:
        """전체 캐시 삭제"""
        self._cache.clear()
    
    def cleanup(self) -> int:
        """만료된 항목 정리"""
        expired = [k for k, v in self._cache.items() if self._is_expired(v)]
        for key in expired:
            del self._cache[key]
        return len(expired)
    
    def stats(self) -> Dict[str, Any]:
        """캐시 통계"""
        total_hits = sum(e.hit_count for e in self._cache.values())
        return {
            "entries": len(self._cache),
            "total_hits": total_hits,
        }


class RedisCache:
    """Redis 캐시"""
    
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        self.host = host
        self.port = port
        self.db = db
        self._client = None
    
    def _get_client(self):
        """Redis 클라이언트 가져오기"""
        if self._client is None:
            try:
                import redis
                self._client = redis.Redis(
                    host=self.host,
                    port=self.port,
                    db=self.db,
                    decode_responses=True
                )
            except ImportError:
                print("redis 패키지 필요: pip install redis")
                return None
        return self._client
    
    def get(self, key: str) -> Optional[Any]:
        """캐시 조회"""
        client = self._get_client()
        if client is None:
            return None
        
        try:
            data = client.get(key)
            if data:
                return json.loads(data)
        except Exception as e:
            print(f"Redis get 오류: {e}")
        
        return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """캐시 저장"""
        client = self._get_client()
        if client is None:
            return
        
        try:
            data = json.dumps(value, ensure_ascii=False, default=str)
            client.setex(key, ttl, data)
        except Exception as e:
            print(f"Redis set 오류: {e}")
    
    def delete(self, key: str) -> bool:
        """캐시 삭제"""
        client = self._get_client()
        if client is None:
            return False
        
        try:
            return client.delete(key) > 0
        except Exception as e:
            print(f"Redis delete 오류: {e}")
            return False


class CacheManager:
    """통합 캐시 매니저"""
    
    def __init__(self, use_redis: bool = False, **kwargs):
        if use_redis:
            self.cache = RedisCache(**kwargs)
        else:
            self.cache = MemoryCache(**kwargs)
    
    def cached(self, ttl: int = 3600, key_prefix: str = ""):
        """캐싱 데코레이터"""
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # 캐시 키 생성
                key_parts = [key_prefix, func.__name__]
                key_parts.extend(str(a) for a in args)
                key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
                cache_key = hashlib.md5(":".join(key_parts).encode()).hexdigest()
                
                # 캐시 조회
                cached = self.cache.get(cache_key)
                if cached is not None:
                    return cached
                
                # 함수 실행 및 캐싱
                result = func(*args, **kwargs)
                self.cache.set(cache_key, result, ttl)
                return result
            
            return wrapper
        return decorator
    
    def invalidate(self, key: str) -> bool:
        """캐시 무효화"""
        return self.cache.delete(key)


# 전역 캐시 인스턴스
_cache_manager = None


def get_cache() -> CacheManager:
    """전역 캐시 매니저"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager


# 사용 예시
def main():
    cache = get_cache()
    
    # 기본 사용
    cache.cache.set("key1", {"data": "value"}, ttl=60)
    result = cache.cache.get("key1")
    print(f"캐시 결과: {result}")
    
    # 데코레이터 사용
    @cache.cached(ttl=300, key_prefix="gdd")
    def expensive_gdd_generation(template_type: str):
        print(f"GDD 생성 중: {template_type}")
        return {"template": template_type, "generated": True}
    
    # 첫 번째 호출 (캐시 미스)
    result1 = expensive_gdd_generation("runner")
    
    # 두 번째 호출 (캐시 히트)
    result2 = expensive_gdd_generation("runner")
    
    print(f"통계: {cache.cache.stats()}")


if __name__ == "__main__":
    main()
