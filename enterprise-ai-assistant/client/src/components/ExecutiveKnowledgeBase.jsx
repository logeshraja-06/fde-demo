import React, { useState, useEffect, useCallback } from 'react'
import { getDocuments, uploadDocument, deleteDocument } from '../services/api'

export default function ExecutiveKnowledgeBase({ onBackToChat = () => {} }) {
  const [documents, setDocuments] = useState([])
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [selectedDomain, setSelectedDomain] = useState('HR')
  const [selectedDoc, setSelectedDoc] = useState(null)
  const [statusMessage, setStatusMessage] = useState(null)

  const loadDocuments = useCallback(async () => {
    setLoading(true)
    try {
      const data = await getDocuments()
      const sorted = [...(data.documents || [])].sort(
        (a, b) => new Date(b.uploaded_at) - new Date(a.uploaded_at)
      )
      setDocuments(sorted)
    } catch (err) {
      console.warn('Could not load documents:', err)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadDocuments()
  }, [loadDocuments])

  const handleFileUpload = async (file) => {
    if (!file) return
    setUploading(true)
    setStatusMessage({ type: 'info', text: `Indexing ${file.name}...` })
    try {
      const result = await uploadDocument(file, selectedDomain)
      setStatusMessage({ type: 'success', text: `Successfully indexed ${file.name} into ${selectedDomain} domain.` })
      await loadDocuments()
      if (result) setSelectedDoc(result)
    } catch (err) {
      setStatusMessage({ type: 'error', text: err.message || 'Upload failed' })
    } finally {
      setUploading(false)
    }
  }

  const handleDelete = async (docId, e) => {
    e.stopPropagation()
    try {
      await deleteDocument(docId)
      setDocuments((prev) => prev.filter((d) => d.document_id !== docId))
      if (selectedDoc?.document_id === docId) setSelectedDoc(null)
      setStatusMessage({ type: 'info', text: 'Document removed from knowledge base.' })
    } catch (err) {
      setStatusMessage({ type: 'error', text: err.message })
    }
  }

  return (
    <div
      style={{
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        overflowY: 'auto',
        padding: '24px 36px',
        position: 'relative',
        zIndex: 1,
      }}
    >
      {/* ── Top Header Bar ── */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: '24px',
          maxWidth: '1000px',
          width: '100%',
          margin: '0 auto 24px auto',
        }}
      >
        <div>
          <h2 style={{ fontSize: '20px', fontWeight: 700, color: 'var(--text-primary)' }}>
            TruthGuard Knowledge Base
          </h2>
          <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '2px' }}>
            Verified policy documents indexed for AI grounding and truth verification.
          </p>
        </div>

        <button
          onClick={onBackToChat}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            backgroundColor: 'var(--pill-bg)',
            border: '1px solid var(--border-subtle)',
            borderRadius: '9999px',
            padding: '7px 16px',
            color: 'var(--text-primary)',
            fontSize: '12.5px',
            fontWeight: 500,
          }}
          onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = 'var(--pill-hover)')}
          onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'var(--pill-bg)')}
        >
          <span>← Back to Chat</span>
        </button>
      </div>

      {/* Status banner */}
      {statusMessage && (
        <div
          style={{
            maxWidth: '1000px',
            width: '100%',
            margin: '0 auto 16px auto',
            padding: '10px 16px',
            borderRadius: '10px',
            fontSize: '12.5px',
            backgroundColor: statusMessage.type === 'error' ? 'rgba(239, 68, 68, 0.12)' : 'rgba(16, 185, 129, 0.12)',
            color: statusMessage.type === 'error' ? '#f87171' : '#10b981',
            border: `1px solid ${statusMessage.type === 'error' ? 'rgba(239, 68, 68, 0.25)' : 'rgba(16, 185, 129, 0.25)'}`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <span>{statusMessage.text}</span>
          <span style={{ cursor: 'pointer', fontWeight: 700 }} onClick={() => setStatusMessage(null)}>✕</span>
        </div>
      )}

      {/* ── Content Grid: Upload Zone + Documents List ── */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: selectedDoc ? '1fr 340px' : '1fr',
          gap: '24px',
          maxWidth: '1000px',
          width: '100%',
          margin: '0 auto',
        }}
      >
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {/* Upload Card */}
          <div
            style={{
              backgroundColor: 'var(--card-bg)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '16px',
              padding: '22px',
              display: 'flex',
              flexDirection: 'column',
              gap: '14px',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text-primary)' }}>
                Index New Policy Document
              </span>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Target Domain:</span>
                <select
                  value={selectedDomain}
                  onChange={(e) => setSelectedDomain(e.target.value)}
                  style={{
                    backgroundColor: 'var(--pill-bg)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: '6px',
                    color: 'var(--text-primary)',
                    padding: '3px 8px',
                    fontSize: '12px',
                    outline: 'none',
                    cursor: 'pointer',
                  }}
                >
                  <option value="HR">HR Domain</option>
                  <option value="Finance">Finance Domain</option>
                  <option value="IT">IT Domain</option>
                </select>
              </div>
            </div>

            {/* Dropzone */}
            <div
              onClick={() => {
                const el = document.createElement('input')
                el.type = 'file'
                el.accept = '.pdf,.txt,.md,.docx'
                el.onchange = (e) => handleFileUpload(e.target.files?.[0])
                el.click()
              }}
              style={{
                border: '1.5px dashed var(--border-highlight)',
                borderRadius: '12px',
                padding: '24px',
                textAlign: 'center',
                cursor: uploading ? 'wait' : 'pointer',
                backgroundColor: 'var(--pill-bg)',
                transition: 'border-color 0.15s ease',
              }}
              onMouseEnter={(e) => (e.currentTarget.style.borderColor = '#ea580c')}
              onMouseLeave={(e) => (e.currentTarget.style.borderColor = 'var(--border-highlight)')}
            >
              <div style={{ fontSize: '24px', marginBottom: '6px' }}>📄</div>
              <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-primary)' }}>
                {uploading ? 'Processing & Embedding Document...' : 'Click or Drag files here to index'}
              </div>
              <div style={{ fontSize: '11.5px', color: 'var(--text-muted)', marginTop: '4px' }}>
                Supports PDF, DOCX, TXT, Markdown • Automatically chunked and vector embedded
              </div>
            </div>
          </div>

          {/* Document List */}
          <div
            style={{
              backgroundColor: 'var(--card-bg)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '16px',
              padding: '20px',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
              <span style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text-primary)' }}>
                Indexed Corporate Files ({documents.length})
              </span>
              <button
                onClick={loadDocuments}
                title="Refresh list"
                style={{ fontSize: '12px', color: 'var(--text-muted)' }}
              >
                🔄 Refresh
              </button>
            </div>

            {loading ? (
              <div style={{ padding: '30px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '13px' }}>
                Loading knowledge documents...
              </div>
            ) : documents.length === 0 ? (
              <div style={{ padding: '30px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '13px' }}>
                No documents uploaded yet. Upload a company policy to ground the AI assistant.
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {documents.map((doc) => {
                  const isSelected = selectedDoc?.document_id === doc.document_id
                  return (
                    <div
                      key={doc.document_id}
                      onClick={() => setSelectedDoc(doc)}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        padding: '12px 14px',
                        borderRadius: '10px',
                        backgroundColor: isSelected ? 'var(--pill-active)' : 'var(--pill-bg)',
                        border: `1px solid ${isSelected ? 'var(--border-highlight)' : 'transparent'}`,
                        cursor: 'pointer',
                        transition: 'all 0.15s ease',
                      }}
                      onMouseEnter={(e) => {
                        if (!isSelected) e.currentTarget.style.backgroundColor = 'var(--pill-hover)'
                      }}
                      onMouseLeave={(e) => {
                        if (!isSelected) e.currentTarget.style.backgroundColor = 'var(--pill-bg)'
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <span style={{ fontSize: '18px' }}>📄</span>
                        <div>
                          <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-primary)' }}>
                            {doc.filename}
                          </div>
                          <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '2px' }}>
                            {doc.domain || 'General'} • {doc.chunk_count || doc.chunks?.length || 0} chunks • {doc.uploaded_at ? new Date(doc.uploaded_at).toLocaleDateString() : 'Active'}
                          </div>
                        </div>
                      </div>

                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <span
                          style={{
                            fontSize: '10px',
                            fontWeight: 700,
                            padding: '2px 8px',
                            borderRadius: '9999px',
                            backgroundColor: doc.domain === 'Finance' ? 'rgba(234, 88, 12, 0.15)' : doc.domain === 'IT' ? 'rgba(59, 130, 246, 0.15)' : 'rgba(16, 185, 129, 0.15)',
                            color: doc.domain === 'Finance' ? '#f97316' : doc.domain === 'IT' ? '#60a5fa' : '#10b981',
                          }}
                        >
                          {doc.domain || 'Policy'}
                        </span>
                        <button
                          onClick={(e) => handleDelete(doc.document_id, e)}
                          title="Delete Document"
                          style={{
                            color: 'var(--text-muted)',
                            padding: '4px',
                            borderRadius: '4px',
                          }}
                          onMouseEnter={(e) => (e.currentTarget.style.color = '#f87171')}
                          onMouseLeave={(e) => (e.currentTarget.style.color = 'var(--text-muted)')}
                        >
                          🗑️
                        </button>
                      </div>
                    </div>
                  )
                })}
              </div>
            )}
          </div>
        </div>

        {/* Selected Document Detail Drawer */}
        {selectedDoc && (
          <div
            style={{
              backgroundColor: 'var(--card-bg)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '16px',
              padding: '20px',
              display: 'flex',
              flexDirection: 'column',
              gap: '14px',
              height: 'fit-content',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-primary)' }}>
                Document Details
              </span>
              <button
                onClick={() => setSelectedDoc(null)}
                style={{ fontSize: '12px', color: 'var(--text-muted)' }}
              >
                ✕
              </button>
            </div>

            <div>
              <div style={{ fontSize: '14px', fontWeight: 700, color: 'var(--text-primary)' }}>
                {selectedDoc.filename}
              </div>
              <div style={{ fontSize: '11.5px', color: 'var(--text-muted)', marginTop: '4px' }}>
                ID: {selectedDoc.document_id}
              </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '12px', color: 'var(--text-secondary)' }}>
              <div><strong>Domain:</strong> {selectedDoc.domain}</div>
              <div><strong>Indexed Chunks:</strong> {selectedDoc.chunk_count || selectedDoc.chunks?.length || 0}</div>
              <div><strong>Status:</strong> <span style={{ color: '#10b981' }}>✓ Embedded in Vector Store</span></div>
            </div>

            <button
              onClick={() => onBackToChat()}
              style={{
                marginTop: '10px',
                backgroundColor: '#ea580c',
                color: '#ffffff',
                borderRadius: '8px',
                padding: '8px 14px',
                fontSize: '12.5px',
                fontWeight: 600,
                textAlign: 'center',
              }}
            >
              Ask AI About This File →
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
