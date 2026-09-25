/**
 * client/src/api/documentsApi.js
 * ------------------------------
 * Document Ingestion, Details, and Deletion API endpoints.
 */

import { request } from './api'

/**
 * Upload a document file (PDF or TXT) to the backend for processing and indexing.
 *
 * @param {File} file - Browser File object
 * @returns {Promise<object>} - Processed document metadata
 */
export async function uploadDocument(file) {
  const formData = new FormData()
  formData.append('file', file)

  return request('/api/documents/upload', {
    method: 'POST',
    body: formData,
  })
}

/**
 * Fetch all processed and indexed documents (metadata only).
 * @returns {Promise<{documents: Array, count: number}>}
 */
export async function getDocuments() {
  return request('/api/documents')
}

/**
 * Fetch full document detail including all chunks by ID.
 * @param {string} documentId
 * @returns {Promise<object>}
 */
export async function getDocument(documentId) {
  return request(`/api/documents/${documentId}`)
}

/**
 * Delete a document by ID (removes source file, processed JSON, and Chroma vectors).
 * @param {string} documentId
 * @returns {Promise<{message: string}>}
 */
export async function deleteDocument(documentId) {
  return request(`/api/documents/${documentId}`, {
    method: 'DELETE',
  })
}
