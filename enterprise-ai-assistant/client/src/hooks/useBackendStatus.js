/**
 * useBackendStatus.js
 * -------------------
 * A custom React Hook that polls the FastAPI /health endpoint.
 *
 * WHAT IS A HOOK?
 * A hook is a reusable piece of logic in React that can hold state
 * and perform side effects (like network requests). By convention,
 * hooks are named with the "use" prefix.
 *
 * WHAT DOES THIS HOOK DO?
 * 1. On mount, sends a GET request to http://localhost:8000/health
 * 2. If the response is successful → status = 'connected'
 * 3. If the request fails → status = 'disconnected'
 * 4. It repeats this check every 10 seconds (so the UI stays current)
 *
 * HOW REACT CALLS THE BACKEND:
 * React (running in the browser at port 5173) uses the browser's
 * built-in `fetch()` function to make an HTTP GET request to
 * FastAPI (running on port 8000). This is the same mechanism
 * used by every website to talk to a server.
 */

import { useState, useEffect } from 'react'
import { checkBackendHealth } from '../api/systemApi'

function useBackendStatus() {
  // 'checking' | 'connected' | 'unavailable'
  const [status, setStatus] = useState('checking')

  useEffect(() => {
    // Define the function that performs the health check
    async function checkHealth() {
      try {
        const data = await checkBackendHealth()
        if (data && (data.status === 'ok' || data.status === 'degraded')) {
          setStatus('connected')
        } else {
          setStatus('unavailable')
        }
      } catch {
        setStatus('unavailable')
      }
    }

    // Run immediately when the component mounts
    checkHealth()

    // Then repeat every 10 seconds
    // This keeps the status live — if the backend goes down, the UI updates
    const intervalId = setInterval(checkHealth, 10_000)

    // Cleanup: cancel the interval when the component is unmounted
    // (avoids memory leaks)
    return () => clearInterval(intervalId)
  }, []) // Empty array = run this effect only once, on first render

  return status
}

export default useBackendStatus
