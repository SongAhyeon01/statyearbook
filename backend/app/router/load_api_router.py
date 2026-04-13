import time

from fastapi import APIRouter, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.config.database import get_database
from app.config.logging import get_logger
from app.batch import (
    step1_clear,
    step2_stat_list,
    step3_id_name,
    step4_metadata,
    step5_values,
)

logger = get_logger("router.load_api")

router = APIRouter(prefix="/api/batch", tags=["batch"])


@router.post("/load")
async def load_all_stat_data(
    start_year: int = Query(2013, description="wrttimeStartYear"),
    end_year: int = Query(2024, description="wrttimeEndYear"),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    start = time.time()
    logger.info("========== 배치 작업 시작 ==========")

    try:
        # Step 1: 기존 컬렉션 전체 삭제
        step1_start = time.time()
        dropped = await step1_clear.run(db)
        logger.info(f"Step 1 소요시간: {time.time() - step1_start:.2f}초")

        # Step 2: statList.do → stat_list_raw
        step2_start = time.time()
        stat_list_count = await step2_stat_list.run(db)
        logger.info(f"Step 2 소요시간: {time.time() - step2_start:.2f}초")

        # Step 3: stat_list_raw → stat_id_name (전체)
        step3_start = time.time()
        id_name_count = await step3_id_name.run(db)
        logger.info(f"Step 3 소요시간: {time.time() - step3_start:.2f}초")

        # Step 4: statTblItm.do → stat_yearbook 메타데이터 (statblTag='T')
        step4_start = time.time()
        metadata_summary = await step4_metadata.run(db, start_year, end_year)
        logger.info(f"Step 4 소요시간: {time.time() - step4_start:.2f}초")

        # Step 5: statDataList.do → stat_yearbook.values (statblTag='T')
        step5_start = time.time()
        values_summary = await step5_values.run(db, start_year, end_year)
        logger.info(f"Step 5 소요시간: {time.time() - step5_start:.2f}초")

    except Exception as e:
        elapsed = time.time() - start
        logger.error(f"배치 작업 실패 (소요시간: {elapsed:.2f}초): {type(e).__name__}: {e}")
        raise

    elapsed = time.time() - start
    logger.info(f"========== 배치 작업 완료 (총 소요시간: {elapsed:.2f}초) ==========")

    return {
        "message": "배치 완료",
        "elapsed_seconds": round(elapsed, 2),
        "step1_dropped_collections": dropped,
        "step2_stat_list_raw": stat_list_count,
        "step3_stat_id_name": id_name_count,
        "step4_stat_yearbook_metadata": metadata_summary,
        "step5_stat_yearbook_values": values_summary,
    }
