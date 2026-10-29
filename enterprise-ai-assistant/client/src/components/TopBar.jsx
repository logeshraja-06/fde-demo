import React, { useState } from 'react'

export default function TopBar({
  activeMode = 'chat',
  onModeChange = () => {},
  theme = 'dark',
  onToggleTheme = () => {},
  onSearch = () => {},
}) {
  const [searchValue, setSearchValue] = useState('')

  const handleSearchSubmit = (e) => {
    if (e.key === 'Enter' && searchValue.trim()) {
      onSearch(searchValue.trim())
    }
  }

  return (
    <header
      style={{
        height: '60px',
        padding: '0 24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        position: 'relative',
        zIndex: 10,
        backgroundColor: 'transparent',
      }}
    >
      {/* ── Left Navigation: Arrows + Breadcrumb + Mode Pill ── */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        {/* Navigation Arrows */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <button
            onClick={() => onModeChange('chat')}
            title="Chat Mode"
            style={{
              width: '28px',
              height: '28px',
              borderRadius: '6px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--text-muted)',
              backgroundColor: 'var(--pill-bg)',
            }}
            onMouseEnter={(e) => (e.currentTarget.style.color = 'var(--text-primary)')}
            onMouseLeave={(e) => (e.currentTarget.style.color = 'var(--text-muted)')}
          >
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="19" y1="12" x2="5" y2="12"></line>
              <polyline points="12 19 5 12 12 5"></polyline>
            </svg>
          </button>
          <button
            onClick={() => onModeChange('knowledge')}
            title="Knowledge Base"
            style={{
              width: '28px',
              height: '28px',
              borderRadius: '6px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--text-muted)',
              backgroundColor: 'var(--pill-bg)',
            }}
            onMouseEnter={(e) => (e.currentTarget.style.color = 'var(--text-primary)')}
            onMouseLeave={(e) => (e.currentTarget.style.color = 'var(--text-muted)')}
          >
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="5" y1="12" x2="19" y2="12"></line>
              <polyline points="12 5 19 12 12 19"></polyline>
            </svg>
          </button>
        </div>

        {/* Breadcrumb Text */}
        <div style={{ fontSize: '12.5px', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span style={{ cursor: 'pointer', fontWeight: 600, color: 'var(--text-primary)' }} onClick={() => onModeChange('chat')}>TruthGuard</span>
          <span>&gt;</span>
          <span style={{ color: 'var(--text-secondary)', fontWeight: 500 }}>
            {activeMode === 'chat' ? 'Policy Analyzer' : 'Knowledge Base'}
          </span>
        </div>

        {/* Mode Switcher Pill [Chat Mode] [Knowledge Base] */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            backgroundColor: 'var(--pill-bg)',
            border: '1px solid var(--border-subtle)',
            borderRadius: '9999px',
            padding: '3px',
            gap: '2px',
          }}
        >
          <button
            onClick={() => onModeChange('chat')}
            style={{
              padding: '5px 14px',
              borderRadius: '9999px',
              fontSize: '12px',
              fontWeight: activeMode === 'chat' ? 600 : 500,
              backgroundColor: activeMode === 'chat' ? (theme === 'dark' ? '#ffffff' : '#0f172a') : 'transparent',
              color: activeMode === 'chat' ? (theme === 'dark' ? '#000000' : '#ffffff') : 'var(--text-muted)',
              transition: 'all 0.15s ease',
            }}
          >
            Chat Mode
          </button>
          <button
            onClick={() => onModeChange('knowledge')}
            style={{
              padding: '5px 14px',
              borderRadius: '9999px',
              fontSize: '12px',
              fontWeight: activeMode === 'knowledge' ? 600 : 500,
              backgroundColor: activeMode === 'knowledge' ? (theme === 'dark' ? '#ffffff' : '#0f172a') : 'transparent',
              color: activeMode === 'knowledge' ? (theme === 'dark' ? '#000000' : '#ffffff') : 'var(--text-muted)',
              transition: 'all 0.15s ease',
            }}
          >
            Knowledge Base
          </button>
        </div>
      </div>

      {/* ── Right Controls: Search, Theme Toggle, Multi-Agent Status ── */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
        {/* Search Input Box */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            backgroundColor: 'var(--pill-bg)',
            border: '1px solid var(--border-subtle)',
            borderRadius: '9999px',
            padding: '6px 14px',
            width: '200px',
          }}
        >
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="var(--text-muted)" strokeWidth="2">
            <circle cx="11" cy="11" r="8"></circle>
            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
          </svg>
          <input
            type="text"
            value={searchValue}
            onChange={(e) => setSearchValue(e.target.value)}
            onKeyDown={handleSearchSubmit}
            placeholder="Search Policy Docs..."
            style={{
              background: 'transparent',
              border: 'none',
              color: 'var(--text-primary)',
              fontSize: '12px',
              width: '100%',
              outline: 'none',
            }}
          />
        </div>

        {/* Theme Toggle Button (Dark / Light) */}
        <button
          onClick={onToggleTheme}
          title={theme === 'dark' ? 'Switch to Light version' : 'Switch to Dark version'}
          style={{
            width: '32px',
            height: '32px',
            borderRadius: '50%',
            backgroundColor: 'var(--pill-bg)',
            border: '1px solid var(--border-subtle)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--text-secondary)',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = 'var(--pill-hover)'
            e.currentTarget.style.color = 'var(--text-primary)'
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = 'var(--pill-bg)'
            e.currentTarget.style.color = 'var(--text-secondary)'
          }}
        >
          {theme === 'dark' ? (
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="5"></circle>
              <line x1="12" y1="1" x2="12" y2="3"></line>
              <line x1="12" y1="21" x2="12" y2="23"></line>
              <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
              <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
              <line x1="1" y1="12" x2="3" y2="12"></line>
              <line x1="21" y1="12" x2="23" y2="12"></line>
              <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
              <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
            </svg>
          ) : (
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
            </svg>
          )}
        </button>

        {/* Multi-Agent Policy Engine Status Pill (No login/user details) */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            backgroundColor: 'var(--pill-bg)',
            border: '1px solid var(--border-subtle)',
            borderRadius: '9999px',
            padding: '5px 12px',
            fontSize: '11.5px',
            color: 'var(--text-secondary)',
            fontWeight: 500,
          }}
        >
          <span
            style={{
              width: '6px',
              height: '6px',
              borderRadius: '50%',
              backgroundColor: '#10b981',
              boxShadow: '0 0 8px #10b981',
            }}
          ></span>
          <span>TruthGuard Engine</span>
          <span
            style={{
              backgroundColor: 'var(--pill-active)',
              color: '#10b981',
              borderRadius: '9999px',
              padding: '1px 6px',
              fontSize: '10.5px',
              fontWeight: 700,
            }}
          >
            ACTIVE
          </span>
        </div>
      </div>
    </header>
  )
}
