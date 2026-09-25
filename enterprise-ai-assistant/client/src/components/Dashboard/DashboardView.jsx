import React, { useState, useEffect } from 'react'
import MetricCard from '../Common/MetricCard'
import StatusBadge from '../Common/StatusBadge'
import { getAnalytics, getChatStatus } from '../../services/api'

/**
 * DashboardView.jsx
 * -----------------
 * Phase 6 Enterprise AI Operational Dashboard.
 *
 * Shows real, honest metrics:
 * - Knowledge Base: Total Documents, Total Chunks
 * - AI Requests: Total Questions, Successful Grounded Responses
 * - Safety & Observability: Blocked Requests, Insufficient Evidence Requests
 * - Live recent activity log
 * - Quick launch actions to AI Assistant, Knowledge Base, Retrieval Playground, Guardrails
 */
export default function DashboardView({ onNavigate }) {
  const [analytics, setAnalytics] = useState(null)
  const [chatStatus, setChatStatus] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const loadData = async () => {
    try {
      setLoading(true)
      setError(null)
      const [analyticsData, statusData] = await Promise.all([
        getAnalytics().catch((err) => {
          console.warn('Analytics endpoint error:', err)
          return null
        }),
        getChatStatus().catch((err) => {
          console.warn('Chat status error:', err)
          return null
        }),
      ])

      setAnalytics(analyticsData)
      setChatStatus(statusData)
    } catch (err) {
      setError(err.message || 'Failed to load dashboard metrics.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
    // Periodic refresh every 10 seconds for live demo observability
    const interval = setInterval(loadData, 10000)
    return () => clearInterval(interval)
  }, [])

  const kb = analytics?.knowledge_base || {}
  const reqs = analytics?.requests || {}
  const recent = analytics?.recent_activity || []

  return (
    <div
      style={{
        flex: 1,
        overflowY: 'auto',
        padding: '32px 36px',
        display: 'flex',
        flexDirection: 'column',
        gap: '28px',
        background: 'var(--color-bg-base)',
      }}
    >
      {/* ── Top Header Banner ── */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '16px',
          borderBottom: '1px solid var(--color-border)',
          paddingBottom: '20px',
        }}
      >
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
            <span
              style={{
                fontSize: '11px',
                fontWeight: 700,
                color: 'var(--color-brand)',
                textTransform: 'uppercase',
                letterSpacing: '0.08em',
                background: 'rgba(99, 102, 241, 0.12)',
                padding: '3px 8px',
                borderRadius: '4px',
              }}
            >
              Enterprise AI &bull; Forward Deployed Demo
            </span>
            <span
              style={{
                fontSize: '11px',
                fontWeight: 600,
                color: '#10b981',
                background: 'rgba(16, 185, 129, 0.12)',
                padding: '3px 8px',
                borderRadius: '4px',
                border: '1px solid rgba(16, 185, 129, 0.25)',
              }}
            >
              ● Production Pipeline Active
            </span>
          </div>
          <h1
            style={{
              fontSize: '24px',
              fontWeight: 700,
              color: 'var(--color-text-primary)',
              letterSpacing: '-0.02em',
              margin: 0,
            }}
          >
            System Observability &amp; Operational Dashboard
          </h1>
          <p
            style={{
              fontSize: '13px',
              color: 'var(--color-text-secondary)',
              marginTop: '4px',
              marginBottom: 0,
            }}
          >
            Real-time pipeline transparency, vector store telemetry, and guardrail enforcement metrics.
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <button
            onClick={loadData}
            disabled={loading}
            style={{
              background: 'var(--color-bg-surface)',
              border: '1px solid var(--color-border)',
              borderRadius: '6px',
              padding: '8px 14px',
              color: 'var(--color-text-secondary)',
              fontSize: '12px',
              fontWeight: 600,
              cursor: loading ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
            }}
          >
            <span>🔄</span>
            <span>{loading ? 'Refreshing...' : 'Refresh Telemetry'}</span>
          </button>

          <button
            onClick={() => onNavigate && onNavigate('assistant')}
            style={{
              background: 'var(--color-brand)',
              border: 'none',
              borderRadius: '6px',
              padding: '8px 16px',
              color: '#fff',
              fontSize: '12px',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              boxShadow: '0 2px 8px rgba(99, 102, 241, 0.3)',
            }}
          >
            <span>Ask AI Assistant ➔</span>
          </button>
        </div>
      </div>

      {error && (
        <div
          style={{
            padding: '12px 16px',
            background: 'rgba(239, 68, 68, 0.08)',
            border: '1px solid rgba(239, 68, 68, 0.25)',
            borderRadius: '6px',
            color: '#f87171',
            fontSize: '13px',
          }}
        >
          {error}
        </div>
      )}

      {/* ── Metric Cards Grid ── */}
      <div>
        <div
          style={{
            fontSize: '12px',
            fontWeight: 700,
            color: 'var(--color-text-secondary)',
            textTransform: 'uppercase',
            letterSpacing: '0.07em',
            marginBottom: '14px',
          }}
        >
          Core System Telemetry
        </div>

        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
            gap: '16px',
          }}
        >
          {/* Card 1: Total Documents */}
          <MetricCard
            title="Total Documents"
            value={kb.total_documents !== undefined ? kb.total_documents : '—'}
            subtitle="Uploaded & parsed policy files"
            icon="📄"
            color="#818cf8"
            onClick={() => onNavigate && onNavigate('knowledge')}
          />

          {/* Card 2: Total Chunks */}
          <MetricCard
            title="Total Chunks"
            value={kb.total_chunks !== undefined ? kb.total_chunks.toLocaleString() : '—'}
            subtitle="Indexed in ChromaDB vector store"
            icon="🧩"
            color="#38bdf8"
            onClick={() => onNavigate && onNavigate('retrieval')}
          />

          {/* Card 3: Total Questions */}
          <MetricCard
            title="Total Questions"
            value={reqs.total_questions !== undefined ? reqs.total_questions : '—'}
            subtitle="Queries processed by pipeline"
            icon="💬"
            color="#a78bfa"
            onClick={() => onNavigate && onNavigate('assistant')}
          />

          {/* Card 4: Successful Responses */}
          <MetricCard
            title="Grounded Responses"
            value={reqs.successful_responses !== undefined ? reqs.successful_responses : '—'}
            subtitle={
              reqs.success_rate_pct !== undefined
                ? `${reqs.success_rate_pct}% grounded accuracy`
                : 'Passed all 5 pipeline layers'
            }
            icon="✓"
            color="#10b981"
            badge={reqs.success_rate_pct !== undefined ? `${reqs.success_rate_pct}%` : undefined}
            badgeType="success"
            onClick={() => onNavigate && onNavigate('analytics')}
          />

          {/* Card 5: Blocked Requests */}
          <MetricCard
            title="Blocked Requests"
            value={reqs.blocked_requests !== undefined ? reqs.blocked_requests : '—'}
            subtitle="Input injection or safety violations"
            icon="🛡️"
            color="#ef4444"
            badge={reqs.blocked_requests > 0 ? 'Defended' : undefined}
            badgeType="danger"
            onClick={() => onNavigate && onNavigate('guardrails')}
          />

          {/* Card 6: Insufficient Evidence */}
          <MetricCard
            title="Insufficient Evidence"
            value={reqs.insufficient_evidence !== undefined ? reqs.insufficient_evidence : '—'}
            subtitle="RAG relevance below threshold"
            icon="⚠"
            color="#f59e0b"
            badge={reqs.insufficient_evidence > 0 ? 'Protected' : undefined}
            badgeType="warning"
            onClick={() => onNavigate && onNavigate('guardrails')}
          />
        </div>
      </div>

      {/* ── Two-Column Section: Pipeline Architecture + Recent Activity ── */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(420px, 1fr))',
          gap: '24px',
        }}
      >
        {/* Left Box: End-to-End Pipeline Overview */}
        <div
          style={{
            background: 'var(--color-bg-surface)',
            border: '1px solid var(--color-border)',
            borderRadius: '10px',
            padding: '20px',
            display: 'flex',
            flexDirection: 'column',
            gap: '16px',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span
              style={{
                fontSize: '12px',
                fontWeight: 700,
                color: 'var(--color-text-secondary)',
                textTransform: 'uppercase',
                letterSpacing: '0.07em',
              }}
            >
              5-Stage AI Production Pipeline
            </span>
            <span
              style={{
                fontSize: '11px',
                color: '#818cf8',
                cursor: 'pointer',
              }}
              onClick={() => onNavigate && onNavigate('guardrails')}
            >
              Configure Guardrails ➔
            </span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {[
              {
                num: '1',
                name: 'Input Guardrail',
                desc: 'Length bounds (max 2000 chars) & prompt injection regex scanner',
                status: 'Enforced',
                badgeColor: '#10b981',
              },
              {
                num: '2',
                name: 'RAG Retrieval',
                desc: 'all-MiniLM-L6-v2 embeddings + ChromaDB cosine vector search',
                status: 'Enforced',
                badgeColor: '#818cf8',
              },
              {
                num: '3',
                name: 'Grounding Check',
                desc: `Relevance cutoff (similarity ≥ ${kb.relevance_threshold || 0.35}) blocks hallucinations`,
                status: 'Enforced',
                badgeColor: '#f59e0b',
              },
              {
                num: '4',
                name: 'LLM Generation',
                desc: `${chatStatus?.model || 'Gemini 2.5 Flash'} strictly instructed to answer from retrieved context only`,
                status: 'Configured',
                badgeColor: '#10b981',
              },
              {
                num: '5',
                name: 'Output Guardrail',
                desc: 'Non-empty verification, source citation check, and system prompt leakage audit',
                status: 'Enforced',
                badgeColor: '#10b981',
              },
            ].map((st, i) => (
              <div
                key={i}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '10px 12px',
                  background: 'var(--color-bg-base)',
                  border: '1px solid var(--color-border)',
                  borderRadius: '6px',
                  gap: '12px',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', minWidth: 0 }}>
                  <div
                    style={{
                      width: '20px',
                      height: '20px',
                      borderRadius: '50%',
                      background: 'rgba(99, 102, 241, 0.15)',
                      color: '#818cf8',
                      fontSize: '11px',
                      fontWeight: 700,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      flexShrink: 0,
                    }}
                  >
                    {st.num}
                  </div>
                  <div style={{ minWidth: 0 }}>
                    <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--color-text-primary)' }}>
                      {st.name}
                    </div>
                    <div
                      style={{
                        fontSize: '11px',
                        color: 'var(--color-text-muted)',
                        whiteSpace: 'nowrap',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                      }}
                    >
                      {st.desc}
                    </div>
                  </div>
                </div>

                <span
                  style={{
                    fontSize: '10px',
                    fontWeight: 700,
                    color: st.badgeColor,
                    background: `${st.badgeColor}18`,
                    border: `1px solid ${st.badgeColor}35`,
                    padding: '2px 8px',
                    borderRadius: '4px',
                    flexShrink: 0,
                  }}
                >
                  {st.status}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Right Box: Recent Activity Feed */}
        <div
          style={{
            background: 'var(--color-bg-surface)',
            border: '1px solid var(--color-border)',
            borderRadius: '10px',
            padding: '20px',
            display: 'flex',
            flexDirection: 'column',
            gap: '16px',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span
              style={{
                fontSize: '12px',
                fontWeight: 700,
                color: 'var(--color-text-secondary)',
                textTransform: 'uppercase',
                letterSpacing: '0.07em',
              }}
            >
              Recent AI Pipeline Activity
            </span>
            <span
              style={{
                fontSize: '11px',
                color: '#818cf8',
                cursor: 'pointer',
              }}
              onClick={() => onNavigate && onNavigate('analytics')}
            >
              Full Analytics Log ➔
            </span>
          </div>

          {recent.length === 0 ? (
            <div
              style={{
                padding: '30px',
                textAlign: 'center',
                color: 'var(--color-text-muted)',
                fontSize: '12px',
                background: 'var(--color-bg-base)',
                borderRadius: '6px',
                border: '1px dashed var(--color-border)',
              }}
            >
              No queries executed yet. Try asking a question in the{' '}
              <span
                style={{ color: '#818cf8', cursor: 'pointer', textDecoration: 'underline' }}
                onClick={() => onNavigate && onNavigate('assistant')}
              >
                AI Assistant
              </span>
              .
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '340px', overflowY: 'auto' }}>
              {recent.slice(0, 7).map((ev, idx) => {
                const timeStr = ev.timestamp
                  ? new Date(ev.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
                  : 'Recent'

                let statusBadge = {
                  label: 'Grounded',
                  icon: '✓',
                  color: '#10b981',
                  bg: 'rgba(16, 185, 129, 0.12)',
                  border: 'rgba(16, 185, 129, 0.3)',
                }

                if (ev.status === 'blocked_input') {
                  statusBadge = {
                    label: 'Prompt Injection Blocked',
                    icon: '✕',
                    color: '#ef4444',
                    bg: 'rgba(239, 68, 68, 0.12)',
                    border: 'rgba(239, 68, 68, 0.3)',
                  }
                } else if (ev.status === 'insufficient_evidence') {
                  statusBadge = {
                    label: 'Insufficient Evidence',
                    icon: '⚠',
                    color: '#f59e0b',
                    bg: 'rgba(245, 158, 11, 0.12)',
                    border: 'rgba(245, 158, 11, 0.3)',
                  }
                } else if (ev.status === 'blocked_output') {
                  statusBadge = {
                    label: 'Output Blocked',
                    icon: '✕',
                    color: '#ef4444',
                    bg: 'rgba(239, 68, 68, 0.12)',
                    border: 'rgba(239, 68, 68, 0.3)',
                  }
                }

                return (
                  <div
                    key={idx}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      padding: '8px 12px',
                      background: 'var(--color-bg-base)',
                      border: '1px solid var(--color-border)',
                      borderRadius: '6px',
                      gap: '12px',
                    }}
                  >
                    <div style={{ minWidth: 0, flex: 1 }}>
                      <div
                        style={{
                          fontSize: '12px',
                          color: 'var(--color-text-primary)',
                          fontWeight: 500,
                          whiteSpace: 'nowrap',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                        }}
                        title={ev.query}
                      >
                        {ev.query}
                      </div>
                      <div style={{ fontSize: '10px', color: 'var(--color-text-muted)', marginTop: '2px' }}>
                        {timeStr} &bull; {ev.response_time_ms} ms {ev.sources_count ? `&bull; ${ev.sources_count} source(s)` : ''}
                      </div>
                    </div>

                    <span
                      style={{
                        fontSize: '10px',
                        fontWeight: 700,
                        color: statusBadge.color,
                        background: statusBadge.bg,
                        border: `1px solid ${statusBadge.border}`,
                        padding: '2px 8px',
                        borderRadius: '4px',
                        flexShrink: 0,
                        display: 'flex',
                        alignItems: 'center',
                        gap: '4px',
                      }}
                    >
                      <span>{statusBadge.icon}</span>
                      <span>{statusBadge.label}</span>
                    </span>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
