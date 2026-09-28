/**
 * client/src/api/ragApi.js
 * ------------------------
 * RAG Semantic Retrieval & Vector Store statistics endpoints.
 */

import { request } from './api'

/**
 * Search the knowledge base for chunks semantically relevant to a query.
 *
 * @param {string} query - Natural language search phrase
 * @param {number} topK - Number of top chunks to retrieve
 * @param {number} threshold - Minimum cosine similarity score required
 * @returns {Promise<object>}
 */
export async function searchKnowledgeBase(query, topK = 3, threshold = 0.35, domain = null) {
  const body = {
    query: (query || '').trim(),
    top_k: Number(topK),
    threshold: Number(threshold),
  }
  if (domain && domain.toUpperCase() !== 'ALL') {
    body.domain = domain
  }

  return request('/rag/search', {
    method: 'POST',
    body: JSON.stringify(body),
  })
}

/**
 * Get RAG vector database & embedding model metadata.
 * @returns {Promise<object>}
 */
export async function getRagStats() {
  return request('/rag/stats')
}
