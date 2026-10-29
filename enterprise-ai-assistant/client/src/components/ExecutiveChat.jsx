import React, { useState, useEffect, useRef } from 'react'
import { sendChatMessage } from '../services/api'

export default function ExecutiveChat({
  customerConfig = {},
  initialPrompt = '',
  onClearInitialPrompt = () => { },
  messages = [],
  setMessages = () => { },
  theme = 'dark',
}) {
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef(null)
  const textareaRef = useRef(null)

  // Handle external prompts
  useEffect(() => {
    if (initialPrompt) {
      handleSend(initialPrompt)
      onClearInitialPrompt()
    }
  }, [initialPrompt])

  // Scroll to bottom
  useEffect(() => {
    if (messages.length > 0) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages, loading])

  const handleInputChange = (e) => {
    setInput(e.target.value)
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleSend = async (customText = null) => {
    const textToSend = customText !== null ? customText : input
    if (!textToSend || !textToSend.trim() || loading) return

    const userMessage = {
      id: `user-${Date.now()}`,
      sender: 'user',
      text: textToSend.trim(),
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    }

    setMessages((prev) => [...prev, userMessage])
    setInput('')
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
    }
    setLoading(true)

    try {
      const topK = customerConfig.rag_top_k || 3
      const threshold = customerConfig.grounding_threshold || 0.70
      // Send query to Multi-Agent RAG Policy backend
      const response = await sendChatMessage(textToSend.trim(), topK, threshold, 'ALL')

      const aiMessage = {
        id: `ai-${Date.now()}`,
        sender: 'ai',
        text: response.answer || 'I have analyzed our corporate documentation. Here are the policy findings.',
        sources: response.sources || [],
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      }

      setMessages((prev) => [...prev, aiMessage])
    } catch (err) {
      const errorAiMessage = {
        id: `ai-err-${Date.now()}`,
        sender: 'ai',
        text: err.message || 'Unable to connect to the policy analysis service. Please ensure the backend is running.',
        isError: true,
        sources: [],
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      }
      setMessages((prev) => [...prev, errorAiMessage])
    } finally {
      setLoading(false)
    }
  }

  const handleAttachment = () => {
    const inputEl = document.createElement('input')
    inputEl.type = 'file'
    inputEl.accept = '.pdf,.txt,.md,.docx'
    inputEl.onchange = (e) => {
      const file = e.target.files?.[0]
      if (file) {
        setInput((prev) => (prev ? `${prev} [Referencing policy document: ${file.name}]` : `[Referencing policy document: ${file.name}] `))
      }
    }
    inputEl.click()
  }

  const hasMessages = messages.length > 0

  return (
    <div
      style={{
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        overflow: 'hidden',
        position: 'relative',
        zIndex: 1,
      }}
    >
      {/* Scrollable Container */}
      <div
        style={{
          flex: 1,
          overflowY: 'auto',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: hasMessages ? 'flex-start' : 'center',
          padding: hasMessages ? '20px 24px 130px 24px' : '20px 24px 40px 24px',
        }}
      >
        {!hasMessages ? (
          /* ── Welcome Stage: Dedicated Multi-Agent Policy Analyzer ── */
          <div
            style={{
              width: '100%',
              maxWidth: '760px',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              textAlign: 'center',
            }}
          >
            {/* Crimson Fluid Swirling Orb */}
            <div className="crimson-orb-container">
              <div className="crimson-orb-glow"></div>
              <img
                src="/crimson_orb.jpg"
                alt="Policy Intelligence Orb"
                className="crimson-orb-img"
                onError={(e) => {
                  e.target.style.display = 'none'
                }}
              />
            </div>

            {/* TruthGuard Headlines */}
            <h1
              style={{
                fontSize: '44px',
                fontWeight: 600,
                letterSpacing: '-0.03em',
                lineHeight: 1.15,
                color: 'var(--text-primary)',
                marginBottom: '12px',
              }}
            >
              TruthGuard
            </h1>
            <div
              style={{
                fontSize: '15px',
                color: 'var(--text-secondary)',
                marginBottom: '32px',
                maxWidth: '620px',
                lineHeight: 1.5,
              }}
            >
              Analyze policies and verify truth at the speed of AI
            </div>

            {/* ── Central Dual-Tone Gradient Border Input Card ── */}
            <div style={{ width: '100%', maxWidth: '720px' }}>
              <div className="gradient-border-box">
                <div className="gradient-border-inner">
                  {/* Textarea */}
                  <textarea
                    ref={textareaRef}
                    value={input}
                    onChange={handleInputChange}
                    onKeyDown={handleKeyDown}
                    placeholder="Ask any policy, guideline, or compliance question..."
                    rows={1}
                    style={{
                      width: '100%',
                      background: 'transparent',
                      border: 'none',
                      color: 'var(--text-primary)',
                      fontSize: '14.5px',
                      lineHeight: 1.5,
                      resize: 'none',
                      outline: 'none',
                      minHeight: '36px',
                      maxHeight: '120px',
                    }}
                  />

                  {/* Bottom Toolbar Controls (Voice, Normal, Deep Think, and Budget Cards Removed) */}
                  <div
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      paddingTop: '6px',
                    }}
                  >
                    {/* Left: Attachment Button */}
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <button
                        onClick={handleAttachment}
                        title="Attach policy document"
                        style={{
                          width: '28px',
                          height: '28px',
                          borderRadius: '6px',
                          backgroundColor: 'var(--pill-bg)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          color: 'var(--text-secondary)',
                        }}
                      >
                        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                          <line x1="12" y1="5" x2="12" y2="19"></line>
                          <line x1="5" y1="12" x2="19" y2="12"></line>
                        </svg>
                      </button>
                      <span style={{ fontSize: '11.5px', color: 'var(--text-muted)' }}>
                        Attach Document
                      </span>
                    </div>

                    {/* Right: Policy Engine Status & Orange/Coral Send Button */}
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <span style={{ fontSize: '11.5px', color: 'var(--text-muted)' }}>
                        🛡️ TruthGuard Verified
                      </span>

                      {/* Coral Send Button */}
                      <button
                        onClick={() => handleSend()}
                        disabled={loading || !input.trim()}
                        style={{
                          width: '32px',
                          height: '32px',
                          borderRadius: '8px',
                          backgroundColor: input.trim() ? '#ea580c' : 'rgba(234, 88, 12, 0.4)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          color: '#ffffff',
                          cursor: input.trim() && !loading ? 'pointer' : 'default',
                          transition: 'background-color 0.15s ease',
                        }}
                      >
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                          <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"></path>
                        </svg>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ) : (
          /* ── Clean Conversation Thread (No login details, clean multi-agent answers) ── */
          <div
            style={{
              width: '100%',
              maxWidth: '760px',
              display: 'flex',
              flexDirection: 'column',
              gap: '20px',
            }}
          >
            {messages.map((msg) => (
              <div
                key={msg.id}
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: msg.sender === 'user' ? 'flex-end' : 'flex-start',
                }}
              >
                <div
                  style={{
                    maxWidth: msg.sender === 'user' ? '76%' : '88%',
                    display: 'flex',
                    gap: '12px',
                    flexDirection: msg.sender === 'user' ? 'row-reverse' : 'row',
                  }}
                >
                  {/* Sender Badge / Icon (No personal login or avatar photos) */}
                  <div
                    style={{
                      width: '32px',
                      height: '32px',
                      borderRadius: '50%',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      flexShrink: 0,
                      backgroundColor: msg.sender === 'user' ? 'var(--pill-active)' : '#ea580c',
                      color: '#ffffff',
                      fontSize: '13px',
                      fontWeight: 700,
                      marginTop: '2px',
                    }}
                  >
                    {msg.sender === 'user' ? 'U' : '🛡️'}
                  </div>

                  {/* Message Bubble */}
                  <div
                    style={{
                      backgroundColor: msg.sender === 'user' ? 'var(--user-bubble-bg)' : 'var(--ai-bubble-bg)',
                      border: msg.sender === 'user' ? 'none' : '1px solid var(--ai-bubble-border)',
                      color: msg.sender === 'user' ? 'var(--user-bubble-text)' : 'var(--text-primary)',
                      borderRadius: msg.sender === 'user' ? '18px 18px 4px 18px' : '18px 18px 18px 4px',
                      padding: '14px 18px',
                      fontSize: '14.5px',
                      lineHeight: 1.6,
                      whiteSpace: 'pre-wrap',
                      wordBreak: 'break-word',
                      boxShadow: '0 4px 20px rgba(0, 0, 0, 0.15)',
                    }}
                  >
                    {msg.text}

                    {/* Verified Source Citations */}
                    {msg.sources && msg.sources.length > 0 && (
                      <div
                        style={{
                          marginTop: '12px',
                          paddingTop: '8px',
                          borderTop: '1px solid var(--border-subtle)',
                          display: 'flex',
                          flexWrap: 'wrap',
                          gap: '6px',
                          alignItems: 'center',
                        }}
                      >
                        <span style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 600 }}>
                          Verified Policy Sources:
                        </span>
                        {msg.sources.map((src, i) => (
                          <span
                            key={i}
                            style={{
                              fontSize: '11px',
                              backgroundColor: 'var(--pill-bg)',
                              border: '1px solid var(--border-subtle)',
                              borderRadius: '6px',
                              padding: '2px 8px',
                              color: 'var(--text-secondary)',
                            }}
                          >
                            📄 {src.filename || src.title || `Policy Section ${i + 1}`}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>

                <div
                  style={{
                    fontSize: '10.5px',
                    color: 'var(--text-muted)',
                    marginTop: '4px',
                    paddingLeft: '44px',
                    paddingRight: '44px',
                  }}
                >
                  {msg.timestamp}
                </div>
              </div>
            ))}

            {/* Thinking / Loading Animation */}
            {loading && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', paddingLeft: '4px' }}>
                <div
                  style={{
                    width: '28px',
                    height: '28px',
                    borderRadius: '50%',
                    backgroundColor: '#ea580c',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '12px',
                    color: '#fff',
                  }}
                >
                  🛡️
                </div>
                <div
                  style={{
                    backgroundColor: 'var(--ai-bubble-bg)',
                    border: '1px solid var(--ai-bubble-border)',
                    borderRadius: '14px',
                    padding: '10px 16px',
                    fontSize: '13px',
                    color: 'var(--text-secondary)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                  }}
                >
                  <span>TruthGuard synthesizing verified policy response</span>
                  <span style={{ display: 'inline-flex', gap: '3px' }}>
                    <span style={{ width: 4, height: 4, borderRadius: '50%', backgroundColor: 'var(--text-muted)', animation: 'pulseGlow 1s infinite' }}></span>
                    <span style={{ width: 4, height: 4, borderRadius: '50%', backgroundColor: 'var(--text-muted)', animation: 'pulseGlow 1s infinite 0.2s' }}></span>
                    <span style={{ width: 4, height: 4, borderRadius: '50%', backgroundColor: 'var(--text-muted)', animation: 'pulseGlow 1s infinite 0.4s' }}></span>
                  </span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* ── Fixed Bottom Gradient Border Input Box (when conversation active) ── */}
      {hasMessages && (
        <div
          style={{
            position: 'absolute',
            bottom: '20px',
            left: 0,
            right: 0,
            display: 'flex',
            justifyContent: 'center',
            padding: '0 24px',
            pointerEvents: 'none',
          }}
        >
          <div style={{ width: '100%', maxWidth: '760px', pointerEvents: 'auto' }}>
            <div className="gradient-border-box">
              <div className="gradient-border-inner">
                <textarea
                  ref={textareaRef}
                  value={input}
                  onChange={handleInputChange}
                  onKeyDown={handleKeyDown}
                  placeholder="Ask any policy, guideline, or compliance question..."
                  rows={1}
                  style={{
                    width: '100%',
                    background: 'transparent',
                    border: 'none',
                    color: 'var(--text-primary)',
                    fontSize: '14.5px',
                    lineHeight: 1.5,
                    resize: 'none',
                    outline: 'none',
                    minHeight: '26px',
                    maxHeight: '100px',
                  }}
                />

                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <button
                    onClick={handleAttachment}
                    style={{
                      width: '26px',
                      height: '26px',
                      borderRadius: '6px',
                      backgroundColor: 'var(--pill-bg)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: 'var(--text-secondary)',
                    }}
                  >
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                      <line x1="12" y1="5" x2="12" y2="19"></line>
                      <line x1="5" y1="12" x2="19" y2="12"></line>
                    </svg>
                  </button>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <button
                      onClick={() => handleSend()}
                      disabled={loading || !input.trim()}
                      style={{
                        width: '28px',
                        height: '28px',
                        borderRadius: '6px',
                        backgroundColor: input.trim() ? '#ea580c' : 'rgba(234, 88, 12, 0.4)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: '#ffffff',
                        cursor: input.trim() && !loading ? 'pointer' : 'default',
                      }}
                    >
                      <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"></path>
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
