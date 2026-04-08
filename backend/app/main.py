# start application

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# FastAPI 인스턴스 생성
app = FastAPI(
    title="MOIS Dashboard API",
    description="행안부 통계 데이터 시각화 API",
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


# 앱 시작 시 DB 연결
@app.on_event("startup")
async def startup():
    from app.config.database import connect_db
    await connect_db()
    print("Connected to DB")


# 앱 종료 시 DB 연결 해제
@app.on_event("shutdown")
async def shutdown():
    from app.config.database import close_db
    await close_db()
    print("Disconnected from DB")

# 헬스체크
@app.get("/health")
def health_check():
    return {"status": "ok"}