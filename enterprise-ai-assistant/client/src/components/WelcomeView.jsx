/**
 * WelcomeView.jsx
 * ---------------
 * The main content shown when the user opens the app.
 *
 * This is a Phase 1 placeholder — it shows what the application
 * WILL do, without implementing any AI functionality yet.
 *
 * Think of it as the "empty state" of the AI Assistant page.
 * In Phase 2, clicking "Start Conversation" will open a real chat.
 */

// These are descriptions of the future AI pipeline stages.
// We display them to explain the system architecture to the user.
const PIPELINE_STEPS = [
  { step: '01', label: 'Document Ingestion',   desc: 'Upload HR policies, handbooks, and guidelines' },
  { step: '02', label: 'Text Extraction',       desc: 'Parse PDFs and documents into raw text' },
  { step: '03', label: 'Chunking',              desc: 'Split text into semantic, retrievable pieces' },
  { step: '04', label: 'Embeddings',            desc: 'Convert text chunks into numerical vectors' },
  { step: '05', label: 'Vector Storage',        desc: 'Store embeddings in a searchable vector database' },
  { step: '06', label: 'Retrieval (RAG)',       desc: 'Find relevant chunks for each user question' },
  { step: '07', label: 'LLM Generation',        desc: 'Generate a grounded answer using retrieved context' },
  { step: '08', label: 'Guardrails',            desc: 'Filter responses for safety and relevance' },
]

function WelcomeView({ onStartConversation }) {
  return (
    <div
      style={{
        flex: 1,
        overflowY: 'auto',
        padding: '48px 40px',
        maxWidth: 820,
        margin: '0 auto',
        width: '100%',
      }}
    >
      {/* ── Hero Section ── */}
      <div style={{ marginBottom: 56 }}>
        {/* Phase badge */}
        <div
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 6,
            background: 'var(--color-accent-muted)',
            color: 'var(--color-accent-hover)',
            fontSize: 11,
            fontWeight: 600,
            textTransform: 'uppercase',
            letterSpacing: '0.08em',
            padding: '4px 10px',
            borderRadius: 4,
            marginBottom: 24,
          }}
        >
          Phase 1 · Foundation
        </div>

        <h2
          style={{
            fontSize: 32,
            fontWeight: 700,
            color: 'var(--color-text-primary)',
            letterSpacing: '-0.03em',
            lineHeight: 1.2,
            marginBottom: 14,
          }}
        >
          Enterprise Knowledge AI
        </h2>

        <p
          style={{
            fontSize: 15,
            color: 'var(--color-text-secondary)',
            lineHeight: 1.7,
            maxWidth: 520,
            marginBottom: 32,
          }}
        >
          An AI assistant that answers employee questions using your internal documents —
          HR policies, handbooks, expense guidelines, and more.
          The AI pipeline is not implemented yet. We are building the foundation first.
        </p>

        {/* Start Conversation button */}
        <button
          id="start-conversation-btn"
          onClick={onStartConversation}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 8,
            background: 'var(--color-accent)',
            color: '#fff',
            border: 'none',
            padding: '11px 22px',
            borderRadius: 7,
            fontSize: 14,
            fontWeight: 600,
            cursor: 'pointer',
            fontFamily: 'inherit',
            letterSpacing: '-0.01em',
            transition: 'background 0.15s ease, transform 0.1s ease',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = 'var(--color-accent-hover)'
            e.currentTarget.style.transform = 'translateY(-1px)'
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = 'var(--color-accent)'
            e.currentTarget.style.transform = 'translateY(0)'
          }}
        >
          Start Conversation
          <span style={{ fontSize: 12 }}>→</span>
        </button>
      </div>

      {/* ── Divider ── */}
      <div
        style={{
          height: 1,
          background: 'var(--color-border)',
          marginBottom: 40,
        }}
      />

      {/* ── AI Pipeline Architecture Section ── */}
      <div>
        <div
          style={{
            fontSize: 11,
            fontWeight: 600,
            color: 'var(--color-text-muted)',
            textTransform: 'uppercase',
            letterSpacing: '0.08em',
            marginBottom: 20,
          }}
        >
          Future Architecture · Not Implemented Yet
        </div>

        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
            gap: 1,
            background: 'var(--color-border)',
            border: '1px solid var(--color-border)',
            borderRadius: 8,
            overflow: 'hidden',
          }}
        >
          {PIPELINE_STEPS.map((item, index) => (
            <div
              key={item.step}
              style={{
                background: 'var(--color-bg-surface)',
                padding: '18px 20px',
                display: 'flex',
                gap: 14,
                alignItems: 'flex-start',
                opacity: 0.7,
              }}
            >
              {/* Step number */}
              <div
                style={{
                  fontSize: 10,
                  fontWeight: 700,
                  color: 'var(--color-accent)',
                  fontFamily: 'monospace',
                  marginTop: 2,
                  flexShrink: 0,
                  opacity: 0.8,
                }}
              >
                {item.step}
              </div>
              <div>
                <div
                  style={{
                    fontSize: 13,
                    fontWeight: 500,
                    color: 'var(--color-text-primary)',
                    marginBottom: 3,
                  }}
                >
                  {item.label}
                </div>
                <div style={{ fontSize: 12, color: 'var(--color-text-muted)', lineHeight: 1.5 }}>
                  {item.desc}
                </div>
              </div>
            </div>
          ))}
        </div>

        <p
          style={{
            marginTop: 16,
            fontSize: 12,
            color: 'var(--color-text-muted)',
            lineHeight: 1.6,
          }}
        >
          These 8 stages will be built incrementally in future phases.
          Phase 1 only establishes the project structure and frontend–backend connection.
        </p>
      </div>
    </div>
  )
}

export default WelcomeView
