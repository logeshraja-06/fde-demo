/**
 * client/src/api/configApi.js
 * ---------------------------
 * Customer Profile and Runtime Configuration API endpoints for Phase 8.
 */

import { request } from './api'

/**
 * Fetch current customer profile, branding, and runtime configuration.
 * @returns {Promise<object>}
 */
export async function getCustomerConfig() {
  return request('/api/config')
}

/**
 * Update customer profile, branding, and runtime configuration without rewriting code.
 * @param {object} configData - Partial or full configuration fields to update
 * @returns {Promise<object>}
 */
export async function updateCustomerConfig(configData) {
  return request('/api/config', {
    method: 'POST',
    body: JSON.stringify(configData),
  })
}
