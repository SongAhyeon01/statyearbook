import type { StatListNode } from '../types/stat'
import TreeNode from './TreeNode'

interface Props {
  roots: StatListNode[]
  expandedIds: Set<string>
  selectedId: string | null
  isOpen: boolean
  onToggleOpen: () => void
  onToggleNode: (id: string) => void
  onSelectLeaf: (node: StatListNode) => void
}

export default function Sidebar({
  roots,
  expandedIds,
  selectedId,
  isOpen,
  onToggleOpen,
  onToggleNode,
  onSelectLeaf,
}: Props) {
  return (
    <>
      <aside className={`sidebar ${isOpen ? 'open' : 'closed'}`}>
        <div className="sidebar-header">
          <span>통계 목록</span>
          <button
            className="sidebar-toggle"
            onClick={onToggleOpen}
            aria-label="사이드바 숨기기"
            title="사이드바 숨기기"
          >
            ◀
          </button>
        </div>
        <div className="sidebar-body">
          {roots.length === 0 ? (
            <div className="sidebar-empty">목록을 불러오는 중…</div>
          ) : (
            <ul className="tree-root">
              {roots.map((root) => (
                <TreeNode
                  key={root.statblId}
                  node={root}
                  depth={0}
                  expandedIds={expandedIds}
                  selectedId={selectedId}
                  onToggle={onToggleNode}
                  onSelectLeaf={onSelectLeaf}
                />
              ))}
            </ul>
          )}
        </div>
      </aside>
      {!isOpen && (
        <button
          className="sidebar-reopen"
          onClick={onToggleOpen}
          aria-label="사이드바 열기"
          title="사이드바 열기"
        >
          ▶
        </button>
      )}
    </>
  )
}
