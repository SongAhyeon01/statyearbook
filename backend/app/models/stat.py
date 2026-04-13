# stat_yearbook 컬렉션 문서 모델

from typing import Any

from pydantic import BaseModel, Field


class StatItemMetadata(BaseModel):
    """metadata.iCol_* 한 항목."""

    itmNm: str | None = None
    itmFullNm: str | None = None
    level: int | None = None
    maxLevel: int | None = None
    leaf: int | None = None
    dummyYn: str | None = None
    uiId: str | None = None
    uiNm: str | None = None


class StatYearbookDocument(BaseModel):
    """stat_yearbook 컬렉션의 한 문서."""

    statblId: str
    statblNm: str | None = None
    metadata: dict[str, StatItemMetadata] = Field(default_factory=dict)
    values: dict[str, dict[str, Any]] = Field(default_factory=dict)
