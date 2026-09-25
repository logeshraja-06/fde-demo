import React, { useState } from 'react'

/**
 * RetrievedContext.jsx
 * --------------------
 * Expandable panel displaying the exact retrieved context chunks that were
 * sent to the LLM generation prompt.
 *
 * Requirements:
 * - Proves what context the LLM received
 * - Shows Source, Page, and the raw chunk content
 * - Expandable / collapsible for clean UX
 */
export default function RetrievedContext({ sources = [] }) {
  const [isOpen, setIsOpen] = useState(false)

  if (!sources || sources.length === 0) return null

  return (
    <div
      style={{
        marginTop: '10px',
        border: '1px solid rgba(99, 102, 241, 0.25)',
        borderRadius: '8px',
        background: 'rgba(15, 23, 42, 0.4)',
        overflow: 'hidden',
      }}
    >
      {/* Header bar with toggle */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        style={{
          width: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '8px 12px',
          background: 'none',
          border: 'none',
          color: '#818cf8',
          fontSize: '11px',
          fontWeight: 600,
          cursor: 'pointer',
          textAlign: 'left',
          transition: 'background 0.15s ease',
        }}
        onMouseEnter={(e) => (e.currentTarget.style.background = 'rgba(99, 102, 241, 0.08)')}
        onMouseLeave={(e) => (e.currentTarget.style.background = 'none')}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span>🔍</span>
          <span>Retrieved Context ({sources.length} chunk{sources.length > 1 ? 's' : ''} fed to LLM)</span>
        </div>
        <span style={{ fontSize: '10px' }}>{isOpen ? '▲ Hide context' : '▼ View context'}</span>
      </button>

      {/* Expanded Content */}
      {isOpen && (
        <div
          style={{
            padding: '12px',
            borderTop: '1px solid rgba(99, 102, 241, 0.2)',
            display: 'flex',
            flexDirection: 'column',
            gap: '10px',
            background: 'var(--color-bg-base)',
          }}
        >
          {sources.map((src, idx) => {
            const docName = src.source || src.document_name || src.filename || 'Unknown Document'
            const pageDisplay = src.page !== undefined && src.page !== null && src.page !== ''
              ? `Page: ${src.page}`
              : 'Page: Not available'

            return (
              <div
                key={idx}
                style={{
                  border: '1px solid var(--color-border)',
                  borderRadius: '6px',
                  background: 'var(--color-bg-surface)',
                  padding: '10px',
                  fontSize: '11px',
                }}
              >
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    marginBottom: '6px',
                    paddingBottom: '4px',
                    borderBottom: '1px solid var(--color-border)',
                  }}
                >
                  <span style={{ fontWeight: 600, color: 'var(--color-text-primary)' }}>
                    Source: {docName}
                  </span>
                  <span style={{ color: 'var(--color-text-muted)' }}>
                    {pageDisplay}
                  </span>
                </div>
                <div
                  style={{
                    color: 'var(--color-text-secondary)',
                    whiteSpace: 'pre-wrap',
                    lineHeight: 1.55,
                    fontFamily: 'inherit',
                  }}
                >
                  {src.text || src.content || 'No text content available.'}
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
