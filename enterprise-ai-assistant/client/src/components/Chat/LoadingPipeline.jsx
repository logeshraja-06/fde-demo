import React from 'react'

/**
 * LoadingPipeline.jsx
 * -------------------
 * Professional processing state while a chat request is executing.
 *
 * Visually represents the active pipeline progression through the 5 stages:
 *   1. Validating input
 *   2. Searching knowledge base
 *   3. Checking evidence
 *   4. Generating answer
 *   5. Validating output
 */
export default function LoadingPipeline({ activeStep = 1 }) {
  const steps = [
    { id: 1, label: 'Validating input (length & injection scan)' },
    { id: 2, label: 'Searching knowledge base (ChromaDB vector search)' },
    { id: 3, label: 'Checking evidence (similarity threshold test)' },
    { id: 4, label: 'Generating answer (Gemini LLM grounded inference)' },
    { id: 5, label: 'Validating output (non-empty & safety audit)' },
  ]

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'flex-start',
        gap: '12px',
        maxWidth: '85%',
        animation: 'fadeIn 0.2s ease',
      }}
    >
      {/* Avatar Icon */}
      <div
        style={{
          width: '32px',
          height: '32px',
          borderRadius: '50%',
          background: 'rgba(99, 102, 241, 0.2)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#818cf8',
          fontSize: '13px',
          fontWeight: 700,
          flexShrink: 0,
          marginTop: '2px',
        }}
      >
        🛡️
      </div>

      {/* Main card */}
      <div
        style={{
          background: 'var(--color-bg-surface)',
          border: '1px solid var(--color-border)',
          borderRadius: '12px',
          padding: '16px 20px',
          width: '100%',
          boxShadow: '0 2px 10px rgba(0, 0, 0, 0.15)',
        }}
      >
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            fontSize: '12px',
            fontWeight: 700,
            color: '#818cf8',
            textTransform: 'uppercase',
            letterSpacing: '0.06em',
            marginBottom: '12px',
          }}
        >
          <span
            style={{
              display: 'inline-block',
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              background: '#818cf8',
              boxShadow: '0 0 8px #818cf8',
            }}
          />
          <span>Processing request through pipeline...</span>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '12px' }}>
          {steps.map((step) => {
            const isCompleted = activeStep > step.id
            const isCurrent = activeStep === step.id
            const isPending = activeStep < step.id

            let icon = '○'
            let color = 'var(--color-text-muted)'
            let fontWeight = 400

            if (isCompleted) {
              icon = '✓'
              color = '#10b981'
              fontWeight = 600
            } else if (isCurrent) {
              icon = '●'
              color = '#38bdf8'
              fontWeight = 600
            }

            return (
              <div
                key={step.id}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '10px',
                  color,
                  fontWeight,
                  transition: 'color 0.2s ease',
                }}
              >
                <span
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    width: '14px',
                    fontSize: '12px',
                    fontWeight: 700,
                  }}
                >
                  {icon}
                </span>
                <span>{step.label}</span>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
