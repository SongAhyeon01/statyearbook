# start application

from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from app.config.database import close_db, connect_db

# FastAPI 인스턴스 생성
app = FastAPI(
    title="MOIS Dashboard API",
    description="행정안전부 통계연보 시각화 API",
    version="1.0.0"
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


# DB 연결
@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    await connect_db()
    yield
    # shutdown
    await close_db()


# 헬스체크
@app.get("/health")
def health_check():
    return {"status": "ok"}