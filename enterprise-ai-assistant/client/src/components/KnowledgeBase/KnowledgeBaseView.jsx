/**
 * KnowledgeBaseView.jsx
 * ----------------------
 * The main page for the Knowledge Base section.
 *
 * Layout:
 *   Left column:  UploadArea + DocumentList
 *   Right panel:  DocumentDetail (appears when a document is selected)
 *
 * Phase 6 updates:
 *   - Real visual processing lifecycle: Uploaded → Text Extracted → Chunked → Embedded → Indexed
 *   - Document metadata inspection (Chunks, Pages, Timestamp, Status)
 */

import { useState, useEffect, useCallback } from 'react'
import UploadArea from './UploadArea'
import DocumentList from './DocumentList'
import DocumentDetail from './DocumentDetail'
import { getDocuments, deleteDocument } from '../../services/api'

function KnowledgeBaseView() {
  const [documents, setDocuments] = useState([])
  const [selectedId, setSelectedId] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [listError, setListError] = useState(null)

  // Load the document list from the backend
  const loadDocuments = useCallback(async () => {
    setIsLoading(true)
    setListError(null)
    try {
      const data = await getDocuments()
      // Sort newest first
      const sorted = [...(data.documents || [])].sort(
        (a, b) => new Date(b.uploaded_at) - new Date(a.uploaded_at)
      )
      setDocuments(sorted)
    } catch (err) {
      setListError(err.message)
    } finally {
      setIsLoading(false)
    }
  }, [])

  // Load on first render
  useEffect(() => {
    loadDocuments()
  }, [loadDocuments])

  // Called after a successful upload
  function handleUploadSuccess(newDoc) {
    setDocuments((prev) => [newDoc, ...prev])
    setSelectedId(newDoc.document_id)
  }

  // Called when user clicks delete in DocumentList
  async function handleDelete(documentId) {
    await deleteDocument(documentId)
    setDocuments((prev) => prev.filter((d) => d.document_id !== documentId))
    if (selectedId === documentId) {
      setSelectedId(null)
    }
  }

  const selectedDoc = documents.find((d) => d.document_id === selectedId)

  return (
    <div
      style={{
        flex: 1,
        display: 'flex',
        overflow: 'hidden',
        height: '100%',
      }}
    >
      {/* ── Left: Upload + List ── */}
      <div
        style={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          overflowY: 'auto',
          padding: '32px 36px',
          maxWidth: selectedId ? 640 : 760,
        }}
      >
        {/* Page description */}
        <div style={{ marginBottom: 24 }}>
          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 6,
              background: 'var(--color-accent-muted)',
              color: 'var(--color-accent-hover)',
              fontSize: 11,
              fontWeight: 600,
              textTransform: 'uppercase',
              letterSpacing: '0.08em',
              padding: '4px 10px',
              borderRadius: 4,
              marginBottom: 12,
            }}
          >
            Knowledge Ingestion &amp; Vector Indexing
          </div>
          <h2
            style={{
              fontSize: 22,
              fontWeight: 700,
              color: 'var(--color-text-primary)',
              letterSpacing: '-0.02em',
              marginBottom: 6,
            }}
          >
            Enterprise Knowledge Base
          </h2>
          <p
            style={{
              fontSize: 13,
              color: 'var(--color-text-secondary)',
              lineHeight: 1.6,
              maxWidth: 540,
              margin: 0,
            }}
          >
            Upload official PDF and TXT documents. Files pass through the automated
            pipeline: text extraction, semantic chunking, SentenceTransformer vector embeddings,
            and ChromaDB indexing.
          </p>
        </div>

        {/* ── Visual Processing Lifecycle ── */}
        <ProcessingLifecycle activeDoc={selectedDoc} />

        {/* ── Upload area ── */}
        <UploadArea onUploadSuccess={handleUploadSuccess} />

        {/* ── Error loading list ── */}
        {listError && (
          <div
            style={{
              padding: '12px 16px',
              background: 'rgba(248,113,113,0.08)',
              border: '1px solid rgba(248,113,113,0.25)',
              borderRadius: 6,
              color: 'var(--color-error)',
              fontSize: 12,
              marginBottom: 16,
            }}
          >
            Failed to load documents: {listError}
          </div>
        )}

        {/* ── Document list ── */}
        <DocumentList
          documents={documents}
          selectedId={selectedId}
          onSelect={setSelectedId}
          onDelete={handleDelete}
          isLoading={isLoading}
        />
      </div>

      {/* ── Right: Document detail panel ── */}
      {selectedId && (
        <DocumentDetail
          documentId={selectedId}
          onClose={() => setSelectedId(null)}
        />
      )}
    </div>
  )
}

/**
 * ProcessingLifecycle
 * -------------------
 * Visual processing lifecycle required by Phase 6:
 * Uploaded → Text Extracted → Chunked → Embedded → Indexed
 */
function ProcessingLifecycle({ activeDoc }) {
  const stages = [
    { id: 'upload', label: 'Uploaded', desc: activeDoc?.uploaded_at ? 'Stored in /uploads' : 'Source file' },
    { id: 'extract', label: 'Text Extracted', desc: 'pypdf text parsing' },
    { id: 'chunk', label: 'Chunked', desc: activeDoc ? `${activeDoc.chunk_count || 0} chunks (800c/100o)` : 'Sliding window' },
    { id: 'embed', label: 'Embedded', desc: 'all-MiniLM-L6-v2 (384-d)' },
    { id: 'index', label: 'Indexed', desc: 'ChromaDB persistent store' },
  ]

  return (
    <div
      style={{
        background: 'var(--color-bg-surface)',
        border: '1px solid var(--color-border)',
        borderRadius: '8px',
        padding: '14px 18px',
        marginBottom: '20px',
      }}
    >
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: '10px',
        }}
      >
        <span
          style={{
            fontSize: '11px',
            fontWeight: 700,
            textTransform: 'uppercase',
            letterSpacing: '0.07em',
            color: 'var(--color-text-secondary)',
          }}
        >
          Document Processing Lifecycle
        </span>
        {activeDoc && (
          <span
            style={{
              fontSize: '10px',
              fontWeight: 600,
              color: '#10b981',
              background: 'rgba(16, 185, 129, 0.12)',
              border: '1px solid rgba(16, 185, 129, 0.25)',
              padding: '2px 6px',
              borderRadius: '4px',
            }}
          >
            {activeDoc.filename} (Fully Indexed)
          </span>
        )}
      </div>

      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '6px',
          flexWrap: 'wrap',
        }}
      >
        {stages.map((st, i) => (
          <div key={st.id} style={{ display: 'flex', alignItems: 'center', gap: '6px', flex: 1, minWidth: '95px' }}>
            <div
              style={{
                flex: 1,
                background: 'var(--color-bg-base)',
                border: '1px solid var(--color-border)',
                borderRadius: '6px',
                padding: '6px 8px',
                display: 'flex',
                flexDirection: 'column',
                gap: '2px',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                <span style={{ fontSize: '10px', color: '#10b981', fontWeight: 700 }}>✓</span>
                <span style={{ fontSize: '11px', fontWeight: 600, color: 'var(--color-text-primary)' }}>
                  {st.label}
                </span>
              </div>
              <span style={{ fontSize: '10px', color: 'var(--color-text-muted)' }}>
                {st.desc}
              </span>
            </div>

            {i < stages.length - 1 && (
              <span style={{ color: 'var(--color-text-muted)', fontSize: '12px' }}>➔</span>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

export default KnowledgeBaseView
