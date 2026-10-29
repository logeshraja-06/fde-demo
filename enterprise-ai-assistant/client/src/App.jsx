import React, { useState, useEffect } from 'react'
import DockSidebar from './components/DockSidebar'
import TopBar from './components/TopBar'
import ExecutiveChat from './components/ExecutiveChat'
import ExecutiveKnowledgeBase from './components/ExecutiveKnowledgeBase'
import useBackendStatus from './hooks/useBackendStatus'

export default function App() {
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('executive_theme') || 'dark'
  })

  // 'chat' | 'knowledge'
  const [activeMode, setActiveMode] = useState('chat')

  // Chat conversation state
  const [messages, setMessages] = useState([])
  const [initialPrompt, setInitialPrompt] = useState('')

  // Backend connection status
  const connectionStatus = useBackendStatus()

  // Apply theme to body
  useEffect(() => {
    document.body.setAttribute('data-theme', theme)
    localStorage.setItem('executive_theme', theme)
  }, [theme])

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'))
  }

  const handleSearch = (query) => {
    setActiveMode('chat')
    setInitialPrompt(query)
  }

  return (
    <div className="app-viewport">
      {/* Ambient Atmospheric Top Glow */}
      <div className="ambient-glow"></div>

      {/* ── Left Slim Dock Sidebar ── */}
      <DockSidebar
        activeTab={activeMode}
        onTabChange={(tab) => {
          if (tab === 'chat') setActiveMode('chat')
          if (tab === 'knowledge') setActiveMode('knowledge')
        }}
        onToggleSettings={() => {
          // Toggle between chat and knowledge base
          setActiveMode((prev) => (prev === 'chat' ? 'knowledge' : 'chat'))
        }}
      />

      {/* ── Main Application Window ── */}
      <div
        style={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          height: '100%',
          overflow: 'hidden',
          position: 'relative',
        }}
      >
        {/* Top Header Bar */}
        <TopBar
          activeMode={activeMode}
          onModeChange={setActiveMode}
          theme={theme}
          onToggleTheme={toggleTheme}
          onSearch={handleSearch}
        />

        {/* Backend Offline Banner (minimal) */}
        {connectionStatus !== 'connected' && connectionStatus !== 'checking' && (
          <div
            style={{
              padding: '6px 20px',
              backgroundColor: 'rgba(239, 68, 68, 0.1)',
              borderBottom: '1px solid rgba(239, 68, 68, 0.2)',
              color: '#f87171',
              fontSize: '12px',
              textAlign: 'center',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '6px',
              position: 'relative',
              zIndex: 15,
            }}
          >
            <span>⚠️</span>
            <span>AI backend is currently unreachable. Make sure the FastAPI server is running on port 8000.</span>
          </div>
        )}

        {/* Dynamic Views: Chat Mode or Knowledge Base Mode */}
        {activeMode === 'chat' ? (
          <ExecutiveChat
            initialPrompt={initialPrompt}
            onClearInitialPrompt={() => setInitialPrompt('')}
            messages={messages}
            setMessages={setMessages}
            theme={theme}
          />
        ) : (
          <ExecutiveKnowledgeBase
            onBackToChat={() => setActiveMode('chat')}
          />
        )}
      </div>
    </div>
  )
}
