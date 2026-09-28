/**
 * client/src/api/chatApi.js
 * -------------------------
 * Chat and Guardrail API endpoints.
 */

import { request, LLM_CHAT_TIMEOUT_MS } from './api'

/**
 * Send user question through the 5-layer RAG & Guardrail pipeline.
 *
 * @param {string} message - User question or test injection payload
 * @param {number} topK - Number of top chunks to retrieve
 * @param {number|null} threshold - Cosine similarity cutoff
 * @returns {Promise<object>}
 */
export async function sendChatMessage(message, topK = 4, threshold = null, domain = null) {
  const payload = {
    message: message !== undefined && message !== null ? message : '',
    top_k: Number(topK),
  }
  if (threshold !== null && threshold !== undefined) {
    payload.threshold = Number(threshold)
  }
  if (domain && domain.toUpperCase() !== 'ALL') {
    payload.domain = domain
  }

  return request('/chat', {
    method: 'POST',
    body: JSON.stringify(payload),
  }, LLM_CHAT_TIMEOUT_MS)
}

/**
 * Get Chat & Guardrail pipeline configuration status.
 * @returns {Promise<object>}
 */
export async function getChatStatus() {
  return request('/chat/status')
}
