/**
 * UploadArea.jsx
 * --------------
 * File upload dropzone and progress display for the Knowledge Base page.
 *
 * States:
 *   idle        → waiting for user to select or drop a file
 *   selected    → user has picked a file, ready to upload
 *   uploading   → file is being sent to FastAPI
 *   processing  → FastAPI is extracting text and chunking
 *   success     → processing complete
 *   error       → something went wrong (message shown)
 *
 * Note: We only have two real network states: "uploading" (sending bytes)
 * and "processing" (waiting for the response). The distinction is real —
 * the request is open the whole time FastAPI processes it.
 */

import { useState, useRef, useCallback } from 'react'
import { uploadDocument } from '../../services/api'

const ACCEPTED_TYPES = ['.pdf', '.txt']
const MAX_MB = 10

function UploadArea({ onUploadSuccess }) {
  const [uploadState, setUploadState] = useState('idle') // idle | selected | uploading | processing | success | error
  const [selectedFile, setSelectedFile] = useState(null)
  const [errorMessage, setErrorMessage] = useState('')
  const [isDragOver, setIsDragOver] = useState(false)
  const fileInputRef = useRef(null)

  // ── File validation (client-side quick check) ──────────────────────────────
  function validateFile(file) {
    const ext = '.' + file.name.split('.').pop().toLowerCase()
    if (!ACCEPTED_TYPES.includes(ext)) {
      return `Unsupported file type "${ext}". Only PDF and TXT files are accepted.`
    }
    if (file.size > MAX_MB * 1024 * 1024) {
      return `File is too large (${(file.size / 1024 / 1024).toFixed(1)} MB). Maximum is ${MAX_MB} MB.`
    }
    if (file.size === 0) {
      return 'The file is empty.'
    }
    return null
  }

  function handleFileSelect(file) {
    setErrorMessage('')
    const error = validateFile(file)
    if (error) {
      setUploadState('error')
      setErrorMessage(error)
      setSelectedFile(null)
      return
    }
    setSelectedFile(file)
    setUploadState('selected')
  }

  // ── Drag and Drop handlers ─────────────────────────────────────────────────
  const handleDragOver = useCallback((e) => {
    e.preventDefault()
    setIsDragOver(true)
  }, [])

  const handleDragLeave = useCallback((e) => {
    e.preventDefault()
    setIsDragOver(false)
  }, [])

  const handleDrop = useCallback((e) => {
    e.preventDefault()
    setIsDragOver(false)
    const file = e.dataTransfer.files[0]
    if (file) handleFileSelect(file)
  }, [])

  // ── Upload handler ─────────────────────────────────────────────────────────
  async function handleUpload() {
    if (!selectedFile) return

    try {
      // Phase 1 of the request: bytes are being transferred
      setUploadState('uploading')

      // After a short moment the bytes are sent; FastAPI is now processing
      // We use a small timer to transition to "processing" state visually
      // so the user knows the backend is working (not just loading)
      const processingTimer = setTimeout(() => {
        setUploadState('processing')
      }, 800)

      const result = await uploadDocument(selectedFile)

      clearTimeout(processingTimer)
      setUploadState('success')

      // Notify the parent component that a new document is ready
      if (onUploadSuccess) {
        onUploadSuccess(result)
      }

      // Reset after 2 seconds
      setTimeout(() => {
        setUploadState('idle')
        setSelectedFile(null)
      }, 2000)
    } catch (err) {
      setUploadState('error')
      setErrorMessage(err.message || 'Upload failed. Please try again.')
    }
  }

  function handleReset() {
    setUploadState('idle')
    setSelectedFile(null)
    setErrorMessage('')
    if (fileInputRef.current) fileInputRef.current.value = ''
  }

  // ── Render ─────────────────────────────────────────────────────────────────
  const isActive = uploadState !== 'uploading' && uploadState !== 'processing'

  return (
    <div style={{ marginBottom: 32 }}>
      {/* Section label */}
      <div style={{
        fontSize: 11,
        fontWeight: 600,
        color: 'var(--color-text-muted)',
        textTransform: 'uppercase',
        letterSpacing: '0.08em',
        marginBottom: 12,
      }}>
        Upload Document
      </div>

      {/* Drop zone */}
      <div
        id="upload-dropzone"
        onClick={() => isActive && fileInputRef.current?.click()}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        style={{
          border: `1px ${isDragOver ? 'solid' : 'dashed'} ${
            isDragOver
              ? 'var(--color-accent)'
              : uploadState === 'error'
              ? 'var(--color-error)'
              : uploadState === 'success'
              ? 'var(--color-success)'
              : 'var(--color-border)'
          }`,
          borderRadius: 6,
          padding: '28px 24px',
          background: isDragOver
            ? 'var(--color-accent-muted)'
            : 'var(--color-bg-elevated)',
          cursor: isActive ? 'pointer' : 'default',
          transition: 'border-color 0.15s, background 0.15s',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: 10,
        }}
      >
        {/* State-dependent content */}
        {uploadState === 'idle' && (
          <>
            <div style={{ fontSize: 22, opacity: 0.5 }}>⬆</div>
            <div style={{ fontSize: 13, color: 'var(--color-text-secondary)', textAlign: 'center' }}>
              Drag a PDF or TXT file here, or <span style={{ color: 'var(--color-accent)' }}>click to browse</span>
            </div>
            <div style={{ fontSize: 11, color: 'var(--color-text-muted)' }}>
              PDF and TXT · max {MAX_MB} MB
            </div>
          </>
        )}

        {uploadState === 'selected' && (
          <>
            <div style={{ fontSize: 13, color: 'var(--color-text-primary)', fontWeight: 500 }}>
              {selectedFile?.name}
            </div>
            <div style={{ fontSize: 11, color: 'var(--color-text-muted)' }}>
              {(selectedFile?.size / 1024).toFixed(0)} KB
            </div>
            <div style={{ display: 'flex', gap: 8, marginTop: 4 }}>
              <button
                id="upload-btn"
                onClick={(e) => { e.stopPropagation(); handleUpload() }}
                style={btnStyle('primary')}
              >
                Upload & Process
              </button>
              <button
                onClick={(e) => { e.stopPropagation(); handleReset() }}
                style={btnStyle('secondary')}
              >
                Cancel
              </button>
            </div>
          </>
        )}

        {(uploadState === 'uploading' || uploadState === 'processing') && (
          <>
            <StatusDot />
            <div style={{ fontSize: 13, color: 'var(--color-text-secondary)', fontWeight: 500 }}>
              {uploadState === 'uploading' ? 'Uploading...' : 'Processing — extracting text and creating chunks...'}
            </div>
            <div style={{ fontSize: 11, color: 'var(--color-text-muted)' }}>
              {selectedFile?.name}
            </div>
          </>
        )}

        {uploadState === 'success' && (
          <>
            <div style={{ fontSize: 18, color: 'var(--color-success)' }}>✓</div>
            <div style={{ fontSize: 13, color: 'var(--color-success)', fontWeight: 500 }}>
              Processing complete
            </div>
          </>
        )}

        {uploadState === 'error' && (
          <>
            <div style={{ fontSize: 13, color: 'var(--color-error)', fontWeight: 500, textAlign: 'center' }}>
              {errorMessage}
            </div>
            <button
              onClick={(e) => { e.stopPropagation(); handleReset() }}
              style={{ ...btnStyle('secondary'), marginTop: 4 }}
            >
              Try again
            </button>
          </>
        )}
      </div>

      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,.txt"
        style={{ display: 'none' }}
        onChange={(e) => {
          const file = e.target.files?.[0]
          if (file) handleFileSelect(file)
        }}
      />
    </div>
  )
}

// ── Animated processing indicator ─────────────────────────────────────────────
function StatusDot() {
  return (
    <div style={{ display: 'flex', gap: 4, alignItems: 'center' }}>
      {[0, 1, 2].map((i) => (
        <div
          key={i}
          style={{
            width: 6,
            height: 6,
            borderRadius: '50%',
            background: 'var(--color-accent)',
            animation: `pulse 1.2s ease-in-out ${i * 0.2}s infinite`,
          }}
        />
      ))}
      <style>{`
        @keyframes pulse {
          0%, 80%, 100% { opacity: 0.2; transform: scale(0.8); }
          40% { opacity: 1; transform: scale(1); }
        }
      `}</style>
    </div>
  )
}

// ── Button style helper ────────────────────────────────────────────────────────
function btnStyle(variant) {
  return {
    padding: '7px 16px',
    borderRadius: 5,
    border: 'none',
    cursor: 'pointer',
    fontSize: 12,
    fontWeight: 600,
    fontFamily: 'inherit',
    background: variant === 'primary' ? 'var(--color-accent)' : 'var(--color-bg-overlay)',
    color: variant === 'primary' ? '#fff' : 'var(--color-text-secondary)',
    transition: 'opacity 0.15s',
  }
}

export default UploadArea
