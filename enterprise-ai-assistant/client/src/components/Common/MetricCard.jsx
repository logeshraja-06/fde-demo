import React from 'react'

/**
 * MetricCard.jsx
 * --------------
 * Reusable metric card for Dashboard and Analytics pages.
 * Displays real enterprise operational metrics with clean aesthetic.
 */
export default function MetricCard({
  title,
  value,
  subtitle,
  icon,
  color = '#818cf8',
  badge,
  badgeType = 'default',
  onClick,
}) {
  const isClickable = Boolean(onClick)

  return (
    <div
      onClick={onClick}
      style={{
        background: 'var(--color-bg-surface)',
        border: '1px solid var(--color-border)',
        borderRadius: '10px',
        padding: '18px 20px',
        display: 'flex',
        flexDirection: 'column',
        gap: '12px',
        cursor: isClickable ? 'pointer' : 'default',
        transition: 'all 0.15s ease',
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
        position: 'relative',
        overflow: 'hidden',
      }}
      onMouseEnter={(e) => {
        if (isClickable) {
          e.currentTarget.style.borderColor = color
          e.currentTarget.style.transform = 'translateY(-2px)'
        }
      }}
      onMouseLeave={(e) => {
        if (isClickable) {
          e.currentTarget.style.borderColor = 'var(--color-border)'
          e.currentTarget.style.transform = 'none'
        }
      }}
    >
      {/* Top row: Title and Icon */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <span
          style={{
            fontSize: '11px',
            fontWeight: 700,
            textTransform: 'uppercase',
            letterSpacing: '0.07em',
            color: 'var(--color-text-secondary)',
          }}
        >
          {title}
        </span>
        {icon && (
          <div
            style={{
              width: '30px',
              height: '30px',
              borderRadius: '6px',
              background: 'var(--color-bg-base)',
              border: '1px solid var(--color-border)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '14px',
              color,
            }}
          >
            {icon}
          </div>
        )}
      </div>

      {/* Metric Value */}
      <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px' }}>
        <span
          style={{
            fontSize: '28px',
            fontWeight: 800,
            color: 'var(--color-text-primary)',
            letterSpacing: '-0.03em',
            lineHeight: 1.1,
          }}
        >
          {value !== undefined && value !== null ? value : '—'}
        </span>

        {badge && (
          <span
            style={{
              fontSize: '11px',
              fontWeight: 600,
              padding: '2px 6px',
              borderRadius: '4px',
              background:
                badgeType === 'success'
                  ? 'rgba(16, 185, 129, 0.15)'
                  : badgeType === 'warning'
                  ? 'rgba(245, 158, 11, 0.15)'
                  : badgeType === 'danger'
                  ? 'rgba(239, 68, 68, 0.15)'
                  : 'rgba(99, 102, 241, 0.15)',
              color:
                badgeType === 'success'
                  ? '#10b981'
                  : badgeType === 'warning'
                  ? '#f59e0b'
                  : badgeType === 'danger'
                  ? '#ef4444'
                  : '#818cf8',
              border: `1px solid ${
                badgeType === 'success'
                  ? 'rgba(16, 185, 129, 0.3)'
                  : badgeType === 'warning'
                  ? 'rgba(245, 158, 11, 0.3)'
                  : badgeType === 'danger'
                  ? 'rgba(239, 68, 68, 0.3)'
                  : 'rgba(99, 102, 241, 0.3)'
              }`,
            }}
          >
            {badge}
          </span>
        )}
      </div>

      {/* Subtitle / context description */}
      {subtitle && (
        <div style={{ fontSize: '12px', color: 'var(--color-text-muted)', lineHeight: 1.4 }}>
          {subtitle}
        </div>
      )}

      {/* Bottom accent glow strip */}
      <div
        style={{
          position: 'absolute',
          bottom: 0,
          left: 0,
          right: 0,
          height: '2px',
          background: color,
          opacity: 0.6,
        }}
      />
    </div>
  )
}
