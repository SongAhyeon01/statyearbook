export interface StatListNode {
  statblId: string
  statblNm: string | null
  level: number | null
  isLeaf: boolean
  children: StatListNode[]
}

export interface StatListResponse {
  tree: StatListNode[]
}

export interface StatItemMetadata {
  itmNm: string | null
  itmFullNm: string | null
  level: number | null
  maxLevel: number | null
  leaf: number | null
  dummyYn: string | null
  uiId: string | null
  uiNm: string | null
}

export interface StatValuesResponse {
  statblId: string
  statblNm: string | null
  metadata: Record<string, StatItemMetadata>
  values: Record<string, Record<string, unknown>>
}
