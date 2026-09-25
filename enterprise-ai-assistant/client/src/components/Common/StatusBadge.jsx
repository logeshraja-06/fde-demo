import React from 'react'

/**
 * StatusBadge.jsx
 * ---------------
 * Reusable status badge with enterprise dark-mode styling.
 */
export default function StatusBadge({ status, label, icon }) {
  const normalized = (status || '').toLowerCase()

  let color = '#94a3b8'
  let bg = 'rgba(148, 163, 184, 0.12)'
  let border = 'rgba(148, 163, 184, 0.25)'
  let defaultIcon = '●'

  if (['passed', 'completed', 'grounded', 'ready', 'active', 'ok', 'success'].includes(normalized)) {
    color = '#10b981'
    bg = 'rgba(16, 185, 129, 0.12)'
    border = 'rgba(16, 185, 129, 0.3)'
    defaultIcon = '✓'
  } else if (['blocked', 'failed', 'error', 'blocked_input', 'blocked_output'].includes(normalized)) {
    color = '#ef4444'
    bg = 'rgba(239, 68, 68, 0.12)'
    border = 'rgba(239, 68, 68, 0.3)'
    defaultIcon = '✕'
  } else if (['insufficient_evidence', 'warning', 'borderline'].includes(normalized)) {
    color = '#f59e0b'
    bg = 'rgba(245, 158, 11, 0.12)'
    border = 'rgba(245, 158, 11, 0.3)'
    defaultIcon = '⚠'
  } else if (['running', 'processing'].includes(normalized)) {
    color = '#38bdf8'
    bg = 'rgba(56, 189, 248, 0.15)'
    border = 'rgba(56, 189, 248, 0.35)'
    defaultIcon = '●'
  }

  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '4px',
        padding: '2px 8px',
        borderRadius: '9999px',
        fontSize: '11px',
        fontWeight: 600,
        color,
        background: bg,
        border: `1px solid ${border}`,
        letterSpacing: '0.03em',
      }}
    >
      <span>{icon !== undefined ? icon : defaultIcon}</span>
      <span>{label || status}</span>
    </span>
  )
}
