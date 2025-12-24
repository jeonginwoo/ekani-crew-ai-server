from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.router import setup_routers
from config.database import engine, Base
from config.redis import redis_client
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(_: FastAPI):
    """애플리케이션 시작/종료 시 실행되는 로직"""
    # Startup
    print("[+] Starting HexaCore AI Server...")

    # 데이터베이스 테이블 생성
    Base.metadata.create_all(bind=engine)
    print("[+] Database tables created")

    # Redis 연결 테스트 (비동기)
    await redis_client.ping()
    print("[+] Redis connected")

    yield

    # Shutdown
    print("[-] Shutting down HexaCore AI Server...")
    engine.dispose()
    await redis_client.aclose()
    print("[+] Database and Redis connections closed")


app = FastAPI(
    title="Hexa AI",
    description="MBTI 서비스",
    version="0.1.0",
    lifespan=lifespan
)

origins = [
    "http://localhost:3000",  # Next.js 프론트 엔드 URL
    "https://mbtimate.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # 정확한 origin만 허용
    allow_credentials=True,      # 쿠키 허용
    allow_methods=["*"],         # 모든 HTTP 메서드 허용
    allow_headers=["*"],         # 모든 헤더 허용
)


# 라우터 등록 (router.py에서 중앙 관리)
setup_routers(app)

@app.get("/health")
async def health_check():
    """서버 상태 체크"""
    return {
        "status": "healthy",
        "database": "ok"
    }