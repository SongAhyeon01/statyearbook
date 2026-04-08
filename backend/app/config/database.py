# app/config/database.py

from motor.motor_asyncio import AsyncIOMotorClient
from app.config.settings import settings
from app.config.exceptions import *

client: AsyncIOMotorClient = None
db = None

async def connect_db():
    global client, db
    try:
        client = AsyncIOMotorClient(
            settings.mongo_url,
            maxPoolSize=10,
            minPoolSize=1,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
        )
        db = client[settings.MONGO_DB_NAME]

        await client.admin.command("ping")
        print(f"MongoDB 연결 성공: {settings.MONGO_DB_NAME}")

    except Exception as e:
        raise DatabaseException(f"MongoDB 연결 실패: {e}")

async def close_db():
    global client
    if client:
        client.close()
        print("MongoDB 연결 종료")

def get_database():
    return db