# Step 4: stat_id_name 에서 statblTag='T' 인 항목에 대해
#         statTblItm.do 로 항목 메타데이터를 가져와
#         stat_yearbook 컬렉션에 {statblId, statblNm, metadata, values} 로 저장한다.

import httpx
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.config.settings import settings
from app.config.logging import get_logger
from app.config.exceptions import MoisApiException

logger = get_logger("batch.step4_metadata")

STAT_TBL_ITM_URL = f"{settings.MOIS_API_BASE_URL}/mois/visual/statTblItm.do"
SRC_COLLECTION = "stat_id_name"
DST_COLLECTION = "stat_yearbook"


async def fetch_metadata(
    statbl_id: str, start_year: int, end_year: int
) -> list[dict]:
    """statblId 의 항목 메타데이터를 조회한다."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            STAT_TBL_ITM_URL,
            data={
                "statblId": statbl_id,
                "wrttimeStartYear": start_year,
                "wrttimeEndYear": end_year,
            },
            timeout=30,
        )

    if response.status_code != 200:
        raise MoisApiException(
            f"statTblItm API 호출 실패: statblId={statbl_id}, status={response.status_code}"
        )

    body = response.json()
    return body.get("data", {}).get("I_DATA", [])


def _progress_bar(current: int, total: int, width: int = 30) -> str:
    ratio = current / total
    filled = int(width * ratio)
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}] {current}/{total} ({ratio:.0%})"


async def load_all(
    db: AsyncIOMotorDatabase, start_year: int, end_year: int
) -> dict:
    """statblTag='T' 대상에 대해 메타데이터를 가져와 stat_yearbook 에 저장."""
    src = db[SRC_COLLECTION]
    dst = db[DST_COLLECTION]

    cursor = src.find({"statblTag": "T"}, {"_id": 0})
    targets = await cursor.to_list(length=None)
    logger.info(f"{SRC_COLLECTION} 에서 statblTag='T' 항목 {len(targets)}건 조회")

    if not targets:
        logger.warning("statblTag='T' 인 항목이 없습니다")
        return {"success": 0, "fail": 0}

    success_count = 0
    fail_count = 0
    total = len(targets)
    log_interval = max(1, total // 10)

    for idx, item in enumerate(targets, 1):
        statbl_id = item["statblId"]
        statbl_nm = item.get("statblNm", "")

        try:
            i_data = await fetch_metadata(statbl_id, start_year, end_year)

            metadata = {}
            for row in i_data:
                datano = row.get("datano")
                if datano is None:
                    continue
                metadata[f"iCol_{datano}"] = {
                    "itmNm": row.get("itmNm"),
                    "itmFullNm": row.get("itmFullNm"),
                    "level": row.get("level"),
                    "maxLevel": row.get("maxLevel"),
                    "leaf": row.get("leaf"),
                    "dummyYn": row.get("dummyYn"),
                    "uiId": row.get("uiId"),
                    "uiNm": row.get("uiNm"),
                }

            await dst.insert_one(
                {
                    "statblId": statbl_id,
                    "statblNm": statbl_nm,
                    "metadata": metadata,
                    "values": {},
                }
            )
            success_count += 1

        except MoisApiException as e:
            fail_count += 1
            logger.error(f"API 호출 실패: {statbl_nm}({statbl_id}) - {e}")
        except Exception as e:
            fail_count += 1
            logger.error(
                f"예상치 못한 오류: {statbl_nm}({statbl_id}) - {type(e).__name__}: {e}"
            )

        if idx % log_interval == 0 or idx == total:
            logger.info(
                f"진행: {_progress_bar(idx, total)} "
                f"(성공={success_count} 실패={fail_count})"
            )

    summary = {"success": success_count, "fail": fail_count}
    logger.info(f"{DST_COLLECTION} 메타데이터 저장 결과: {summary}")
    return summary


async def run(
    db: AsyncIOMotorDatabase, start_year: int, end_year: int
) -> dict:
    """Step 4 실행: statTblItm.do → stat_yearbook 메타데이터."""
    logger.info(
        f"===== Step 4: stat_yearbook 메타데이터 수집 시작 (years={start_year}~{end_year}) ====="
    )
    summary = await load_all(db, start_year, end_year)
    logger.info(f"===== Step 4 완료: {summary} =====")
    return summary
