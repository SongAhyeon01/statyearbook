import type { StatListResponse, StatValuesResponse } from '../types/stat'

export async function fetchStatList(): Promise<StatListResponse> {
  const res = await fetch('/api/stat/list')
  if (!res.ok) throw new Error(`통계 목록 조회 실패: ${res.status}`)
  return res.json()
}

export async function fetchStatValues(
  statblId: string,
): Promise<StatValuesResponse> {
  const res = await fetch(`/api/stat/${encodeURIComponent(statblId)}`)
  if (!res.ok) throw new Error(`통계 값 조회 실패: ${res.status}`)
  return res.json()
}
