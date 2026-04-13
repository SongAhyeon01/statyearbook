# 통계 조회 라우터

from fastapi import APIRouter, Depends, Path, Query

from app.config.logging import get_logger
from app.schemas.stat import StatValuesResponse
from app.services.stat_service import StatService, get_stat_service

logger = get_logger("router.stat")

router = APIRouter(prefix="/api/stat", tags=["stat"])


@router.get("/{statbl_id}", response_model=StatValuesResponse)
async def get_stat_values(
    statbl_id: str = Path(..., description="조회할 statblId"),
    start_year: int | None = Query(None, description="시작 연도 (선택)"),
    end_year: int | None = Query(None, description="마지막 연도 (선택)"),
    service: StatService = Depends(get_stat_service),
) -> StatValuesResponse:
    logger.info(
        f"통계 조회 요청: statblId={statbl_id} "
        f"start_year={start_year} end_year={end_year}"
    )
    return await service.get_values(statbl_id, start_year, end_year)
