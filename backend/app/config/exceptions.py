# app/config/exceptions.py

from fastapi import Request
from fastapi.responses import JSONResponse


# 사용자 정의 예외 클래스
class DatabaseException(Exception):
    def __init__(self, message: str = "데이터베이스 연결 오류"):
        self.message = message
        super().__init__(self.message)

class MoisApiException(Exception):
    def __init__(self, message: str = "행정안전부 API 호출 오류"):
        self.message = message
        super().__init__(self.message)

class NotFoundException(Exception):
    def __init__(self, message: str = "데이터 없음"):
        self.message = message
        super().__init__(self.message)



# 예외 핸들러 등록
def register_exception_handlers(app):

    @app.exception_handler(DatabaseException)
    async def database_exception_handler(request: Request, exc: DatabaseException):
        return JSONResponse(
            status_code=500,
            content={"error": "DATABASE_ERROR", "message": exc.message}
        )

    @app.exception_handler(MoisApiException)
    async def mois_api_exception_handler(request: Request, exc: MoisApiException):
        return JSONResponse(
            status_code=502,
            content={"error": "EXTERNAL_API_ERROR", "message": exc.message}
        )

    @app.exception_handler(NotFoundException)
    async def not_found_exception_handler(request: Request, exc: NotFoundException):
        return JSONResponse(
            status_code=404,
            content={"error": "NOT_FOUND", "message": exc.message}
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={"error": "INTERNAL_ERROR", "message": "서버 내부 오류가 발생"}
        )