# start application

from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from app.config.database import database
from app.config.logging import get_logger, setup_logger
from app.router.load_api_router import router as load_api_router

# DB 연결
@asynccontextmanager
async def lifespan(_app: FastAPI):
    # startup
    await database.connect()
    yield
    # shutdown
    await database.close()

# FastAPI 인스턴스 생성
app = FastAPI(
    title="MOIS Dashboard API",
    description="행정안전부 통계연보 시각화 API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(load_api_router)
    
    
# 로거
setup_logger()
logger = get_logger("main")


# 헬스체크
@app.get("/health")
def health_check():
    logger.info("Health check requested")
    return {"status": "ok"}