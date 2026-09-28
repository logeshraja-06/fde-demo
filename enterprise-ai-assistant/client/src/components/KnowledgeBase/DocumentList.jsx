/**
 * DocumentList.jsx
 * -----------------
 * Displays all processed documents as a clean list.
 *
 * Each item shows: filename, type badge, chunk count, processed status,
 * upload time, and a delete action.
 *
 * Props:
 *   documents      — array of document metadata objects
 *   selectedId     — the currently selected document's ID
 *   onSelect       — called with document ID when user clicks a row
 *   onDelete       — called with document ID when user clicks delete
 *   isLoading      — show skeleton state while fetching
 */

import { useState } from 'react'

function DocumentList({ documents, selectedId, onSelect, onDelete, isLoading }) {
  const [deletingId, setDeletingId] = useState(null)

  async function handleDelete(e, documentId) {
    // Stop click from also selecting the document
    e.stopPropagation()

    if (!window.confirm('Delete this document? This cannot be undone.')) return

    setDeletingId(documentId)
    try {
      await onDelete(documentId)
    } finally {
      setDeletingId(null)
    }
  }

  if (isLoading) {
    return (
      <div>
        <ListHeader count={0} />
        {[1, 2, 3].map((i) => (
          <SkeletonRow key={i} />
        ))}
      </div>
    )
  }

  if (documents.length === 0) {
    return (
      <div>
        <ListHeader count={0} />
        <div style={{
          padding: '32px 20px',
          textAlign: 'center',
          color: 'var(--color-text-muted)',
          fontSize: 13,
          border: '1px dashed var(--color-border)',
          borderRadius: 6,
          lineHeight: 1.7,
        }}>
          No documents uploaded yet.<br />
          Upload a PDF or TXT file above to get started.
        </div>
      </div>
    )
  }

  return (
    <div>
      <ListHeader count={documents.length} />
      <div style={{
        border: '1px solid var(--color-border)',
        borderRadius: 6,
        overflow: 'hidden',
      }}>
        {documents.map((doc, index) => {
          const isSelected = doc.document_id === selectedId
          const isDeleting = doc.document_id === deletingId

          return (
            <div
              key={doc.document_id}
              id={`doc-row-${doc.document_id}`}
              onClick={() => onSelect(doc.document_id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 14,
                padding: '13px 16px',
                background: isSelected
                  ? 'var(--color-accent-muted)'
                  : 'var(--color-bg-surface)',
                borderBottom: index < documents.length - 1
                  ? '1px solid var(--color-border)'
                  : 'none',
                cursor: 'pointer',
                transition: 'background 0.12s',
                opacity: isDeleting ? 0.5 : 1,
              }}
              onMouseEnter={(e) => {
                if (!isSelected) e.currentTarget.style.background = 'var(--color-bg-elevated)'
              }}
              onMouseLeave={(e) => {
                if (!isSelected) e.currentTarget.style.background = 'var(--color-bg-surface)'
              }}
            >
              {/* File type badge */}
              <TypeBadge type={doc.file_type} />

              {/* Document name and metadata */}
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{
                  fontSize: 13,
                  fontWeight: 500,
                  color: isSelected ? 'var(--color-accent-hover)' : 'var(--color-text-primary)',
                  whiteSpace: 'nowrap',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                }}>
                  {doc.filename}
                </div>
                <div style={{
                  fontSize: 11,
                  color: 'var(--color-text-muted)',
                  marginTop: 2,
                }}>
                  {doc.chunk_count} chunk{doc.chunk_count !== 1 ? 's' : ''} · {formatDate(doc.uploaded_at)}
                </div>
              </div>

              {/* Domain & Status indicators */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexShrink: 0 }}>
                {doc.domain && (
                  <span
                    style={{
                      fontSize: '11px',
                      color: doc.domain === 'HR' ? '#818cf8' : doc.domain === 'Finance' ? '#34d399' : doc.domain === 'IT' ? '#fbbf24' : '#94a3b8',
                      fontWeight: 600,
                      background: doc.domain === 'HR' ? 'rgba(99, 102, 241, 0.12)' : doc.domain === 'Finance' ? 'rgba(16, 185, 129, 0.12)' : doc.domain === 'IT' ? 'rgba(245, 158, 11, 0.12)' : 'rgba(148, 163, 184, 0.12)',
                      border: `1px solid ${doc.domain === 'HR' ? 'rgba(99, 102, 241, 0.25)' : doc.domain === 'Finance' ? 'rgba(16, 185, 129, 0.25)' : doc.domain === 'IT' ? 'rgba(245, 158, 11, 0.25)' : 'rgba(148, 163, 184, 0.25)'}`,
                      padding: '2px 8px',
                      borderRadius: '4px',
                    }}
                  >
                    {doc.domain}
                  </span>
                )}
                {doc.status === 'indexed' ? (
                  <span
                    style={{
                      fontSize: '11px',
                      color: 'var(--color-success)',
                      fontWeight: 600,
                      background: 'rgba(16, 185, 129, 0.1)',
                      border: '1px solid rgba(16, 185, 129, 0.25)',
                      padding: '2px 8px',
                      borderRadius: '4px',
                    }}
                  >
                    ✓ Indexed
                  </span>
                ) : (
                  <span
                    style={{
                      fontSize: '11px',
                      color: '#60a5fa',
                      fontWeight: 500,
                      background: 'rgba(59, 130, 246, 0.1)',
                      border: '1px solid rgba(59, 130, 246, 0.25)',
                      padding: '2px 8px',
                      borderRadius: '4px',
                    }}
                  >
                    ✓ Processed
                  </span>
                )}
              </div>

              {/* Delete button */}
              <button
                id={`delete-${doc.document_id}`}
                onClick={(e) => handleDelete(e, doc.document_id)}
                disabled={isDeleting}
                title="Delete document"
                style={{
                  background: 'none',
                  border: 'none',
                  cursor: isDeleting ? 'default' : 'pointer',
                  padding: '4px 6px',
                  borderRadius: 4,
                  color: 'var(--color-text-muted)',
                  fontSize: 13,
                  fontFamily: 'inherit',
                  flexShrink: 0,
                  transition: 'color 0.12s, background 0.12s',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.color = 'var(--color-error)'
                  e.currentTarget.style.background = 'rgba(248,113,113,0.1)'
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.color = 'var(--color-text-muted)'
                  e.currentTarget.style.background = 'none'
                }}
              >
                {isDeleting ? '...' : '✕'}
              </button>
            </div>
          )
        })}
      </div>
    </div>
  )
}

// ── Sub-components ─────────────────────────────────────────────────────────────

function ListHeader({ count }) {
  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      marginBottom: 10,
    }}>
      <div style={{
        fontSize: 11,
        fontWeight: 600,
        color: 'var(--color-text-muted)',
        textTransform: 'uppercase',
        letterSpacing: '0.08em',
      }}>
        Documents
      </div>
      {count > 0 && (
        <div style={{
          fontSize: 10,
          color: 'var(--color-text-muted)',
          background: 'var(--color-bg-elevated)',
          padding: '2px 7px',
          borderRadius: 3,
        }}>
          {count}
        </div>
      )}
    </div>
  )
}

function TypeBadge({ type }) {
  const colors = {
    pdf: { bg: 'rgba(239,68,68,0.12)', color: '#f87171' },
    txt: { bg: 'rgba(99,102,241,0.12)', color: '#818cf8' },
  }
  const style = colors[type] || colors.txt
  return (
    <div style={{
      fontSize: 9,
      fontWeight: 700,
      letterSpacing: '0.05em',
      textTransform: 'uppercase',
      padding: '3px 6px',
      borderRadius: 3,
      background: style.bg,
      color: style.color,
      flexShrink: 0,
      fontFamily: 'monospace',
    }}>
      {type}
    </div>
  )
}

function SkeletonRow() {
  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      gap: 14,
      padding: '14px 16px',
      background: 'var(--color-bg-surface)',
      borderBottom: '1px solid var(--color-border)',
    }}>
      <div style={{ width: 28, height: 16, borderRadius: 3, background: 'var(--color-bg-elevated)' }} />
      <div style={{ flex: 1 }}>
        <div style={{ width: '55%', height: 12, borderRadius: 3, background: 'var(--color-bg-elevated)', marginBottom: 6 }} />
        <div style={{ width: '30%', height: 10, borderRadius: 3, background: 'var(--color-border)' }} />
      </div>
    </div>
  )
}

function formatDate(isoString) {
  if (!isoString) return '—'
  try {
    return new Date(isoString).toLocaleString(undefined, {
      month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit',
    })
  } catch {
    return '—'
  }
}

export default DocumentList
