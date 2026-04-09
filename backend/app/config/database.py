# app/config/database.py

from motor.motor_asyncio import AsyncIOMotorClient
from app.config.settings import settings
from app.config.exceptions import DatabaseException
from app.config.logging import get_logger

# 로거
logger = get_logger("database")

class Database:

    def __init__(self):
        self.client: AsyncIOMotorClient = None
        self.db = None
        

    # MongoDB 연결
    async def connect(self):
        try:
            self.client = AsyncIOMotorClient(
                settings.mongo_url,
                maxPoolSize=10,
                minPoolSize=1,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
            )
            self.db = self.client[settings.MONGO_DB_NAME]
            await self.client.admin.command("ping")
            logger.info("MongoDB 연결 성공")
        except Exception as e:
            raise DatabaseException(f"MongoDB 연결 실패: {e}")

    # MongoDB 연결 종료
    async def close(self):
        if self.client:
            self.client.close()
            logger.info("MongoDB 연결 종료")


database = Database()


def get_database():
    return database.db