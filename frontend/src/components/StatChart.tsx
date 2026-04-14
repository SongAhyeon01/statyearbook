import { useEffect, useMemo, useState } from 'react'
import Plotly from 'plotly.js-dist-min'
import createPlotlyComponent from 'react-plotly.js/factory'
import { fetchStatValues } from '../api/client'
import type { StatValuesResponse } from '../types/stat'

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const Plot = createPlotlyComponent(Plotly as any)

interface Props {
  statblId: string
}

const TOTAL_KEYWORDS = ['합계', '총계', '총합', '전체', '계']

function parseValue(v: unknown): number | null {
  if (v === null || v === undefined) return null
  if (typeof v === 'number') return Number.isFinite(v) ? v : null
  if (typeof v === 'string') {
    const cleaned = v.replace(/,/g, '').trim()
    if (cleaned === '' || cleaned === '-') return null
    const n = Number(cleaned)
    return Number.isFinite(n) ? n : null
  }
  return null
}

function nameMatchesTotal(name: string | null | undefined): boolean {
  if (!name) return false
  return TOTAL_KEYWORDS.some((kw) => name.includes(kw))
}

function pickDefaultColumn(data: StatValuesResponse): string | null {
  const entries = Object.entries(data.metadata).filter(
    ([, meta]) => meta.dummyYn !== 'Y',
  )
  if (entries.length === 0) return null

  // 1순위: 이름에 합계/총계/총합/전체/계 포함
  const byName = entries.find(
    ([, m]) => nameMatchesTotal(m.itmNm) || nameMatchesTotal(m.itmFullNm),
  )
  if (byName) return byName[0]

  // 2순위: 가장 상위 레벨(level 값이 가장 작은)
  const minLevel = Math.min(
    ...entries.map(([, m]) => m.level ?? Number.MAX_SAFE_INTEGER),
  )
  const byLevel = entries.find(
    ([, m]) => (m.level ?? Number.MAX_SAFE_INTEGER) === minLevel,
  )
  if (byLevel) return byLevel[0]

  // 3순위: 첫 컬럼
  return entries[0][0]
}

export default function StatChart({ statblId }: Props) {
  const [data, setData] = useState<StatValuesResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [selectedCol, setSelectedCol] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)
    setData(null)
    setSelectedCol(null)

    fetchStatValues(statblId)
      .then((res) => {
        if (cancelled) return
        setData(res)
        setSelectedCol(pickDefaultColumn(res))
      })
      .catch((e: unknown) => {
        if (cancelled) return
        setError(e instanceof Error ? e.message : String(e))
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [statblId])

  const columnOptions = useMemo(() => {
    if (!data) return []
    return Object.entries(data.metadata)
      .filter(([, m]) => m.dummyYn !== 'Y')
      .map(([key, m]) => ({
        key,
        label: m.itmFullNm ?? m.itmNm ?? key,
      }))
  }, [data])

  const series = useMemo(() => {
    if (!data || !selectedCol) return { x: [] as string[], y: [] as (number | null)[] }
    const years = Object.keys(data.values)
      .map((y) => y)
      .filter((y) => /^\d{4}$/.test(y))
      .sort()
    const y = years.map((year) => parseValue(data.values[year]?.[selectedCol]))
    return { x: years, y }
  }, [data, selectedCol])

  if (loading) return <div className="chart-status">불러오는 중…</div>
  if (error) return <div className="chart-status error">{error}</div>
  if (!data) return <div className="chart-status">통계 항목을 선택하세요.</div>

  const selectedMeta = selectedCol ? data.metadata[selectedCol] : null
  const selectedLabel =
    selectedMeta?.itmFullNm ?? selectedMeta?.itmNm ?? selectedCol ?? ''

  return (
    <div className="chart-wrap">
      <div className="chart-head">
        <h2>{data.statblNm ?? data.statblId}</h2>
        <div className="chart-controls">
          <label>
            컬럼:
            <select
              value={selectedCol ?? ''}
              onChange={(e) => setSelectedCol(e.target.value)}
            >
              {columnOptions.map((opt) => (
                <option key={opt.key} value={opt.key}>
                  {opt.label}
                </option>
              ))}
            </select>
          </label>
        </div>
      </div>
      <Plot
        data={[
          {
            x: series.x,
            y: series.y,
            type: 'scatter',
            mode: 'lines+markers',
            name: selectedLabel,
            line: { color: '#1f5fa8', width: 2 },
            marker: { size: 6 },
          },
        ]}
        layout={{
          autosize: true,
          margin: { l: 60, r: 20, t: 10, b: 50 },
          xaxis: { title: { text: '연도' }, type: 'category' },
          yaxis: { title: { text: selectedLabel }, rangemode: 'tozero' },
          hovermode: 'x unified',
          showlegend: false,
        }}
        style={{ width: '100%', height: '480px' }}
        config={{ responsive: true, displaylogo: false }}
        useResizeHandler
      />
    </div>
  )
}
