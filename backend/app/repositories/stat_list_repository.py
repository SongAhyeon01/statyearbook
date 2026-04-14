# stat_list_raw 컬렉션 접근 레이어

from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.config.database import get_database

COLLECTION_NAME = "stat_list_raw"


class StatListRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db[COLLECTION_NAME]

    async def find_all(self) -> list[dict]:
        """사이드바 트리 구성에 필요한 필드만 전부 조회한다."""
        cursor = self.collection.find(
            {},
            {
                "_id": 0,
                "statblId": 1,
                "statblNm": 1,
                "parStatblId": 1,
                "statblTag": 1,
                "Level": 1,
                "vOrder": 1,
            },
        )
        return await cursor.to_list(length=None)


def get_stat_list_repository(
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> StatListRepository:
    return StatListRepository(db)
