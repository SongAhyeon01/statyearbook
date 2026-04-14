# 통계표 목록(사이드바) 트리 응답 DTO

from pydantic import BaseModel, Field


class StatListNode(BaseModel):
    """통계표 목록의 계층 노드.

    리프 노드(isLeaf=True)의 statblId 는 'M' 으로 시작하며
    /api/stat/{statblId} 호출에 사용된다.
    """

    statblId: str
    statblNm: str | None = None
    level: int | None = None
    isLeaf: bool = False
    children: list["StatListNode"] = Field(default_factory=list)


StatListNode.model_rebuild()


class StatListResponse(BaseModel):
    tree: list[StatListNode] = Field(default_factory=list)
