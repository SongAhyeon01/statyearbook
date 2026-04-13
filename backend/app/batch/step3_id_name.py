# Step 3: stat_list_raw 의 모든 항목에서 statblId, statblNm, statblTag 를
#         추출하여 stat_id_name 컬렉션에 저장한다.

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.config.logging import get_logger

logger = get_logger("batch.step3_id_name")

SRC_COLLECTION = "stat_list_raw"
DST_COLLECTION = "stat_id_name"


async def extract_and_save(db: AsyncIOMotorDatabase) -> int:
    """stat_list_raw 의 모든 문서에서 id/nm/tag 를 추출해 stat_id_name 에 저장."""
    src = db[SRC_COLLECTION]
    dst = db[DST_COLLECTION]

    cursor = src.find({}, {"_id": 0})
    raw_items = await cursor.to_list(length=None)
    logger.info(f"{SRC_COLLECTION} 에서 {len(raw_items)}건 조회")

    if not raw_items:
        logger.warning(f"{SRC_COLLECTION} 이 비어있습니다")
        return 0

    docs = []
    for item in raw_items:
        statbl_id = item.get("statblId")
        statbl_nm = item.get("statblNm")
        statbl_tag = item.get("statblTag")
        if not statbl_id:
            logger.warning(f"statblId 가 없는 항목 건너뜀: {item}")
            continue
        docs.append(
            {
                "statblId": statbl_id,
                "statblNm": statbl_nm,
                "statblTag": statbl_tag,
            }
        )

    logger.info(f"저장 대상 {len(docs)}건 추출 완료")
    insert_result = await dst.insert_many(docs)
    inserted = len(insert_result.inserted_ids)
    logger.info(f"{DST_COLLECTION} 에 {inserted}건 저장 완료")
    return inserted


async def run(db: AsyncIOMotorDatabase) -> int:
    """Step 3 실행: stat_list_raw → stat_id_name (필터 없음)."""
    logger.info("===== Step 3: stat_id_name 저장 시작 =====")
    count = await extract_and_save(db)
    logger.info(f"===== Step 3 완료: {count}건 저장 =====")
    return count
