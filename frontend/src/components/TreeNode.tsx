import type { StatListNode } from '../types/stat'

interface Props {
  node: StatListNode
  depth: number
  expandedIds: Set<string>
  selectedId: string | null
  onToggle: (id: string) => void
  onSelectLeaf: (node: StatListNode) => void
}

export default function TreeNode({
  node,
  depth,
  expandedIds,
  selectedId,
  onToggle,
  onSelectLeaf,
}: Props) {
  const isExpanded = expandedIds.has(node.statblId)
  const isSelected = selectedId === node.statblId
  const hasChildren = node.children.length > 0

  const handleClick = () => {
    if (node.isLeaf) {
      onSelectLeaf(node)
    } else {
      onToggle(node.statblId)
    }
  }

  return (
    <li className="tree-node">
      <div
        className={`tree-row ${isSelected ? 'selected' : ''} ${
          node.isLeaf ? 'leaf' : 'branch'
        }`}
        style={{ paddingLeft: 8 + depth * 14 }}
        onClick={handleClick}
        title={node.statblNm ?? node.statblId}
      >
        <span className="tree-caret">
          {hasChildren ? (isExpanded ? '▾' : '▸') : ''}
        </span>
        <span className="tree-label">{node.statblNm ?? node.statblId}</span>
      </div>
      {hasChildren && isExpanded && (
        <ul>
          {node.children.map((child) => (
            <TreeNode
              key={child.statblId}
              node={child}
              depth={depth + 1}
              expandedIds={expandedIds}
              selectedId={selectedId}
              onToggle={onToggle}
              onSelectLeaf={onSelectLeaf}
            />
          ))}
        </ul>
      )}
    </li>
  )
}
