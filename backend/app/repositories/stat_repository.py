# stat_yearbook 컬렉션 접근 레이어

from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.config.database import get_database

COLLECTION_NAME = "stat_yearbook"


class StatRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db[COLLECTION_NAME]

    async def find_by_statbl_id(self, statbl_id: str) -> dict | None:
        """statblId 로 stat_yearbook 문서 한 건을 조회한다."""
        return await self.collection.find_one(
            {"statblId": statbl_id},
            {"_id": 0},
        )


def get_stat_repository(
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> StatRepository:
    return StatRepository(db)
