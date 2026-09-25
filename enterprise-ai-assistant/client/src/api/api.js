/**
 * client/src/api/api.js
 * ---------------------
 * Centralized HTTP Client for Phase 7 Enterprise AI Assistant.
 *
 * Provides:
 * - Centralized BASE_URL configuration
 * - Automatic AbortController timeout handling (prevents UI hanging forever)
 * - Safe JSON parsing and HTTP error extraction
 * - Friendly network error reporting when backend is unavailable
 * - Clean FormData handling for multipart uploads
 */

export const BASE_URL = import.meta.env?.VITE_API_URL !== undefined
  ? import.meta.env.VITE_API_URL
  : ''

// Default timeout durations in milliseconds
export const DEFAULT_TIMEOUT_MS = 15000       // 15 seconds for standard requests
export const LLM_CHAT_TIMEOUT_MS = 35000       // 35 seconds for LLM generation

/**
 * Core centralized request function with AbortController timeout handling.
 *
 * @param {string} path - URL path (e.g. '/health', '/chat')
 * @param {object} options - Standard fetch options (method, headers, body)
 * @param {number} timeoutMs - Timeout in milliseconds
 * @returns {Promise<any>} - Parsed JSON response
 */
export async function request(path, options = {}, timeoutMs = DEFAULT_TIMEOUT_MS) {
  const controller = new AbortController()
  const timeoutId = setTimeout(() => {
    controller.abort()
  }, timeoutMs)

  const isFormData = typeof FormData !== 'undefined' && options.body instanceof FormData

  const headers = {
    ...(!isFormData ? { 'Content-Type': 'application/json' } : {}),
    ...(options.headers || {}),
  }

  const fetchOptions = {
    ...options,
    headers,
    signal: controller.signal,
  }

  // Primary URL (uses Vite reverse-proxy by default for 100% reliable local networking)
  const primaryUrl = `${BASE_URL}${path}`

  try {
    let response
    try {
      response = await fetch(primaryUrl, fetchOptions)
    } catch (primaryErr) {
      // If relative proxy path failed, try direct 127.0.0.1:8000
      if (!BASE_URL && (primaryErr.name === 'TypeError' || primaryErr.code === 'ERR_CONNECTION_REFUSED')) {
        const directUrl = `http://127.0.0.1:8000${path}`
        response = await fetch(directUrl, fetchOptions)
      } else {
        throw primaryErr
      }
    }
    clearTimeout(timeoutId)

    if (!response.ok) {
      let errorMessage = `Request failed with status ${response.status}`
      let errorCode = 'INTERNAL_SERVER_ERROR'

      try {
        const errorData = await response.json()
        if (errorData?.error?.message) {
          errorMessage = errorData.error.message
          errorCode = errorData.error.code || errorCode
        } else if (errorData?.detail) {
          errorMessage = typeof errorData.detail === 'string' ? errorData.detail : JSON.stringify(errorData.detail)
        } else if (errorData?.message) {
          errorMessage = errorData.message
        }
      } catch {
        // Fallback to HTTP status text if response is not valid JSON
        if (response.statusText) {
          errorMessage = `Server error: ${response.statusText} (${response.status})`
        }
      }

      const err = new Error(errorMessage)
      err.status = response.status
      err.code = errorCode
      throw err
    }

    return await response.json()
  } catch (error) {
    clearTimeout(timeoutId)

    // Handle request timeout triggered by AbortController
    if (error.name === 'AbortError') {
      const timeoutErr = new Error('The AI service took too long to respond. Please try again.')
      timeoutErr.code = 'REQUEST_TIMEOUT'
      timeoutErr.isTimeout = true
      throw timeoutErr
    }

    // Handle connection failures (backend unreachable or down)
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      const netErr = new Error('Unable to connect to the AI service. Check whether the backend is running.')
      netErr.code = 'BACKEND_UNAVAILABLE'
      netErr.isNetworkError = true
      throw netErr
    }

    // Re-throw standardized error
    throw error
  }
}
