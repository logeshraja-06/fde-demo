import React, { useState, useEffect } from 'react'
import { searchKnowledgeBase, getRagStats } from '../../services/api'

// Preset test questions to help learners test the RAG retrieval pipeline easily
const PRESET_QUERIES = [
  {
    label: 'Casual Leaves',
    query: 'How many casual leaves do employees get per year?',
    category: 'HR Policy',
    expected: 'Should match leave-policy chunks with high similarity (~0.85+)',
  },
  {
    label: 'Internet Expense',
    query: 'What is the monthly internet reimbursement limit for remote work?',
    category: 'Expense Policy',
    expected: 'Should match expense-policy chunks with high similarity',
  },
  {
    label: 'Password Security',
    query: 'What are the password complexity and expiration requirements?',
    category: 'IT Guidelines',
    expected: 'Should match IT security guidelines with high similarity',
  },
  {
    label: 'Chocolate Cake (Irrelevant)',
    query: 'What is the recipe for baking a chocolate cake?',
    category: 'Negative Test',
    expected: 'Should trigger relevance threshold rejection (0 matches)',
  },
]

export default function RetrievalPlayground() {
  const [query, setQuery] = useState('')
  const [topK, setTopK] = useState(3)
  const [threshold, setThreshold] = useState(0.35)
  const [domain, setDomain] = useState('ALL')
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState(null)
  const [error, setError] = useState(null)
  const [stats, setStats] = useState(null)
  const [copiedId, setCopiedId] = useState(null)

  // Load vector store & embedding model stats on mount
  useEffect(() => {
    async function loadStats() {
      try {
        const data = await getRagStats()
        setStats(data)
      } catch (err) {
        console.warn('Could not load RAG stats:', err)
      }
    }
    loadStats()
  }, [])

  const handleSearch = async (searchQuery = query) => {
    const q = (searchQuery || '').trim()
    if (!q) return

    setLoading(true)
    setError(null)
    setResults(null)

    try {
      const response = await searchKnowledgeBase(q, topK, threshold, domain)
      setResults(response)
    } catch (err) {
      setError(err.message || 'Failed to search vector store.')
    } finally {
      setLoading(false)
    }
  }

  const handlePresetClick = (presetQuery) => {
    setQuery(presetQuery)
    handleSearch(presetQuery)
  }

  const handleCopyText = (chunkId, text) => {
    navigator.clipboard.writeText(text)
    setCopiedId(chunkId)
    setTimeout(() => setCopiedId(null), 2000)
  }

  // Get score color styling based on cosine similarity
  const getScoreBadge = (score) => {
    const pct = Math.round(score * 100)
    if (score >= 0.75) {
      return {
        bg: 'rgba(16, 185, 129, 0.12)',
        border: 'rgba(16, 185, 129, 0.3)',
        text: '#10b981',
        label: `High Match (${pct}%)`,
      }
    } else if (score >= 0.50) {
      return {
        bg: 'rgba(59, 130, 246, 0.12)',
        border: 'rgba(59, 130, 246, 0.3)',
        text: '#60a5fa',
        label: `Moderate Match (${pct}%)`,
      }
    } else {
      return {
        bg: 'rgba(245, 158, 11, 0.12)',
        border: 'rgba(245, 158, 11, 0.3)',
        text: '#fbbf24',
        label: `Borderline Match (${pct}%)`,
      }
    }
  }

  return (
    <div style={{ padding: '32px', maxWidth: '1200px', margin: '0 auto' }}>
      {/* ── Page Header ── */}
      <div style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
          <span style={{ fontSize: '24px' }}>⚡</span>
          <h1 style={{ margin: 0, fontSize: '24px', fontWeight: 700, color: 'var(--color-text-primary)' }}>
            RAG Retrieval Playground
          </h1>
          <span
            style={{
              fontSize: '11px',
              fontWeight: 700,
              padding: '3px 8px',
              borderRadius: '9999px',
              background: 'rgba(99, 102, 241, 0.15)',
              color: '#818cf8',
              border: '1px solid rgba(99, 102, 241, 0.3)',
              letterSpacing: '0.05em',
            }}
          >
            PHASE 3 ACTIVE
          </span>
        </div>
        <p style={{ margin: 0, fontSize: '14px', color: 'var(--color-text-secondary)', lineHeight: 1.5 }}>
          Test semantic search across your ingested company documents. The engine embeds your question in real-time,
          queries ChromaDB, and returns the top-ranking text chunks.
        </p>
      </div>

      {/* ── Phase 3 Learning & Boundary Banner ── */}
      <div
        style={{
          background: 'rgba(30, 41, 59, 0.6)',
          border: '1px solid rgba(99, 102, 241, 0.25)',
          borderRadius: '10px',
          padding: '16px 20px',
          marginBottom: '24px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '16px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div
            style={{
              width: '36px',
              height: '36px',
              borderRadius: '8px',
              background: 'rgba(99, 102, 241, 0.15)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#818cf8',
              fontSize: '18px',
              flexShrink: 0,
            }}
          >
            ℹ️
          </div>
          <div>
            <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--color-text-primary)' }}>
              Retrieval Inspection Mode
            </div>
            <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', marginTop: '2px' }}>
              These are retrieved knowledge-base chunks and vector similarity scores. The generative LLM response
              will be connected in <strong>Phase 4</strong>.
            </div>
          </div>
        </div>

        {stats && (
          <div
            style={{
              display: 'flex',
              gap: '16px',
              fontSize: '12px',
              color: 'var(--color-text-secondary)',
              borderLeft: '1px solid var(--color-border)',
              paddingLeft: '16px',
              flexShrink: 0,
            }}
          >
            <div>
              <span style={{ color: 'var(--color-text-muted)' }}>Embedding: </span>
              <strong style={{ color: '#818cf8' }}>{stats.embedding_model?.model_name || 'all-MiniLM-L6-v2'}</strong>
            </div>
            <div>
              <span style={{ color: 'var(--color-text-muted)' }}>Vectors in DB: </span>
              <strong style={{ color: '#10b981' }}>{stats.vector_store?.total_chunks_indexed || 0}</strong>
            </div>
          </div>
        )}
      </div>

      {/* ── Search Controls Panel ── */}
      <div
        style={{
          background: 'var(--color-bg-surface)',
          border: '1px solid var(--color-border)',
          borderRadius: '12px',
          padding: '24px',
          marginBottom: '24px',
          boxShadow: '0 4px 20px rgba(0, 0, 0, 0.25)',
        }}
      >
        <form
          onSubmit={(e) => {
            e.preventDefault()
            handleSearch()
          }}
        >
          {/* Main Query Input Bar */}
          <div style={{ display: 'flex', gap: '12px', marginBottom: '16px' }}>
            <div style={{ position: 'relative', flex: 1 }}>
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask a question about leave policies, IT security, expenses..."
                style={{
                  width: '100%',
                  padding: '14px 18px',
                  paddingRight: query ? '40px' : '18px',
                  background: 'var(--color-bg-base)',
                  border: '1px solid var(--color-border)',
                  borderRadius: '8px',
                  color: 'var(--color-text-primary)',
                  fontSize: '15px',
                  outline: 'none',
                  transition: 'border-color 0.2s',
                  boxSizing: 'border-box',
                }}
                onFocus={(e) => (e.target.style.borderColor = 'var(--color-brand)')}
                onBlur={(e) => (e.target.style.borderColor = 'var(--color-border)')}
              />
              {query && (
                <button
                  type="button"
                  onClick={() => setQuery('')}
                  style={{
                    position: 'absolute',
                    right: '12px',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    background: 'none',
                    border: 'none',
                    color: 'var(--color-text-muted)',
                    cursor: 'pointer',
                    fontSize: '16px',
                  }}
                  title="Clear input"
                >
                  ✕
                </button>
              )}
            </div>

            <button
              type="submit"
              disabled={loading || !query.trim()}
              style={{
                padding: '0 28px',
                background: loading || !query.trim() ? 'rgba(99, 102, 241, 0.4)' : 'var(--color-brand)',
                color: '#fff',
                border: 'none',
                borderRadius: '8px',
                fontSize: '14px',
                fontWeight: 600,
                cursor: loading || !query.trim() ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                transition: 'background 0.2s',
                whiteSpace: 'nowrap',
              }}
            >
              {loading ? (
                <>
                  <span className="spinner" style={{ width: '14px', height: '14px', border: '2px solid rgba(255,255,255,0.3)', borderTopColor: '#fff', borderRadius: '50%', display: 'inline-block', animation: 'spin 0.8s linear infinite' }} />
                  Retrieving...
                </>
              ) : (
                <>
                  <span>🔍</span> Search Chunks
                </>
              )}
            </button>
          </div>

          {/* Controls: Top-K & Threshold */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              flexWrap: 'wrap',
              gap: '16px',
              paddingTop: '12px',
              borderTop: '1px solid var(--color-border)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
              {/* Top-K Selector */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px' }}>
                <label style={{ color: 'var(--color-text-secondary)', fontWeight: 500 }}>Top-K Chunks:</label>
                <select
                  value={topK}
                  onChange={(e) => setTopK(Number(e.target.value))}
                  style={{
                    background: 'var(--color-bg-base)',
                    border: '1px solid var(--color-border)',
                    borderRadius: '6px',
                    color: 'var(--color-text-primary)',
                    padding: '4px 10px',
                    fontSize: '13px',
                    cursor: 'pointer',
                  }}
                >
                  <option value={1}>1 chunk</option>
                  <option value={2}>2 chunks</option>
                  <option value={3}>3 chunks (Default)</option>
                  <option value={5}>5 chunks</option>
                  <option value={8}>8 chunks</option>
                </select>
              </div>

              {/* Threshold Selector */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px' }}>
                <label style={{ color: 'var(--color-text-secondary)', fontWeight: 500 }}>Relevance Threshold:</label>
                <select
                  value={threshold}
                  onChange={(e) => setThreshold(Number(e.target.value))}
                  style={{
                    background: 'var(--color-bg-base)',
                    border: '1px solid var(--color-border)',
                    borderRadius: '6px',
                    color: 'var(--color-text-primary)',
                    padding: '4px 10px',
                    fontSize: '13px',
                    cursor: 'pointer',
                  }}
                >
                  <option value={0.20}>0.20 (Permissive)</option>
                  <option value={0.35}>0.35 (Standard Default)</option>
                  <option value={0.50}>0.50 (Strict)</option>
                  <option value={0.65}>0.65 (Very High Precision)</option>
                </select>
              </div>

              {/* Domain Filter Selector (Phase 8 Requirement) */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px' }}>
                <label style={{ color: 'var(--color-text-secondary)', fontWeight: 500 }}>Domain:</label>
                <select
                  id="domain-filter-select"
                  value={domain}
                  onChange={(e) => setDomain(e.target.value)}
                  style={{
                    background: 'var(--color-bg-base)',
                    border: '1px solid var(--color-brand)',
                    borderRadius: '6px',
                    color: 'var(--color-brand)',
                    fontWeight: 600,
                    padding: '4px 10px',
                    fontSize: '13px',
                    cursor: 'pointer',
                  }}
                >
                  <option value="ALL">All Domains</option>
                  <option value="HR">HR Only</option>
                  <option value="Finance">Finance Only</option>
                  <option value="IT">IT Only</option>
                </select>
              </div>
            </div>

            {/* Quick Helper Note */}
            <span style={{ fontSize: '12px', color: 'var(--color-text-muted)' }}>
              Uses Cosine Distance in ChromaDB collection
            </span>
          </div>
        </form>

        {/* ── Preset Query Chips ── */}
        <div style={{ marginTop: '20px' }}>
          <div style={{ fontSize: '12px', color: 'var(--color-text-muted)', marginBottom: '8px', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Quick Test Questions:
          </div>
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            {PRESET_QUERIES.map((item, idx) => (
              <button
                key={idx}
                onClick={() => handlePresetClick(item.query)}
                style={{
                  background: 'var(--color-bg-base)',
                  border: '1px solid var(--color-border)',
                  borderRadius: '6px',
                  padding: '6px 12px',
                  color: 'var(--color-text-secondary)',
                  fontSize: '12px',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  transition: 'all 0.15s ease',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.borderColor = 'var(--color-brand)'
                  e.currentTarget.style.color = 'var(--color-text-primary)'
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.borderColor = 'var(--color-border)'
                  e.currentTarget.style.color = 'var(--color-text-secondary)'
                }}
              >
                <span style={{ fontWeight: 600, color: '#818cf8' }}>{item.label}</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* ── Error Banner ── */}
      {error && (
        <div
          style={{
            background: 'rgba(239, 68, 68, 0.1)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            borderRadius: '8px',
            padding: '14px 18px',
            color: '#ef4444',
            fontSize: '14px',
            marginBottom: '24px',
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
          }}
        >
          <span>⚠️</span>
          <span>{error}</span>
        </div>
      )}

      {/* ── Results Container ── */}
      {results && (
        <div>
          {/* Results Summary Bar */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: '16px',
              paddingBottom: '12px',
              borderBottom: '1px solid var(--color-border)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <h2 style={{ margin: 0, fontSize: '16px', fontWeight: 600, color: 'var(--color-text-primary)' }}>
                Retrieved Chunks
              </h2>
              <span
                style={{
                  fontSize: '12px',
                  padding: '2px 8px',
                  borderRadius: '10px',
                  background: results.total_found > 0 ? 'rgba(16, 185, 129, 0.15)' : 'rgba(245, 158, 11, 0.15)',
                  color: results.total_found > 0 ? '#10b981' : '#fbbf24',
                  fontWeight: 600,
                }}
              >
                {results.total_found} matched
              </span>
            </div>

            <div style={{ fontSize: '13px', color: 'var(--color-text-secondary)' }}>
              Threshold: <strong style={{ color: 'var(--color-text-primary)' }}>{results.threshold}</strong> &bull; Top-K: <strong style={{ color: 'var(--color-text-primary)' }}>{results.top_k}</strong>
            </div>
          </div>

          {/* When results are empty (Threshold Rejection) */}
          {results.total_found === 0 ? (
            <div
              style={{
                background: 'var(--color-bg-surface)',
                border: '1px dashed var(--color-border)',
                borderRadius: '12px',
                padding: '48px 24px',
                textAlign: 'center',
              }}
            >
              <div style={{ fontSize: '32px', marginBottom: '12px' }}>🛡️</div>
              <h3 style={{ margin: '0 0 8px 0', fontSize: '16px', fontWeight: 600, color: 'var(--color-text-primary)' }}>
                No Relevant Information Found
              </h3>
              <p style={{ margin: '0 auto', maxWidth: '500px', fontSize: '13px', color: 'var(--color-text-secondary)', lineHeight: 1.6 }}>
                {results.message || 'No chunks in the knowledge base met the minimum relevance threshold for this query.'}
              </p>
              <div style={{ marginTop: '16px', fontSize: '12px', color: 'var(--color-text-muted)' }}>
                💡 <em>This threshold prevents hallucinations by refusing to send irrelevant context to the LLM.</em>
              </div>
            </div>
          ) : (
            /* List of Retrieved Chunks */
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {results.results.map((chunk, index) => {
                const scoreStyle = getScoreBadge(chunk.score)
                return (
                  <div
                    key={chunk.chunk_id || index}
                    style={{
                      background: 'var(--color-bg-surface)',
                      border: '1px solid var(--color-border)',
                      borderRadius: '10px',
                      overflow: 'hidden',
                      transition: 'border-color 0.2s',
                    }}
                  >
                    {/* Chunk Card Header */}
                    <div
                      style={{
                        padding: '12px 18px',
                        background: 'rgba(15, 23, 42, 0.6)',
                        borderBottom: '1px solid var(--color-border)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        flexWrap: 'wrap',
                        gap: '12px',
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        {/* Rank Badge */}
                        <span
                          style={{
                            fontSize: '12px',
                            fontWeight: 700,
                            padding: '2px 8px',
                            borderRadius: '4px',
                            background: 'var(--color-bg-base)',
                            color: 'var(--color-text-primary)',
                            border: '1px solid var(--color-border)',
                          }}
                        >
                          #{String(index + 1).padStart(2, '0')}
                        </span>

                        {/* Source Document */}
                        <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--color-text-primary)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                          📄 {chunk.source}
                        </span>

                        {/* Domain Tag */}
                        {chunk.domain && (
                          <span
                            style={{
                              fontSize: '11px',
                              fontWeight: 600,
                              color: chunk.domain === 'HR' ? '#818cf8' : chunk.domain === 'Finance' ? '#34d399' : chunk.domain === 'IT' ? '#fbbf24' : '#94a3b8',
                              background: chunk.domain === 'HR' ? 'rgba(99, 102, 241, 0.12)' : chunk.domain === 'Finance' ? 'rgba(16, 185, 129, 0.12)' : chunk.domain === 'IT' ? 'rgba(245, 158, 11, 0.12)' : 'rgba(148, 163, 184, 0.12)',
                              border: `1px solid ${chunk.domain === 'HR' ? 'rgba(99, 102, 241, 0.3)' : chunk.domain === 'Finance' ? 'rgba(16, 185, 129, 0.3)' : chunk.domain === 'IT' ? 'rgba(245, 158, 11, 0.3)' : 'rgba(148, 163, 184, 0.3)'}`,
                              padding: '2px 6px',
                              borderRadius: '4px',
                            }}
                          >
                            {chunk.domain}
                          </span>
                        )}

                        {/* Page indicator if present */}
                        {chunk.page && (
                          <span style={{ fontSize: '11px', color: 'var(--color-text-muted)', background: 'var(--color-bg-base)', padding: '2px 6px', borderRadius: '4px' }}>
                            Page {chunk.page}
                          </span>
                        )}

                        {/* Chunk ID */}
                        <span
                          style={{
                            fontSize: '11px',
                            fontFamily: 'monospace',
                            color: 'var(--color-text-muted)',
                            background: 'var(--color-bg-base)',
                            padding: '2px 6px',
                            borderRadius: '4px',
                            border: '1px solid var(--color-border)',
                          }}
                        >
                          {chunk.chunk_id}
                        </span>
                      </div>

                      {/* Right: Scores & Actions */}
                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        {/* Similarity Score Badge */}
                        <div
                          style={{
                            padding: '3px 10px',
                            borderRadius: '6px',
                            background: scoreStyle.bg,
                            border: `1px solid ${scoreStyle.border}`,
                            color: scoreStyle.text,
                            fontSize: '12px',
                            fontWeight: 700,
                            display: 'flex',
                            alignItems: 'center',
                            gap: '6px',
                          }}
                        >
                          <span>Cosine Sim: {chunk.score.toFixed(4)}</span>
                        </div>

                        {/* Distance metric */}
                        {chunk.distance !== undefined && (
                          <span style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>
                            Dist: {chunk.distance.toFixed(4)}
                          </span>
                        )}

                        {/* Copy Button */}
                        <button
                          onClick={() => handleCopyText(chunk.chunk_id, chunk.text)}
                          style={{
                            background: 'none',
                            border: '1px solid var(--color-border)',
                            borderRadius: '4px',
                            color: 'var(--color-text-secondary)',
                            padding: '3px 8px',
                            fontSize: '11px',
                            cursor: 'pointer',
                          }}
                        >
                          {copiedId === chunk.chunk_id ? '✓ Copied' : 'Copy'}
                        </button>
                      </div>
                    </div>

                    {/* Chunk Card Content */}
                    <div
                      style={{
                        padding: '16px 18px',
                        fontSize: '14px',
                        color: 'var(--color-text-primary)',
                        lineHeight: 1.6,
                        whiteSpace: 'pre-wrap',
                        background: 'var(--color-bg-surface)',
                        fontFamily: 'inherit',
                      }}
                    >
                      {chunk.text}
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
