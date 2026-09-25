import React from 'react'

/**
 * PipelineStage.jsx
 * -----------------
 * Renders a single stage in the enterprise AI pipeline.
 *
 * Supported states:
 * - 'passed' | 'completed' : Green check
 * - 'blocked' | 'failed'   : Red cross or amber warning
 * - 'not_run'              : Gray circle
 * - 'running'              : Blue/cyan pulsing indicator
 * - 'pending'              : Subdued ring
 */
export default function PipelineStage({
  name,
  stageKey,
  status,
  subtitle,
  detail,
  reason,
  checks,
  isLast = false,
}) {
  const normalizedStatus = (status || 'not_run').toLowerCase()

  const getStatusConfig = () => {
    switch (normalizedStatus) {
      case 'passed':
      case 'completed':
        return {
          icon: '✓',
          color: '#10b981',
          bg: 'rgba(16, 185, 129, 0.12)',
          border: 'rgba(16, 185, 129, 0.3)',
          label: normalizedStatus === 'completed' ? 'Completed' : 'Passed',
        }
      case 'blocked':
        return {
          icon: '✕',
          color: stageKey === 'grounding' ? '#f59e0b' : '#ef4444',
          bg: stageKey === 'grounding' ? 'rgba(245, 158, 11, 0.12)' : 'rgba(239, 68, 68, 0.12)',
          border: stageKey === 'grounding' ? 'rgba(245, 158, 11, 0.3)' : 'rgba(239, 68, 68, 0.3)',
          label: stageKey === 'grounding' ? 'Insufficient Evidence' : 'Blocked',
        }
      case 'failed':
        return {
          icon: '!',
          color: '#ef4444',
          bg: 'rgba(239, 68, 68, 0.12)',
          border: 'rgba(239, 68, 68, 0.3)',
          label: 'Failed',
        }
      case 'running':
        return {
          icon: '●',
          color: '#38bdf8',
          bg: 'rgba(56, 189, 248, 0.15)',
          border: 'rgba(56, 189, 248, 0.4)',
          label: 'Running...',
        }
      case 'pending':
        return {
          icon: '○',
          color: 'var(--color-text-muted)',
          bg: 'rgba(255, 255, 255, 0.03)',
          border: 'rgba(255, 255, 255, 0.08)',
          label: 'Pending',
        }
      case 'not_run':
      default:
        return {
          icon: '○',
          color: 'var(--color-text-muted)',
          bg: 'rgba(255, 255, 255, 0.03)',
          border: 'var(--color-border)',
          label: 'Not Run',
        }
    }
  }

  const cfg = getStatusConfig()

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', flex: 1, minWidth: '150px' }}>
      {/* Node box */}
      <div
        style={{
          width: '100%',
          background: cfg.bg,
          border: `1px solid ${cfg.border}`,
          borderRadius: '8px',
          padding: '10px 12px',
          display: 'flex',
          flexDirection: 'column',
          gap: '4px',
          transition: 'all 0.2s ease',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '8px' }}>
          <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--color-text-primary)' }}>
            {name}
          </span>
          <span
            style={{
              fontSize: '10px',
              fontWeight: 700,
              padding: '1px 6px',
              borderRadius: '4px',
              color: cfg.color,
              background: 'rgba(0,0,0,0.3)',
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
            }}
          >
            <span>{cfg.icon}</span>
            <span>{cfg.label}</span>
          </span>
        </div>

        {/* Dynamic subtitle (e.g. "3 relevant chunks found" or "Score: 0.47") */}
        {subtitle && (
          <div style={{ fontSize: '11px', color: 'var(--color-text-secondary)', marginTop: '2px' }}>
            {subtitle}
          </div>
        )}

        {/* Reason when blocked */}
        {reason && (
          <div style={{ fontSize: '11px', color: cfg.color, fontWeight: 500, marginTop: '2px' }}>
            {reason}
          </div>
        )}

        {/* Specific sub-checks */}
        {checks && (
          <div style={{ fontSize: '10px', color: 'var(--color-text-muted)', marginTop: '4px', lineHeight: 1.4 }}>
            {Object.entries(checks).map(([k, v]) => (
              <div key={k} style={{ textTransform: 'capitalize' }}>
                • {k.replace(/_/g, ' ')}: <strong style={{ color: v === 'passed' || v === 'not_detected' ? '#10b981' : '#f87171' }}>{v}</strong>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Downward / Rightward indicator between stages if rendered */}
      {!isLast && (
        <div
          style={{
            alignSelf: 'center',
            color: 'var(--color-text-muted)',
            fontSize: '12px',
            padding: '2px 0',
            userSelect: 'none',
          }}
        >
          ↓
        </div>
      )}
    </div>
  )
}
