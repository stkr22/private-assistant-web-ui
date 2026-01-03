#!/usr/bin/env node

// Reads .env file and generates public/config.js for development
import fs from "node:fs"
import path from "node:path"
import { fileURLToPath } from "node:url"
import dotenv from "dotenv"

// ES module equivalent of __dirname
const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

// Load environment variables from .env file
dotenv.config({ path: path.join(__dirname, "..", ".env") })

// Read environment variables
const apiUrl = process.env.VITE_API_URL
const oauthAuthority = process.env.VITE_OAUTH_AUTHORITY
const oauthClientId = process.env.VITE_OAUTH_CLIENT_ID
const oauthRedirectUri = process.env.VITE_OAUTH_REDIRECT_URI
const oauthScope = process.env.VITE_OAUTH_SCOPE

// Validate required configuration
if (!apiUrl) {
  console.error("❌ ERROR: VITE_API_URL is required in .env file")
  process.exit(1)
}

// OAuth validation: both or neither
const hasAuthority = Boolean(oauthAuthority)
const hasClientId = Boolean(oauthClientId)

if (hasAuthority !== hasClientId) {
  console.error(
    "❌ ERROR: OAuth config incomplete. " +
      "Both VITE_OAUTH_AUTHORITY and VITE_OAUTH_CLIENT_ID must be set together.",
  )
  process.exit(1)
}

// Generate config.js content with same format as docker-entrypoint.sh
let configContent = `// Runtime configuration (auto-generated from .env)
// DO NOT EDIT - This file is regenerated on every dev server start
window.runtimeConfig = {
  apiUrl: "${apiUrl}",`

// Add OAuth configuration if both authority and clientId are present
if (hasAuthority && hasClientId) {
  configContent += `
  oauth: {
    authority: "${oauthAuthority}",
    clientId: "${oauthClientId}",`

  if (oauthRedirectUri) {
    configContent += `
    redirectUri: "${oauthRedirectUri}",`
  }

  if (oauthScope) {
    configContent += `
    scope: "${oauthScope}",`
  }

  configContent += `
  },`
}

configContent += `
};
`

// Write config.js to public directory
const publicDir = path.join(__dirname, "..", "public")
const outputPath = path.join(publicDir, "config.js")

// Ensure public directory exists
if (!fs.existsSync(publicDir)) {
  fs.mkdirSync(publicDir, { recursive: true })
}

fs.writeFileSync(outputPath, configContent)

console.log("✅ Generated public/config.js from .env")
console.log(`   API URL: ${apiUrl}`)
if (hasAuthority && hasClientId) {
  console.log(`   OAuth: Enabled (${oauthAuthority})`)
} else {
  console.log(`   OAuth: Disabled`)
}
