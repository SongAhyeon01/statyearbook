# Step 1: 기존 DB 의 모든 컬렉션을 삭제한다.

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.config.logging import get_logger

logger = get_logger("batch.step1_clear")


async def clear_all(db: AsyncIOMotorDatabase) -> list[str]:
    """DB 의 모든 컬렉션을 삭제한다."""
    existing = await db.list_collection_names()
    for name in existing:
        await db.drop_collection(name)
    return existing


async def run(db: AsyncIOMotorDatabase) -> list[str]:
    """Step 1 실행: 모든 컬렉션 삭제."""
    logger.info("===== Step 1: 기존 컬렉션 전체 삭제 시작 =====")
    dropped = await clear_all(db)
    logger.info(f"===== Step 1 완료: {len(dropped)}개 삭제 {dropped} =====")
    return dropped
