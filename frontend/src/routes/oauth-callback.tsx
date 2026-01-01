import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { useEffect, useState } from "react"

import { AuthLayout } from "@/components/Common/AuthLayout"
import { signinCallback } from "@/lib/oidc"

export const Route = createFileRoute("/oauth-callback")({
  component: OAuthCallback,
  head: () => ({
    meta: [
      {
        title: "Authenticating... - Private Assistant",
      },
    ],
  }),
})

function OAuthCallback() {
  const navigate = useNavigate()
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function handleCallback() {
      try {
        const token = await signinCallback()
        localStorage.setItem("access_token", token)
        navigate({ to: "/" })
      } catch (err) {
        console.error("OAuth callback error:", err)
        setError(err instanceof Error ? err.message : "Authentication failed")
        setTimeout(() => navigate({ to: "/login" }), 2000)
      }
    }
    handleCallback()
  }, [navigate])

  return (
    <AuthLayout>
      <div className="flex flex-col items-center gap-4 text-center">
        {error ? (
          <>
            <div className="rounded-full bg-destructive/10 p-3">
              <svg
                className="h-6 w-6 text-destructive"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                aria-hidden="true"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </div>
            <p className="text-destructive">Authentication failed</p>
            <p className="text-sm text-muted-foreground">
              Redirecting to login...
            </p>
          </>
        ) : (
          <>
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
            <p className="text-muted-foreground">
              Completing authentication...
            </p>
          </>
        )}
      </div>
    </AuthLayout>
  )
}
