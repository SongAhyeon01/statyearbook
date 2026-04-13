# Step 2: statList.do 에서 통계표 목록 원본 JSON 을 가져와
#         stat_list_raw 컬렉션에 저장한다.

import httpx
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.config.settings import settings
from app.config.logging import get_logger
from app.config.exceptions import MoisApiException

logger = get_logger("batch.step2_stat_list")

STAT_LIST_URL = f"{settings.MOIS_API_BASE_URL}/mois/visual/statList.do"
COLLECTION_NAME = "stat_list_raw"


async def fetch_stat_list() -> list[dict]:
    """행안부 API 에서 통계표 목록 원본 JSON 을 가져온다."""
    logger.info(f"statList.do API 호출 시작: {STAT_LIST_URL}")

    async with httpx.AsyncClient() as client:
        response = await client.get(STAT_LIST_URL, timeout=30)

    logger.info(f"statList.do 응답 상태코드: {response.status_code}")

    if response.status_code != 200:
        raise MoisApiException(f"statList API 호출 실패: status={response.status_code}")

    body = response.json()
    data = body.get("data", [])

    if not data:
        raise MoisApiException("statList API 응답에 data가 없음")

    logger.info(f"statList.do 에서 {len(data)}건 조회 완료")
    return data


async def save_raw(db: AsyncIOMotorDatabase, data: list[dict]) -> int:
    """원본 JSON 을 stat_list_raw 컬렉션에 저장한다."""
    collection = db[COLLECTION_NAME]
    insert_result = await collection.insert_many(data)
    inserted = len(insert_result.inserted_ids)
    logger.info(f"{COLLECTION_NAME} 에 {inserted}건 저장 완료")
    return inserted


async def run(db: AsyncIOMotorDatabase) -> int:
    """Step 2 실행: statList.do → stat_list_raw."""
    logger.info("===== Step 2: stat_list_raw 수집 시작 =====")
    data = await fetch_stat_list()
    count = await save_raw(db, data)
    logger.info(f"===== Step 2 완료: {count}건 저장 =====")
    return count
