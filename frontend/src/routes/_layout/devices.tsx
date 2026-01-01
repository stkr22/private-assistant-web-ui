import { useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { Search } from "lucide-react"
import { Suspense, useMemo } from "react"

import {
  DevicesService,
  DeviceTypesService,
  MonitoringService,
  RoomsService,
} from "@/client"
import { DataTable } from "@/components/Common/DataTable"
import AddDevice from "@/components/Devices/AddDevice"
import { createColumns } from "@/components/Devices/columns"
import PendingDevices from "@/components/Pending/PendingDevices"

function getDevicesQueryOptions() {
  return {
    queryFn: () => DevicesService.readDevices({ skip: 0, limit: 100 }),
    queryKey: ["devices"],
  }
}

function getDeviceTypesQueryOptions() {
  return {
    queryFn: () => DeviceTypesService.readDeviceTypes({ skip: 0, limit: 100 }),
    queryKey: ["device-types"],
  }
}

function getRoomsQueryOptions() {
  return {
    queryFn: () => RoomsService.readRooms({ skip: 0, limit: 100 }),
    queryKey: ["rooms"],
  }
}

function getSkillsQueryOptions() {
  return {
    queryFn: () => MonitoringService.readSkills(),
    queryKey: ["skills"],
  }
}

export const Route = createFileRoute("/_layout/devices")({
  component: Devices,
  head: () => ({
    meta: [
      {
        title: "Devices - Private Assistant",
      },
    ],
  }),
})

function DevicesTableContent() {
  const { data: devices } = useSuspenseQuery(getDevicesQueryOptions())
  const { data: deviceTypes } = useSuspenseQuery(getDeviceTypesQueryOptions())
  const { data: rooms } = useSuspenseQuery(getRoomsQueryOptions())
  const { data: skills } = useSuspenseQuery(getSkillsQueryOptions())

  const columns = useMemo(
    () => createColumns(deviceTypes.data, rooms.data, skills.data),
    [deviceTypes.data, rooms.data, skills.data]
  )

  const filterOptions = useMemo(
    () => ({
      device_type_name: deviceTypes.data.map((dt) => ({
        value: dt.name,
        label: dt.name,
      })),
      room_name: rooms.data.map((room) => ({
        value: room.name,
        label: room.name,
      })),
    }),
    [deviceTypes.data, rooms.data]
  )

  if (devices.data.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center text-center py-12">
        <div className="rounded-full bg-muted p-4 mb-4">
          <Search className="h-8 w-8 text-muted-foreground" />
        </div>
        <h3 className="text-lg font-semibold">
          You don't have any devices yet
        </h3>
        <p className="text-muted-foreground">Add a new device to get started</p>
      </div>
    )
  }

  return (
    <DataTable
      columns={columns}
      data={devices.data}
      filterOptions={filterOptions}
    />
  )
}

function DevicesTable() {
  return (
    <Suspense fallback={<PendingDevices />}>
      <DevicesTableContent />
    </Suspense>
  )
}

function Devices() {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Devices</h1>
          <p className="text-muted-foreground">
            Manage your smart home devices
          </p>
        </div>
        <AddDevice />
      </div>
      <DevicesTable />
    </div>
  )
}
