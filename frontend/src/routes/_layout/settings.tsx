import { createFileRoute } from "@tanstack/react-router"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import useAuth from "@/hooks/useAuth"

export const Route = createFileRoute("/_layout/settings")({
  component: UserSettings,
  head: () => ({
    meta: [
      {
        title: "Settings - Private Assistant",
      },
    ],
  }),
})

function UserSettings() {
  const { user: currentUser } = useAuth()

  if (!currentUser) {
    return null
  }

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">User Settings</h1>
        <p className="text-muted-foreground">View your account information</p>
      </div>

      <Card className="max-w-md">
        <CardHeader>
          <CardTitle className="text-lg">Account Information</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <p className="text-sm text-muted-foreground">Email</p>
            <p className="font-medium">{currentUser.email}</p>
          </div>
          {currentUser.full_name && (
            <div>
              <p className="text-sm text-muted-foreground">Full Name</p>
              <p className="font-medium">{currentUser.full_name}</p>
            </div>
          )}
          <div>
            <p className="text-sm text-muted-foreground">Status</p>
            <p className="font-medium">
              {currentUser.is_active ? "Active" : "Inactive"}
            </p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Role</p>
            <p className="font-medium">
              {currentUser.is_superuser ? "Administrator" : "User"}
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
