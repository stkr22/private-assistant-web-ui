// Runtime configuration loaded from window.runtimeConfig
// This file provides type-safe access to runtime configuration values
// that are injected when the container starts (or generated from .env in dev mode).

export interface RuntimeConfig {
  apiUrl: string
  oauth?: {
    authority: string
    clientId: string
    redirectUri?: string
    scope?: string
  }
}

// Extend Window interface to include runtimeConfig
declare global {
  interface Window {
    runtimeConfig?: RuntimeConfig
  }
}

/**
 * Get runtime configuration from window.runtimeConfig
 * In both development and production, config is loaded from /config.js
 * which is generated from environment variables.
 *
 * @throws {Error} If window.runtimeConfig is not available
 */
function getRuntimeConfig(): RuntimeConfig {
  if (!window.runtimeConfig) {
    throw new Error(
      "Runtime configuration not available. " +
        "Ensure config.js is generated before the application starts. " +
        "In development, run 'npm run generate-config' or 'npm run dev'.",
    )
  }

  return window.runtimeConfig
}

// Export singleton config instance
export const config = getRuntimeConfig()
