import React, { useState } from 'react'

/**
 * SourceList.jsx
 * --------------
 * Reusable component for displaying grounded knowledge sources and citations.
 *
 * Requirements:
 * - Document name
 * - Page number (or "Page: Not available" if missing)
 * - Actual retrieval score or distance (unmodified from backend)
 * - Expandable chunk text preview
 */
export default function SourceList({ sources = [], title = 'Sources' }) {
  const [expandedIndex, setExpandedIndex] = useState(null)

  if (!sources || sources.length === 0) return null

  const toggleExpand = (index) => {
    setExpandedIndex(expandedIndex === index ? null : index)
  }

  return (
    <div
      style={{
        marginTop: '12px',
        paddingTop: '10px',
        borderTop: '1px solid rgba(255, 255, 255, 0.08)',
        fontSize: '12px',
      }}
    >
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          fontWeight: 600,
          color: 'var(--color-text-secondary)',
          textTransform: 'uppercase',
          letterSpacing: '0.06em',
          fontSize: '11px',
          marginBottom: '8px',
        }}
      >
        <span>📚</span>
        <span>{title}</span>
        <span
          style={{
            fontSize: '10px',
            background: 'var(--color-bg-base)',
            padding: '1px 6px',
            borderRadius: '10px',
            color: 'var(--color-text-muted)',
            border: '1px solid var(--color-border)',
          }}
        >
          {sources.length}
        </span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
        {sources.map((src, idx) => {
          const isExpanded = expandedIndex === idx
          // Document name
          const docName = src.source || src.document_name || src.filename || 'Unknown Document'
          // Page display rule: if unavailable, display "Page: Not available"
          const pageDisplay = src.page !== undefined && src.page !== null && src.page !== ''
            ? `Page ${src.page}`
            : 'Page: Not available'
          // Retrieval score / distance: use real backend value
          let metricLabel = 'Score'
          let metricValue = null
          if (src.distance !== undefined && src.distance !== null) {
            metricLabel = 'Distance'
            metricValue = typeof src.distance === 'number' ? src.distance.toFixed(4) : src.distance
          } else if (src.score !== undefined && src.score !== null) {
            metricLabel = 'Score'
            metricValue = typeof src.score === 'number' ? src.score.toFixed(4) : src.score
          } else if (src.similarity !== undefined && src.similarity !== null) {
            metricLabel = 'Similarity'
            metricValue = typeof src.similarity === 'number' ? src.similarity.toFixed(4) : src.similarity
          }

          return (
            <div
              key={idx}
              style={{
                background: 'var(--color-bg-base)',
                border: '1px solid var(--color-border)',
                borderRadius: '6px',
                overflow: 'hidden',
                transition: 'border-color 0.15s ease',
              }}
            >
              {/* Header / Clickable row */}
              <div
                onClick={() => toggleExpand(idx)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '8px 12px',
                  cursor: 'pointer',
                  userSelect: 'none',
                  background: isExpanded ? 'var(--color-bg-elevated)' : 'transparent',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', minWidth: 0 }}>
                  <span style={{ fontSize: '10px', color: '#818cf8', fontWeight: 700 }}>
                    {isExpanded ? '▼' : '▸'}
                  </span>
                  <span
                    style={{
                      fontWeight: 600,
                      color: 'var(--color-text-primary)',
                      whiteSpace: 'nowrap',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                    }}
                    title={docName}
                  >
                    {docName}
                  </span>
                  <span style={{ color: 'var(--color-text-muted)', fontSize: '11px' }}>
                    &bull; {pageDisplay}
                  </span>
                </div>

                {metricValue !== null && (
                  <span
                    style={{
                      fontSize: '10px',
                      color: '#38bdf8',
                      background: 'rgba(56, 189, 248, 0.1)',
                      border: '1px solid rgba(56, 189, 248, 0.25)',
                      padding: '2px 6px',
                      borderRadius: '4px',
                      fontWeight: 600,
                      flexShrink: 0,
                      marginLeft: '8px',
                    }}
                  >
                    {metricLabel}: {metricValue}
                  </span>
                )}
              </div>

              {/* Expandable Chunk Content */}
              {isExpanded && (
                <div
                  style={{
                    padding: '10px 12px',
                    borderTop: '1px solid var(--color-border)',
                    background: 'var(--color-bg-surface)',
                    fontSize: '11px',
                    color: 'var(--color-text-secondary)',
                    lineHeight: 1.6,
                    whiteSpace: 'pre-wrap',
                    fontFamily: 'inherit',
                  }}
                >
                  <div
                    style={{
                      fontSize: '10px',
                      textTransform: 'uppercase',
                      letterSpacing: '0.05em',
                      color: 'var(--color-text-muted)',
                      fontWeight: 600,
                      marginBottom: '4px',
                    }}
                  >
                    Extracted Chunk Content:
                  </div>
                  {src.text || src.content || 'No text snippet available.'}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
