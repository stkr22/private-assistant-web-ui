import { UserManager, WebStorageStateStore } from "oidc-client-ts"

const authority = import.meta.env.VITE_OAUTH_AUTHORITY
const clientId = import.meta.env.VITE_OAUTH_CLIENT_ID
const redirectUri =
  import.meta.env.VITE_OAUTH_REDIRECT_URI ||
  `${window.location.origin}/oauth-callback`
const scope = import.meta.env.VITE_OAUTH_SCOPE || "openid email profile"

export const isOAuthEnabled = Boolean(authority && clientId)

const settings = {
  authority,
  client_id: clientId,
  redirect_uri: redirectUri,
  response_type: "code",
  scope,
  userStore: new WebStorageStateStore({ store: window.sessionStorage }),
  automaticSilentRenew: false,
}

let userManager: UserManager | null = null

function getUserManager(): UserManager {
  if (!userManager) {
    if (!isOAuthEnabled) {
      throw new Error("OAuth is not configured")
    }
    userManager = new UserManager(settings)
  }
  return userManager
}

export async function signinRedirect(): Promise<void> {
  const manager = getUserManager()
  await manager.signinRedirect()
}

export async function signinCallback(): Promise<string> {
  const manager = getUserManager()
  const user = await manager.signinRedirectCallback()
  return user.access_token
}

export async function signoutRedirect(): Promise<void> {
  const manager = getUserManager()
  await manager.signoutRedirect()
}
