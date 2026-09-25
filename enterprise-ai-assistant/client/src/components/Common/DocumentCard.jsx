import React from 'react'

/**
 * DocumentCard.jsx
 * ----------------
 * Card representing a processed knowledge document with metadata,
 * chunk count, status, and click selection.
 */
export default function DocumentCard({
  document,
  isSelected,
  onSelect,
  onDelete,
}) {
  const {
    document_id,
    filename,
    total_pages,
    chunk_count,
    uploaded_at,
    file_size_bytes,
    file_type,
  } = document

  const formatSize = (bytes) => {
    if (!bytes) return ''
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  const formatDate = (isoString) => {
    if (!isoString) return 'Recent'
    try {
      const d = new Date(isoString)
      return d.toLocaleDateString(undefined, {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      })
    } catch {
      return isoString
    }
  }

  return (
    <div
      onClick={() => onSelect && onSelect(document_id)}
      style={{
        background: isSelected ? 'var(--color-bg-elevated)' : 'var(--color-bg-surface)',
        border: `1px solid ${isSelected ? 'var(--color-brand)' : 'var(--color-border)'}`,
        borderRadius: '8px',
        padding: '14px 16px',
        cursor: 'pointer',
        transition: 'all 0.15s ease',
        display: 'flex',
        flexDirection: 'column',
        gap: '8px',
      }}
      onMouseEnter={(e) => {
        if (!isSelected) e.currentTarget.style.borderColor = 'rgba(99, 102, 241, 0.4)'
      }}
      onMouseLeave={(e) => {
        if (!isSelected) e.currentTarget.style.borderColor = 'var(--color-border)'
      }}
    >
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '8px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', minWidth: 0 }}>
          <span style={{ fontSize: '18px' }}>{file_type === 'pdf' ? '📄' : '📝'}</span>
          <div style={{ minWidth: 0 }}>
            <div
              style={{
                fontSize: '13px',
                fontWeight: 600,
                color: 'var(--color-text-primary)',
                whiteSpace: 'nowrap',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
              }}
              title={filename}
            >
              {filename}
            </div>
            <div style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>
              Uploaded {formatDate(uploaded_at)}
            </div>
          </div>
        </div>

        {onDelete && (
          <button
            onClick={(e) => {
              e.stopPropagation()
              if (window.confirm(`Delete ${filename}?`)) {
                onDelete(document_id)
              }
            }}
            title="Delete document"
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--color-text-muted)',
              cursor: 'pointer',
              fontSize: '14px',
              padding: '2px 6px',
              borderRadius: '4px',
              lineHeight: 1,
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.color = '#ef4444'
              e.currentTarget.style.background = 'rgba(239, 68, 68, 0.1)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.color = 'var(--color-text-muted)'
              e.currentTarget.style.background = 'none'
            }}
          >
            ✕
          </button>
        )}
      </div>

      {/* Stats bar */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          fontSize: '11px',
          color: 'var(--color-text-secondary)',
          borderTop: '1px solid var(--color-border)',
          paddingTop: '8px',
          marginTop: '2px',
        }}
      >
        <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <strong style={{ color: 'var(--color-text-primary)' }}>{chunk_count || 0}</strong> chunks
        </span>

        {total_pages !== undefined && total_pages !== null && (
          <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            &bull; <strong style={{ color: 'var(--color-text-primary)' }}>{total_pages}</strong> pages
          </span>
        )}

        {file_size_bytes && (
          <span style={{ color: 'var(--color-text-muted)' }}>
            &bull; {formatSize(file_size_bytes)}
          </span>
        )}

        <span
          style={{
            marginLeft: 'auto',
            fontSize: '10px',
            fontWeight: 600,
            padding: '1px 6px',
            borderRadius: '4px',
            background: 'rgba(16, 185, 129, 0.12)',
            color: '#10b981',
            border: '1px solid rgba(16, 185, 129, 0.25)',
          }}
        >
          Indexed
        </span>
      </div>
    </div>
  )
}
