/**
 * services/api.js
 * ---------------
 * Centralized API service for the frontend.
 *
 * In Phase 7, this re-exports from the modularized client/src/api/ suite
 * while maintaining 100% backward compatibility for existing component imports.
 */

export { BASE_URL, request } from '../api/api'
export { sendChatMessage, getChatStatus } from '../api/chatApi'
export { uploadDocument, getDocuments, getDocument, deleteDocument } from '../api/documentsApi'
export { searchKnowledgeBase, getRagStats } from '../api/ragApi'
export { checkBackendHealth, getAnalytics } from '../api/systemApi'
