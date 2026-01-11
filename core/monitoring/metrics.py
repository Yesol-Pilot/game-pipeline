"""
모니터링 미들웨어
Prometheus 메트릭 수집
"""

from fastapi import Request
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time


# 메트릭 정의
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

ACTIVE_REQUESTS = Gauge(
    'http_requests_active',
    'Number of active HTTP requests'
)

GAMES_CREATED = Counter(
    'games_created_total',
    'Total games created',
    ['template_type']
)

BUILDS_COMPLETED = Counter(
    'builds_completed_total',
    'Total builds completed',
    ['platform', 'status']
)

ASSETS_GENERATED = Counter(
    'assets_generated_total',
    'Total assets generated',
    ['asset_type', 'status']
)


class PrometheusMiddleware(BaseHTTPMiddleware):
    """Prometheus 메트릭 수집 미들웨어"""
    
    async def dispatch(self, request: Request, call_next):
        # 메트릭 엔드포인트는 제외
        if request.url.path == "/metrics":
            return await call_next(request)
        
        ACTIVE_REQUESTS.inc()
        start_time = time.time()
        
        try:
            response = await call_next(request)
            status = response.status_code
        except Exception as e:
            status = 500
            raise e
        finally:
            ACTIVE_REQUESTS.dec()
            
            # 메트릭 기록
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=request.url.path,
                status=status
            ).inc()
            
            REQUEST_LATENCY.labels(
                method=request.method,
                endpoint=request.url.path
            ).observe(time.time() - start_time)
        
        return response


async def metrics_endpoint(request: Request) -> Response:
    """Prometheus 메트릭 엔드포인트"""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


# 비즈니스 메트릭 헬퍼 함수
def track_game_created(template_type: str):
    """게임 생성 추적"""
    GAMES_CREATED.labels(template_type=template_type).inc()


def track_build_completed(platform: str, success: bool):
    """빌드 완료 추적"""
    status = "success" if success else "failed"
    BUILDS_COMPLETED.labels(platform=platform, status=status).inc()


def track_asset_generated(asset_type: str, success: bool):
    """자산 생성 추적"""
    status = "success" if success else "failed"
    ASSETS_GENERATED.labels(asset_type=asset_type, status=status).inc()
