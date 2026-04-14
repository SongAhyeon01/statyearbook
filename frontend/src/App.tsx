import { useCallback, useEffect, useMemo, useState } from 'react'
import Header from './components/Header'
import NavBar from './components/NavBar'
import Sidebar from './components/Sidebar'
import StatChart from './components/StatChart'
import { fetchStatList } from './api/client'
import type { StatListNode } from './types/stat'

function collectNonLeafIds(node: StatListNode): string[] {
  if (node.isLeaf) return []
  return [node.statblId, ...node.children.flatMap(collectNonLeafIds)]
}

function findFirstLeaf(node: StatListNode): StatListNode | null {
  if (node.isLeaf) return node
  for (const child of node.children) {
    const leaf = findFirstLeaf(child)
    if (leaf) return leaf
  }
  return null
}

function findPathToId(
  nodes: StatListNode[],
  targetId: string,
): string[] | null {
  for (const node of nodes) {
    if (node.statblId === targetId) return [node.statblId]
    const childPath = findPathToId(node.children, targetId)
    if (childPath) return [node.statblId, ...childPath]
  }
  return null
}

// 백엔드가 단일 최상위 래퍼(예: '행정안전통계')를 포함해 내려줄 수 있으므로,
// 루트가 하나뿐이고 리프가 아니면 그 자식들을 실질 루트로 사용한다.
function unwrapRoots(tree: StatListNode[]): StatListNode[] {
  if (tree.length === 1 && !tree[0].isLeaf && tree[0].children.length > 0) {
    return tree[0].children
  }
  return tree
}

export default function App() {
  const [roots, setRoots] = useState<StatListNode[]>([])
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [activeRootId, setActiveRootId] = useState<string | null>(null)
  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set())
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [loadError, setLoadError] = useState<string | null>(null)

  useEffect(() => {
    fetchStatList()
      .then((res) => {
        const unwrapped = unwrapRoots(res.tree)
        setRoots(unwrapped)
        if (unwrapped.length > 0) {
          handleSelectRoot(unwrapped[0], unwrapped)
        }
      })
      .catch((e: unknown) => {
        setLoadError(e instanceof Error ? e.message : String(e))
      })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const handleSelectRoot = useCallback(
    (root: StatListNode, allRoots?: StatListNode[]) => {
      const treeRoots = allRoots ?? roots
      const descendants = collectNonLeafIds(root)
      setExpandedIds(new Set(descendants))
      setActiveRootId(root.statblId)

      const firstLeaf = findFirstLeaf(root)
      if (firstLeaf) {
        setSelectedId(firstLeaf.statblId)
      } else {
        setSelectedId(null)
      }
      // reference used so the callback has a deterministic closure
      void treeRoots
    },
    [roots],
  )

  const handleToggleNode = useCallback((id: string) => {
    setExpandedIds((prev) => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }, [])

  const handleSelectLeaf = useCallback((node: StatListNode) => {
    setSelectedId(node.statblId)
  }, [])

  // 선택된 리프가 바뀌면, 해당 노드의 조상들을 자동으로 펴서 보이게 한다.
  useEffect(() => {
    if (!selectedId) return
    const path = findPathToId(roots, selectedId)
    if (!path) return
    setExpandedIds((prev) => {
      const next = new Set(prev)
      // 마지막(자기 자신) 빼고 모두 펼침
      for (let i = 0; i < path.length - 1; i++) next.add(path[i])
      return next
    })
    // 현재 selectedId 가 속한 최상위 root 를 active 로 표시
    if (path.length > 0) setActiveRootId(path[0])
  }, [selectedId, roots])

  const toggleSidebar = useCallback(() => {
    setSidebarOpen((v) => !v)
  }, [])

  const navRoots = useMemo(() => roots, [roots])

  return (
    <div className={`app ${sidebarOpen ? '' : 'sidebar-hidden'}`}>
      <Header />
      <NavBar
        roots={navRoots}
        activeRootId={activeRootId}
        onSelectRoot={(root) => handleSelectRoot(root)}
      />
      <div className="app-body">
        <Sidebar
          roots={roots}
          expandedIds={expandedIds}
          selectedId={selectedId}
          isOpen={sidebarOpen}
          onToggleOpen={toggleSidebar}
          onToggleNode={handleToggleNode}
          onSelectLeaf={handleSelectLeaf}
        />
        <main className="app-main">
          {loadError && <div className="chart-status error">{loadError}</div>}
          {!loadError && selectedId && <StatChart statblId={selectedId} />}
          {!loadError && !selectedId && (
            <div className="chart-status">
              왼쪽 목록에서 통계 항목을 선택하세요.
            </div>
          )}
        </main>
      </div>
    </div>
  )
}
