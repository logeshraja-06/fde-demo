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

function Header({ title, connectionStatus }) {
  /**
   * connectionStatus can be one of:
   *   'checking'     — waiting for the first response
   *   'connected'    — GET /health returned 200 OK
   *   'disconnected' — request failed or returned an error
   */

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
      }}
    >
      {/* Page title */}
      <h1
        style={{
          fontSize: 15,
          fontWeight: 600,
          color: 'var(--color-text-primary)',
          letterSpacing: '-0.01em',
        }}
      >
        {title}
      </h1>

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
        {/* Dot indicator — filled if connected, hollow if not */}
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
