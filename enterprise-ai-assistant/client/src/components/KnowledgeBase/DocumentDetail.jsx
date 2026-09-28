/**
 * DocumentDetail.jsx
 * ------------------
 * Shows the full details of a selected document — including all its chunks.
 *
 * WHY SHOW CHUNKS?
 * This is a learning project. You need to SEE what the chunking produced.
 * In a production system you might hide this, but for an FDE demo it's
 * essential to verify: "Did the text extract correctly? Are the chunks
 * a sensible size? Do they contain meaningful content?"
 *
 * Props:
 *   documentId   — the ID of the document to load (triggers a fetch)
 *   onClose      — called when the user closes the detail panel
 */

import { useState, useEffect } from 'react'
import { getDocument } from '../../services/api'

function DocumentDetail({ documentId, onClose }) {
  const [doc, setDoc] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)
  const [expandedChunk, setExpandedChunk] = useState(null)

  // Load document details whenever the selected documentId changes
  useEffect(() => {
    if (!documentId) return

    setIsLoading(true)
    setError(null)
    setDoc(null)
    setExpandedChunk(null)

    getDocument(documentId)
      .then(setDoc)
      .catch((err) => setError(err.message))
      .finally(() => setIsLoading(false))
  }, [documentId])

  if (!documentId) return null

  return (
    <div style={{
      width: 400,
      flexShrink: 0,
      borderLeft: '1px solid var(--color-border)',
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      background: 'var(--color-bg-surface)',
    }}>
      {/* ── Panel header ── */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '14px 18px',
        borderBottom: '1px solid var(--color-border)',
        flexShrink: 0,
      }}>
        <div style={{
          fontSize: 11,
          fontWeight: 600,
          color: 'var(--color-text-muted)',
          textTransform: 'uppercase',
          letterSpacing: '0.08em',
        }}>
          Document Detail
        </div>
        <button
          id="close-detail-btn"
          onClick={onClose}
          style={{
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            color: 'var(--color-text-muted)',
            fontSize: 16,
            padding: '2px 6px',
            borderRadius: 4,
            fontFamily: 'inherit',
          }}
        >
          ✕
        </button>
      </div>

      {/* ── Content area ── */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '18px' }}>
        {isLoading && (
          <div style={{ color: 'var(--color-text-muted)', fontSize: 13, paddingTop: 12 }}>
            Loading...
          </div>
        )}

        {error && (
          <div style={{ color: 'var(--color-error)', fontSize: 13, paddingTop: 12 }}>
            Failed to load: {error}
          </div>
        )}

        {doc && (
          <>
            {/* ── Metadata section ── */}
            <section style={{ marginBottom: 24 }}>
              <div style={{
                fontSize: 14,
                fontWeight: 600,
                color: 'var(--color-text-primary)',
                marginBottom: 12,
                wordBreak: 'break-all',
              }}>
                {doc.filename}
              </div>

              <MetaGrid rows={[
                ['Document ID', doc.document_id],
                ['Domain',      doc.domain || 'General'],
                ['File type',   doc.file_type.toUpperCase()],
                ['Chunks',      doc.chunk_count],
                ['Status',      doc.status === 'indexed' ? 'Indexed in Vector DB' : doc.status],
                ['Uploaded',    formatDate(doc.uploaded_at)],
                ['Indexed at',  formatDate(doc.indexed_at)],
              ]} />

              {/* Phase 3 Pipeline Checklist */}
              <div
                style={{
                  marginTop: '16px',
                  padding: '12px 14px',
                  background: 'var(--color-bg-base)',
                  border: '1px solid var(--color-border)',
                  borderRadius: '6px',
                }}
              >
                <div style={{ fontSize: '10px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--color-text-muted)', marginBottom: '8px' }}>
                  Ingestion &amp; Vector Pipeline
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', fontSize: '12px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#10b981' }}>
                    <span>✓</span> <span>Uploaded source file</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#10b981' }}>
                    <span>✓</span> <span>Text extracted &amp; cleaned</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#10b981' }}>
                    <span>✓</span> <span>{doc.chunk_count} Chunks generated (800c / 100o)</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: doc.status === 'indexed' ? '#10b981' : 'var(--color-text-muted)' }}>
                    <span>{doc.status === 'indexed' ? '✓' : '○'}</span> <span>Embedded (384-d local vectors)</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: doc.status === 'indexed' ? '#10b981' : 'var(--color-text-muted)' }}>
                    <span>{doc.status === 'indexed' ? '✓' : '○'}</span> <span>Indexed in ChromaDB</span>
                  </div>
                </div>
              </div>
            </section>

            {/* ── Divider ── */}
            <div style={{ height: 1, background: 'var(--color-border)', marginBottom: 20 }} />

            {/* ── Chunks section ── */}
            <section>
              <div style={{
                fontSize: 11,
                fontWeight: 600,
                color: 'var(--color-text-muted)',
                textTransform: 'uppercase',
                letterSpacing: '0.08em',
                marginBottom: 12,
              }}>
                Chunks ({doc.chunks?.length ?? 0})
              </div>

              <p style={{
                fontSize: 11,
                color: 'var(--color-text-muted)',
                lineHeight: 1.6,
                marginBottom: 14,
              }}>
                Each chunk is a segment of the document text. In Phase 3,
                these chunks will be converted to embeddings and stored in
                a vector database for similarity search.
              </p>

              {doc.chunks?.length === 0 && (
                <div style={{ color: 'var(--color-text-muted)', fontSize: 12 }}>
                  No chunks found.
                </div>
              )}

              <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                {doc.chunks?.map((chunk, i) => (
                  <ChunkCard
                    key={chunk.id}
                    chunk={chunk}
                    index={i}
                    isExpanded={expandedChunk === chunk.id}
                    onToggle={() => setExpandedChunk(
                      expandedChunk === chunk.id ? null : chunk.id
                    )}
                  />
                ))}
              </div>
            </section>
          </>
        )}
      </div>
    </div>
  )
}

// ── ChunkCard ──────────────────────────────────────────────────────────────────
function ChunkCard({ chunk, index, isExpanded, onToggle }) {
  const preview = chunk.text.slice(0, 120).replace(/\n/g, ' ')
  const hasMore = chunk.text.length > 120

  return (
    <div
      id={`chunk-card-${chunk.id}`}
      style={{
        border: '1px solid var(--color-border)',
        borderRadius: 5,
        overflow: 'hidden',
        transition: 'border-color 0.12s',
      }}
    >
      {/* Chunk header */}
      <button
        onClick={onToggle}
        style={{
          width: '100%',
          background: isExpanded ? 'var(--color-accent-muted)' : 'var(--color-bg-elevated)',
          border: 'none',
          padding: '9px 12px',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          gap: 8,
          textAlign: 'left',
          fontFamily: 'inherit',
          transition: 'background 0.12s',
        }}
      >
        <span style={{
          fontSize: 9,
          fontWeight: 700,
          color: 'var(--color-accent)',
          fontFamily: 'monospace',
          flexShrink: 0,
        }}>
          {String(index + 1).padStart(3, '0')}
        </span>
        <span style={{
          fontSize: 11,
          color: isExpanded ? 'var(--color-accent-hover)' : 'var(--color-text-secondary)',
          fontFamily: 'monospace',
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          whiteSpace: 'nowrap',
          flex: 1,
        }}>
          {chunk.id}
        </span>
        <span style={{
          fontSize: 10,
          color: 'var(--color-text-muted)',
          flexShrink: 0,
        }}>
          {chunk.text.length} chars
        </span>
        <span style={{
          fontSize: 10,
          color: 'var(--color-text-muted)',
          flexShrink: 0,
          transition: 'transform 0.15s',
          transform: isExpanded ? 'rotate(90deg)' : 'none',
        }}>
          ›
        </span>
      </button>

      {/* Chunk body — only shown when expanded */}
      {isExpanded && (
        <div style={{
          padding: '10px 12px',
          background: 'var(--color-bg-surface)',
          borderTop: '1px solid var(--color-border)',
        }}>
          <pre style={{
            fontSize: 11,
            color: 'var(--color-text-secondary)',
            lineHeight: 1.65,
            whiteSpace: 'pre-wrap',
            wordBreak: 'break-word',
            fontFamily: 'monospace',
            margin: 0,
          }}>
            {chunk.text}
          </pre>
        </div>
      )}
    </div>
  )
}

// ── MetaGrid ───────────────────────────────────────────────────────────────────
function MetaGrid({ rows }) {
  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: 'auto 1fr',
      gap: '6px 12px',
      fontSize: 12,
    }}>
      {rows.map(([label, value]) => (
        <>
          <div key={label + '-label'} style={{ color: 'var(--color-text-muted)', whiteSpace: 'nowrap' }}>
            {label}
          </div>
          <div key={label + '-value'} style={{
            color: 'var(--color-text-primary)',
            fontFamily: label === 'Document ID' ? 'monospace' : 'inherit',
            fontSize: label === 'Document ID' ? 10 : 12,
            wordBreak: 'break-all',
          }}>
            {String(value)}
          </div>
        </>
      ))}
    </div>
  )
}

function formatDate(isoString) {
  if (!isoString) return '—'
  try {
    return new Date(isoString).toLocaleString()
  } catch {
    return '—'
  }
}

export default DocumentDetail
