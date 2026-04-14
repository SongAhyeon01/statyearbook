import type { StatListNode } from '../types/stat'

interface Props {
  roots: StatListNode[]
  activeRootId: string | null
  onSelectRoot: (root: StatListNode) => void
}

export default function NavBar({ roots, activeRootId, onSelectRoot }: Props) {
  return (
    <nav className="app-nav">
      <ul>
        {roots.map((root) => (
          <li key={root.statblId}>
            <button
              className={activeRootId === root.statblId ? 'active' : ''}
              onClick={() => onSelectRoot(root)}
            >
              {root.statblNm ?? root.statblId}
            </button>
          </li>
        ))}
      </ul>
    </nav>
  )
}
