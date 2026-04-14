# 사이드바용 통계표 목록 트리 서비스

from fastapi import Depends

from app.config.logging import get_logger
from app.repositories.stat_list_repository import (
    StatListRepository,
    get_stat_list_repository,
)
from app.schemas.stat_list import StatListNode, StatListResponse

logger = get_logger("service.stat_list")

# statblTag == 'T' 인 노드가 실제 통계표(리프) 이고,
# statblId 가 'M' 으로 시작한다. 그 외는 카테고리(C).
LEAF_TAG = "T"


class StatListService:
    def __init__(self, repository: StatListRepository):
        self.repository = repository

    async def get_tree(self) -> StatListResponse:
        """stat_list_raw 의 전체 목록을 parStatblId 기준으로 트리 구성해 반환."""
        docs = await self.repository.find_all()
        logger.info(f"stat_list_raw 조회: {len(docs)}건")

        nodes: dict[str, StatListNode] = {}
        children_map: dict[str, list[StatListNode]] = {}

        for doc in docs:
            statbl_id = doc.get("statblId")
            if not statbl_id:
                continue
            node = StatListNode(
                statblId=statbl_id,
                statblNm=doc.get("statblNm"),
                level=doc.get("Level"),
                isLeaf=doc.get("statblTag") == LEAF_TAG,
            )
            nodes[statbl_id] = node
            children_map.setdefault(doc.get("parStatblId") or "", []).append(
                (doc.get("vOrder") or 0, node)
            )

        # vOrder 로 정렬해서 children 에 연결
        for parent_id, items in children_map.items():
            items.sort(key=lambda x: x[0])
            parent = nodes.get(parent_id)
            if parent is None:
                continue
            parent.children = [n for _, n in items]

        # 부모가 현재 목록에 없는 노드들이 루트
        roots = [
            n for _, n in sorted(
                (
                    (v_order, node)
                    for parent_id, items in children_map.items()
                    if parent_id not in nodes
                    for v_order, node in items
                ),
                key=lambda x: x[0],
            )
        ]
        logger.info(f"트리 루트 {len(roots)}개 구성 완료")
        return StatListResponse(tree=roots)


def get_stat_list_service(
    repository: StatListRepository = Depends(get_stat_list_repository),
) -> StatListService:
    return StatListService(repository)
