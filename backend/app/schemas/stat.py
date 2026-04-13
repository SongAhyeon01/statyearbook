# 통계 조회 API 의 응답 DTO

from typing import Any

from pydantic import BaseModel, Field


class StatItemMetadataDto(BaseModel):
    """iCol_* 한 항목의 메타데이터."""

    itmNm: str | None = None
    itmFullNm: str | None = None
    level: int | None = None
    maxLevel: int | None = None
    leaf: int | None = None
    dummyYn: str | None = None
    uiId: str | None = None
    uiNm: str | None = None


class StatValuesResponse(BaseModel):
    """statblId 의 메타데이터 및 연도별 iCol 값 응답."""

    statblId: str
    statblNm: str | None = None
    metadata: dict[str, StatItemMetadataDto] = Field(
        default_factory=dict,
        description="{iCol_*: 메타데이터} — 계층 순서 보존",
    )
    values: dict[str, dict[str, Any]] = Field(
        default_factory=dict,
        description="{연도: {iCol_*: 값}}",
    )
