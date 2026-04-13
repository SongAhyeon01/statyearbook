# 통계 조회 서비스 레이어

from fastapi import Depends, HTTPException, status

from app.config.logging import get_logger
from app.repositories.stat_repository import StatRepository, get_stat_repository
from app.schemas.stat import StatValuesResponse

logger = get_logger("service.stat")


class StatService:
    def __init__(self, repository: StatRepository):
        self.repository = repository

    async def get_values(
        self,
        statbl_id: str,
        start_year: int | None = None,
        end_year: int | None = None,
    ) -> StatValuesResponse:
        """statblId 에 해당하는 연도별 iCol 값을 조회한다.

        start_year, end_year 는 모두 선택이며 지정된 쪽만 필터링에 사용된다.
        """
        doc = await self.repository.find_by_statbl_id(statbl_id)
        if doc is None:
            logger.warning(f"조회 실패: statblId={statbl_id} 없음")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"statblId={statbl_id} 를 찾을 수 없습니다",
            )

        values = _filter_years(doc.get("values", {}), start_year, end_year)

        # metadata 는 statTblItm.do 의 I_DATA 를 받은 순서(= 트리 DFS 순서)대로
        # 저장되어 있고, MongoDB 와 dict 가 모두 삽입 순서를 보존하므로
        # 그대로 내려보내면 계층 순서가 유지된다.
        return StatValuesResponse(
            statblId=doc["statblId"],
            statblNm=doc.get("statblNm"),
            metadata=doc.get("metadata", {}),
            values=values,
        )


def _filter_years(
    values: dict,
    start_year: int | None,
    end_year: int | None,
) -> dict:
    """values dict 을 [start_year, end_year] 범위로 필터링한다."""
    if start_year is None and end_year is None:
        return values

    filtered = {}
    for year_key, cols in values.items():
        try:
            year = int(year_key)
        except (TypeError, ValueError):
            continue
        if start_year is not None and year < start_year:
            continue
        if end_year is not None and year > end_year:
            continue
        filtered[year_key] = cols
    return filtered


def get_stat_service(
    repository: StatRepository = Depends(get_stat_repository),
) -> StatService:
    return StatService(repository)
