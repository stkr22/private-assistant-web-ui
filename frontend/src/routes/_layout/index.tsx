import { useQuery } from "@tanstack/react-query"
import { createFileRoute, Link } from "@tanstack/react-router"
import { Cpu, DoorClosed, Layers } from "lucide-react"

import { DevicesService, DeviceTypesService, RoomsService } from "@/client"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import useAuth from "@/hooks/useAuth"

export const Route = createFileRoute("/_layout/")({
  component: Dashboard,
  head: () => ({
    meta: [
      {
        title: "Dashboard - Private Assistant",
      },
    ],
  }),
})

function StatCard({
  title,
  description,
  count,
  icon: Icon,
  href,
  isLoading,
}: {
  title: string
  description: string
  count?: number
  icon: React.ElementType
  href: string
  isLoading: boolean
}) {
  return (
    <Link to={href}>
      <Card className="hover:bg-muted/50 transition-colors cursor-pointer">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-sm font-medium">{title}</CardTitle>
            <Icon className="h-4 w-4 text-muted-foreground" />
          </div>
          <CardDescription>{description}</CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <Skeleton className="h-8 w-16" />
          ) : (
            <p className="text-3xl font-bold">{count ?? 0}</p>
          )}
        </CardContent>
      </Card>
    </Link>
  )
}

function Dashboard() {
  const { user: currentUser } = useAuth()

  const { data: devices, isLoading: devicesLoading } = useQuery({
    queryFn: () => DevicesService.readDevices({ skip: 0, limit: 1 }),
    queryKey: ["devices-count"],
  })

  const { data: rooms, isLoading: roomsLoading } = useQuery({
    queryFn: () => RoomsService.readRooms({ skip: 0, limit: 1 }),
    queryKey: ["rooms-count"],
  })

  const { data: deviceTypes, isLoading: deviceTypesLoading } = useQuery({
    queryFn: () => DeviceTypesService.readDeviceTypes({ skip: 0, limit: 1 }),
    queryKey: ["device-types-count"],
  })

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight truncate max-w-sm">
          Hi, {currentUser?.full_name || currentUser?.email}
        </h1>
        <p className="text-muted-foreground">
          Welcome back, nice to see you again!
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <StatCard
          title="Devices"
          description="Manage smart home devices"
          count={devices?.count}
          icon={Cpu}
          href="/devices"
          isLoading={devicesLoading}
        />
        <StatCard
          title="Rooms"
          description="Organize by location"
          count={rooms?.count}
          icon={DoorClosed}
          href="/rooms"
          isLoading={roomsLoading}
        />
        <StatCard
          title="Device Types"
          description="Device classifications"
          count={deviceTypes?.count}
          icon={Layers}
          href="/device-types"
          isLoading={deviceTypesLoading}
        />
      </div>
    </div>
  )
}
