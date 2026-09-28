/**
 * Header.jsx
 * ----------
 * The top bar of the application's main content area.
 *
 * It shows:
 * - The current page title
 * - The backend connection status indicator
 *
 * The connection status is REAL — it reflects an actual
 * HTTP call to the FastAPI /health endpoint (see useBackendStatus.js).
 */

function Header({
  title,
  connectionStatus,
  viewMode = 'engineering',
  onToggleViewMode,
  customerConfig = {},
}) {
  const statusConfig = {
    checking: {
      dot: '○',
      label: 'Checking Backend...',
      color: 'var(--color-text-muted)',
    },
    connected: {
      dot: '●',
      label: 'Backend Connected',
      color: 'var(--color-success)',
    },
    unavailable: {
      dot: '○',
      label: 'Backend Unavailable',
      color: 'var(--color-error)',
    },
    disconnected: {
      dot: '○',
      label: 'Backend Unavailable',
      color: 'var(--color-error)',
    },
  }

  const status = statusConfig[connectionStatus] || statusConfig.unavailable
  const orgName = customerConfig.organization || 'Acme Corporation'

  return (
    <header
      style={{
        height: 'var(--header-height)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 28px',
        borderBottom: '1px solid var(--color-border)',
        background: 'var(--color-bg-surface)',
        flexShrink: 0,
        gap: 16,
      }}
    >
      {/* Page title and Org */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <h1
          style={{
            fontSize: 15,
            fontWeight: 600,
            color: 'var(--color-text-primary)',
            letterSpacing: '-0.01em',
            margin: 0,
          }}
        >
          {title}
        </h1>
        <span
          style={{
            fontSize: 10,
            background: 'var(--color-accent-muted)',
            color: 'var(--color-brand)',
            padding: '2px 6px',
            borderRadius: 4,
            fontWeight: 600,
          }}
        >
          {orgName}
        </span>
      </div>

      {/* Center: Role-Based View Simulation Toggle (Customer Demo vs Engineering) */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            background: 'var(--color-bg-base)',
            border: '1px solid var(--color-border)',
            padding: '2px',
            borderRadius: 6,
          }}
        >
          <button
            id="mode-toggle-customer"
            type="button"
            title="Simplified experience for customer executive review"
            onClick={() => onToggleViewMode && onToggleViewMode('customer')}
            style={{
              background: viewMode === 'customer' ? 'var(--color-brand)' : 'transparent',
              color: viewMode === 'customer' ? '#fff' : 'var(--color-text-secondary)',
              border: 'none',
              borderRadius: 4,
              padding: '4px 10px',
              fontSize: 11,
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: 4,
              transition: 'all 0.15s ease',
            }}
          >
            <span>👤</span> Customer Demo Mode
          </button>

          <button
            id="mode-toggle-engineering"
            type="button"
            title="Deep technical observability for Forward Deployed Engineers"
            onClick={() => onToggleViewMode && onToggleViewMode('engineering')}
            style={{
              background: viewMode === 'engineering' ? 'var(--color-brand)' : 'transparent',
              color: viewMode === 'engineering' ? '#fff' : 'var(--color-text-secondary)',
              border: 'none',
              borderRadius: 4,
              padding: '4px 10px',
              fontSize: 11,
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: 4,
              transition: 'all 0.15s ease',
            }}
          >
            <span>🛠️</span> Engineering Mode
          </button>
        </div>

        <span
          style={{
            fontSize: 9,
            color: 'var(--color-text-muted)',
            background: 'rgba(255,255,255,0.04)',
            padding: '2px 5px',
            borderRadius: 3,
            border: '1px solid var(--color-border)',
          }}
        >
          Role Simulation (Demo)
        </span>
      </div>

      {/* Backend connection status indicator */}
      <div
        id="connection-status"
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 6,
          fontSize: 12,
          color: 'var(--color-text-secondary)',
        }}
      >
        <span style={{ fontSize: 11, color: 'var(--color-text-muted)' }}>Backend</span>
        <span style={{ color: 'var(--color-border)' }}>·</span>
        <span
          style={{
            color: status.color,
            fontSize: 10,
            lineHeight: 1,
            transition: 'color 0.3s ease',
          }}
        >
          {status.dot}
        </span>
        <span
          style={{
            color: status.color,
            fontWeight: 500,
            transition: 'color 0.3s ease',
          }}
        >
          {status.label}
        </span>
      </div>
    </header>
  )
}

export default Header
