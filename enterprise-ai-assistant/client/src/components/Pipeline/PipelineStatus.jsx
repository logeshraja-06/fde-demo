import React, { useState } from 'react'
import PipelineStage from './PipelineStage'

/**
 * PipelineStatus.jsx
 * ------------------
 * Visualizes the 5-stage enterprise AI pipeline with real backend data:
 *   Input Guardrail
 *        ↓
 *   RAG Retrieval
 *        ↓
 *   Grounding Check
 *        ↓
 *   LLM Generation
 *        ↓
 *   Output Guardrail
 *
 * Supports states: pending, running, passed, blocked, completed, not_run, failed.
 * Maps actual backend response objects directly without fake data.
 */
export default function PipelineStatus({ pipeline, sources = [] }) {
  const [expanded, setExpanded] = useState(false)

  if (!pipeline) return null

  const inputG = pipeline.input_guardrail || { status: 'not_run' }
  const rag = pipeline.rag || { status: 'not_run' }
  const grounding = pipeline.grounding || { status: 'not_run' }
  const llm = pipeline.llm || { status: 'not_run' }
  const outputG = pipeline.output_guardrail || { status: 'not_run' }

  // Determine top-level outcome
  const isInputBlocked = inputG.status === 'blocked'
  const isGroundingBlocked = grounding.status === 'blocked'
  const isOutputBlocked = outputG.status === 'blocked'
  const isLLMFailed = llm.status === 'failed'
  const isSuccess = outputG.status === 'passed'

  let outcomeBadge = {
    label: 'PROCESSING',
    color: '#38bdf8',
    bg: 'rgba(56, 189, 248, 0.15)',
    border: 'rgba(56, 189, 248, 0.3)',
  }

  if (isInputBlocked) {
    outcomeBadge = {
      label: 'REQUEST BLOCKED',
      color: '#ef4444',
      bg: 'rgba(239, 68, 68, 0.15)',
      border: 'rgba(239, 68, 68, 0.3)',
    }
  } else if (isGroundingBlocked) {
    outcomeBadge = {
      label: 'KNOWLEDGE BASE EVIDENCE INSUFFICIENT',
      color: '#f59e0b',
      bg: 'rgba(245, 158, 11, 0.15)',
      border: 'rgba(245, 158, 11, 0.3)',
    }
  } else if (isLLMFailed) {
    outcomeBadge = {
      label: 'LLM GENERATION FAILED',
      color: '#ef4444',
      bg: 'rgba(239, 68, 68, 0.15)',
      border: 'rgba(239, 68, 68, 0.3)',
    }
  } else if (isOutputBlocked) {
    outcomeBadge = {
      label: 'OUTPUT BLOCKED',
      color: '#ef4444',
      bg: 'rgba(239, 68, 68, 0.15)',
      border: 'rgba(239, 68, 68, 0.3)',
    }
  } else if (isSuccess) {
    outcomeBadge = {
      label: 'ANSWER READY',
      color: '#10b981',
      bg: 'rgba(16, 185, 129, 0.15)',
      border: 'rgba(16, 185, 129, 0.3)',
    }
  }

  return (
    <div
      style={{
        marginTop: '16px',
        paddingTop: '12px',
        borderTop: '1px solid rgba(255, 255, 255, 0.08)',
        display: 'flex',
        flexDirection: 'column',
        gap: '10px',
      }}
    >
      {/* ── Top Outcome Header ── */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '8px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span
            style={{
              fontSize: '11px',
              fontWeight: 700,
              color: 'var(--color-text-secondary)',
              textTransform: 'uppercase',
              letterSpacing: '0.06em',
            }}
          >
            AI Pipeline:
          </span>
          <span
            style={{
              fontSize: '10px',
              fontWeight: 700,
              padding: '2px 8px',
              borderRadius: '9999px',
              color: outcomeBadge.color,
              background: outcomeBadge.bg,
              border: `1px solid ${outcomeBadge.border}`,
              letterSpacing: '0.04em',
            }}
          >
            {outcomeBadge.label}
          </span>
        </div>

        {/* Toggle details */}
        <button
          onClick={() => setExpanded(!expanded)}
          style={{
            background: 'var(--color-bg-base)',
            border: '1px solid var(--color-border)',
            borderRadius: '4px',
            color: '#818cf8',
            fontSize: '11px',
            fontWeight: 600,
            cursor: 'pointer',
            padding: '3px 8px',
            transition: 'background 0.15s ease',
          }}
        >
          {expanded ? '▼ Hide pipeline details' : '▶ Inspect pipeline evidence'}
        </button>
      </div>

      {/* ── Compact Stage Flow Bar (Horizontal/Vertical Grid) ── */}
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '2px',
          background: 'var(--color-bg-base)',
          border: '1px solid var(--color-border)',
          borderRadius: '8px',
          padding: '12px',
        }}
      >
        {/* Stage 1: Input Guardrail */}
        <PipelineStage
          name="Input Guardrail"
          stageKey="input"
          status={inputG.status}
          reason={isInputBlocked ? inputG.reason : null}
          checks={expanded ? inputG.checks : null}
        />

        {/* Stage 2: RAG Retrieval */}
        <PipelineStage
          name="RAG Retrieval"
          stageKey="rag"
          status={rag.status}
          subtitle={
            rag.status === 'passed' || rag.status === 'completed'
              ? `${rag.results_count || sources.length} relevant chunk(s) found`
              : null
          }
        />

        {/* Stage 3: Grounding Check */}
        <PipelineStage
          name="Grounding Check"
          stageKey="grounding"
          status={grounding.status}
          subtitle={
            grounding.score !== undefined && grounding.score !== null
              ? `Score: ${grounding.score} (Cutoff: ${grounding.threshold || 0.35})`
              : null
          }
          reason={isGroundingBlocked ? grounding.reason : null}
        />

        {/* Stage 4: LLM Generation */}
        <PipelineStage
          name="LLM Generation"
          stageKey="llm"
          status={llm.status}
          subtitle={llm.model ? `Model: ${llm.model}` : null}
        />

        {/* Stage 5: Output Guardrail */}
        <PipelineStage
          name="Output Guardrail"
          stageKey="output"
          status={outputG.status}
          reason={isOutputBlocked ? outputG.reason : null}
          checks={expanded ? outputG.checks : null}
          isLast={true}
        />
      </div>

      {/* Specific notice for Insufficient Evidence */}
      {isGroundingBlocked && (
        <div
          style={{
            background: 'rgba(245, 158, 11, 0.08)',
            border: '1px solid rgba(245, 158, 11, 0.25)',
            borderRadius: '6px',
            padding: '10px 14px',
            fontSize: '12px',
            color: '#fbbf24',
            display: 'flex',
            flexDirection: 'column',
            gap: '2px',
          }}
        >
          <div style={{ fontWeight: 600 }}>Knowledge Base Evidence Insufficient</div>
          <div style={{ color: 'var(--color-text-secondary)', fontSize: '11px' }}>
            The system could not find enough relevant information in the organization&apos;s knowledge base to answer this question.
          </div>
        </div>
      )}

      {/* Specific notice for LLM Failure (Section 14) */}
      {isLLMFailed && (
        <div
          style={{
            background: 'rgba(239, 68, 68, 0.08)',
            border: '1px solid rgba(239, 68, 68, 0.25)',
            borderRadius: '6px',
            padding: '10px 14px',
            fontSize: '12px',
            color: '#f87171',
            display: 'flex',
            flexDirection: 'column',
            gap: '2px',
          }}
        >
          <div style={{ fontWeight: 600 }}>The AI generation service is currently unavailable.</div>
          <div style={{ color: 'var(--color-text-secondary)', fontSize: '11px' }}>
            {llm.reason || 'An issue occurred during model inference. The request has been safely halted.'}
          </div>
        </div>
      )}

      {/* Specific notice for Blocked Input */}
      {isInputBlocked && (
        <div
          style={{
            background: 'rgba(239, 68, 68, 0.08)',
            border: '1px solid rgba(239, 68, 68, 0.25)',
            borderRadius: '6px',
            padding: '10px 14px',
            fontSize: '12px',
            color: '#f87171',
            display: 'flex',
            flexDirection: 'column',
            gap: '2px',
          }}
        >
          <div style={{ fontWeight: 600 }}>Request blocked</div>
          <div style={{ color: 'var(--color-text-secondary)', fontSize: '11px' }}>
            <strong>Reason:</strong> {inputG.reason || 'Potential prompt injection detected'}
          </div>
        </div>
      )}
    </div>
  )
}
