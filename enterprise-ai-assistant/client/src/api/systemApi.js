/**
 * client/src/api/systemApi.js
 * ---------------------------
 * System Health Check & Telemetry Analytics API endpoints.
 */

import { request } from './api'

/**
 * Check backend service health and dependency states (vector store, embeddings, LLM).
 * @returns {Promise<object>}
 */
export async function checkBackendHealth() {
  return request('/health', { method: 'GET' }, 5000)
}

/**
 * Get aggregated real-time execution metrics and recent activity audit trail.
 * @returns {Promise<object>}
 */
export async function getAnalytics() {
  return request('/analytics')
}
