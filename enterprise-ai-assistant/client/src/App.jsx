/**
 * App.jsx
 * -------
 * The root component of the React application.
 *
 * Phase 6 updates:
 *  - DashboardView (Overview / Operational Telemetry)
 *  - Grounded AI Assistant with visible 5-stage pipeline
 *  - Knowledge Base with visual processing lifecycle
 *  - Retrieval Playground for isolated vector search tests
 *  - Guardrails & Safety Control Center
 *  - Real-time Analytics & Execution Audit Log
 */

import { useState } from 'react'
import Sidebar from './components/Sidebar'
import Header from './components/Header'
import DashboardView from './components/Dashboard/DashboardView'
import ChatView from './components/Chat/ChatView'
import KnowledgeBaseView from './components/KnowledgeBase/KnowledgeBaseView'
import RetrievalPlayground from './components/RetrievalPlayground/RetrievalPlayground'
import GuardrailsView from './components/Guardrails/GuardrailsView'
import AnalyticsView from './components/Analytics/AnalyticsView'
import useBackendStatus from './hooks/useBackendStatus'

// Map each nav item to a human-readable page title shown in Header
const PAGE_TITLES = {
  overview:    'System Overview & Dashboard',
  assistant:   'AI Assistant',
  knowledge:   'Knowledge Base',
  retrieval:   'Retrieval Playground',
  guardrails:  'Guardrails & Safety Control Center',
  analytics:   'Observability & Analytics',
}

function App() {
  // Default to the overview/dashboard or assistant
  const [activeNav, setActiveNav] = useState('overview')

  // Check if FastAPI backend is reachable
  const connectionStatus = useBackendStatus()

  return (
    <div
      style={{
        display: 'flex',
        height: '100vh',
        background: 'var(--color-bg-base)',
        overflow: 'hidden',
      }}
    >
      {/* Left sidebar with real connection & KB status */}
      <Sidebar
        activeNav={activeNav}
        onNavChange={setActiveNav}
        connectionStatus={connectionStatus}
        kbReady={connectionStatus === 'connected'}
      />

      {/* Right side: header + content */}
      <div
        style={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
          background: 'var(--color-bg-surface)',
        }}
      >
        <Header
          title={PAGE_TITLES[activeNav] || 'Enterprise AI Assistant'}
          connectionStatus={connectionStatus}
        />

        {/* Backend Unavailable Banner (Section 6 Requirement) */}
        {connectionStatus !== 'connected' && connectionStatus !== 'checking' && (
          <div
            id="backend-unavailable-banner"
            style={{
              background: 'rgba(239, 68, 68, 0.1)',
              borderBottom: '1px solid rgba(239, 68, 68, 0.3)',
              padding: '10px 28px',
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              color: '#f87171',
              fontSize: '12px',
              flexShrink: 0,
            }}
          >
            <span style={{ fontSize: '14px' }}>⚠️</span>
            <div>
              <strong>Backend Unavailable:</strong> Unable to connect to the AI service. Check whether the backend is running.
            </div>
          </div>
        )}

        {/* Main content area */}
        <main style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column' }}>
          {/* Phase 6: Operational Telemetry & Overview Dashboard */}
          {activeNav === 'overview' && (
            <DashboardView onNavigate={setActiveNav} />
          )}

          {/* Phase 4/5/6: Grounded AI Assistant Chat with Visible Pipeline */}
          {activeNav === 'assistant' && (
            <ChatView />
          )}

          {/* Phase 2/6: Knowledge Base with Visual Processing Lifecycle */}
          {activeNav === 'knowledge' && (
            <KnowledgeBaseView />
          )}

          {/* Phase 3: RAG Retrieval Playground */}
          {activeNav === 'retrieval' && (
            <RetrievalPlayground />
          )}

          {/* Phase 5: Guardrails and AI Safety Control Center */}
          {activeNav === 'guardrails' && (
            <GuardrailsView />
          )}

          {/* Phase 6: Real-time Analytics & Audit Log */}
          {activeNav === 'analytics' && (
            <AnalyticsView />
          )}
        </main>
      </div>
    </div>
  )
}

export default App
