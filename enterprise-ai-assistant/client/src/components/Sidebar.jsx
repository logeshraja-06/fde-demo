import React from 'react'

/**
 * Sidebar.jsx
 * -----------
 * Enterprise AI Left Navigation Bar.
 *
 * Sections:
 *   1. Overview (Dashboard)
 *   2. AI Assistant (Chat)
 *   3. Knowledge Base
 *   4. Retrieval Playground
 *   5. Guardrails
 *   6. Analytics
 *
 * Bottom status:
 *   System Status
 *   ● Backend Connected
 *   ● Knowledge Base Ready
 */

const NAV_ITEMS = [
  { id: 'overview',   label: 'Overview',             icon: '📊', badge: null },
  { id: 'assistant',  label: 'AI Assistant',         icon: '💬', badge: 'LLM' },
  { id: 'knowledge',  label: 'Knowledge Base',       icon: '📁', badge: null },
  { id: 'retrieval',  label: 'Retrieval Playground', icon: '⚡', badge: 'RAG' },
  { id: 'guardrails', label: 'Guardrails',           icon: '🛡️', badge: 'SAFETY' },
  { id: 'analytics',  label: 'Analytics',            icon: '📈', badge: 'PHASE 6' },
]

export default function Sidebar({ activeNav, onNavChange, connectionStatus = 'connected', kbReady = true }) {
  const isBackendConnected = connectionStatus === 'connected'

  return (
    <aside
      style={{
        width: 'var(--sidebar-width)',
        background: 'var(--color-sidebar-bg)',
        borderRight: '1px solid var(--color-sidebar-border)',
        display: 'flex',
        flexDirection: 'column',
        flexShrink: 0,
        height: '100%',
        boxSizing: 'border-box',
      }}
    >
      {/* ── Logo / Header ── */}
      <div
        style={{
          height: 'var(--header-height)',
          display: 'flex',
          alignItems: 'center',
          padding: '0 20px',
          borderBottom: '1px solid var(--color-sidebar-border)',
          gap: '10px',
        }}
      >
        <div
          style={{
            width: 28,
            height: 28,
            background: 'var(--color-brand)',
            borderRadius: 6,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: 14,
            fontWeight: 700,
            color: '#fff',
            flexShrink: 0,
          }}
        >
          K
        </div>
        <div>
          <div style={{ fontWeight: 700, fontSize: 13, color: 'var(--color-text-primary)', lineHeight: 1.2, letterSpacing: '0.04em' }}>
            ENTERPRISE AI
          </div>
          <div style={{ fontSize: 10, color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
            Forward Deployed Demo
          </div>
        </div>
      </div>

      {/* ── Navigation Items ── */}
      <nav style={{ flex: 1, padding: '14px 10px', display: 'flex', flexDirection: 'column', gap: 3 }}>
        <div
          style={{
            fontSize: 10,
            fontWeight: 700,
            color: 'var(--color-text-muted)',
            textTransform: 'uppercase',
            letterSpacing: '0.08em',
            padding: '6px 12px 4px',
          }}
        >
          Navigation
        </div>

        {NAV_ITEMS.map((item) => {
          const isActive = activeNav === item.id
          return (
            <button
              key={item.id}
              id={`nav-${item.id}`}
              onClick={() => onNavChange(item.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 10,
                padding: '9px 12px',
                borderRadius: 6,
                border: 'none',
                cursor: 'pointer',
                width: '100%',
                textAlign: 'left',
                background: isActive ? 'var(--color-accent-muted)' : 'transparent',
                color: isActive ? 'var(--color-accent-hover)' : 'var(--color-text-secondary)',
                fontFamily: 'inherit',
                fontSize: 13,
                fontWeight: isActive ? 600 : 400,
                transition: 'background 0.15s ease, color 0.15s ease',
              }}
              onMouseEnter={(e) => {
                if (!isActive) {
                  e.currentTarget.style.background = 'var(--color-bg-elevated)'
                  e.currentTarget.style.color = 'var(--color-text-primary)'
                }
              }}
              onMouseLeave={(e) => {
                if (!isActive) {
                  e.currentTarget.style.background = 'transparent'
                  e.currentTarget.style.color = 'var(--color-text-secondary)'
                }
              }}
            >
              <span style={{ fontSize: 14 }}>{item.icon}</span>
              <span style={{ flex: 1 }}>{item.label}</span>

              {item.badge && (
                <span
                  style={{
                    fontSize: 9,
                    fontWeight: 700,
                    color:
                      item.badge === 'LLM'
                        ? '#10b981'
                        : item.badge === 'RAG'
                        ? '#818cf8'
                        : item.badge === 'SAFETY'
                        ? '#38bdf8'
                        : '#f59e0b',
                    background:
                      item.badge === 'LLM'
                        ? 'rgba(16, 185, 129, 0.15)'
                        : item.badge === 'RAG'
                        ? 'rgba(99, 102, 241, 0.15)'
                        : item.badge === 'SAFETY'
                        ? 'rgba(56, 189, 248, 0.15)'
                        : 'rgba(245, 158, 11, 0.15)',
                    padding: '2px 6px',
                    borderRadius: 3,
                  }}
                >
                  {item.badge}
                </span>
              )}
            </button>
          )
        })}
      </nav>

      {/* ── Bottom System Status (Required by Section 21) ── */}
      <div
        style={{
          padding: '16px 18px',
          borderTop: '1px solid var(--color-sidebar-border)',
          background: 'rgba(0, 0, 0, 0.2)',
          display: 'flex',
          flexDirection: 'column',
          gap: '8px',
        }}
      >
        <div
          style={{
            fontSize: 10,
            color: 'var(--color-text-muted)',
            fontWeight: 700,
            textTransform: 'uppercase',
            letterSpacing: '0.07em',
          }}
        >
          System Status
        </div>

        {/* Backend Connected */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '11px' }}>
          <span
            style={{
              color: isBackendConnected ? '#10b981' : '#ef4444',
              fontSize: '10px',
              lineHeight: 1,
            }}
          >
            {isBackendConnected ? '●' : '○'}
          </span>
          <span style={{ color: isBackendConnected ? 'var(--color-text-primary)' : '#f87171', fontWeight: 500 }}>
            {isBackendConnected ? 'Backend Connected' : 'Backend Unavailable'}
          </span>
        </div>

        {/* Knowledge Base Ready */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '11px' }}>
          <span
            style={{
              color: kbReady && isBackendConnected ? '#10b981' : '#f59e0b',
              fontSize: '10px',
              lineHeight: 1,
            }}
          >
            ●
          </span>
          <span
            style={{
              color: kbReady && isBackendConnected ? 'var(--color-text-primary)' : 'var(--color-text-muted)',
              fontWeight: 500,
            }}
          >
            {kbReady && isBackendConnected ? 'Knowledge Base Ready' : 'Knowledge Base Syncing'}
          </span>
        </div>
      </div>
    </aside>
  )
}
