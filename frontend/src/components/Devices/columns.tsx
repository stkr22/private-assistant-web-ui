import type { ColumnDef } from "@tanstack/react-table"
import { Check, Copy } from "lucide-react"

import type {
  DeviceTypePublic,
  GlobalDevicePublic,
  RoomPublic,
  SkillPublic,
} from "@/client"
import { Button } from "@/components/ui/button"
import { useCopyToClipboard } from "@/hooks/useCopyToClipboard"
import { cn } from "@/lib/utils"
import { DeviceActionsMenu } from "./DeviceActionsMenu"

function CopyId({ id }: { id: string }) {
  const [copiedText, copy] = useCopyToClipboard()
  const isCopied = copiedText === id

  return (
    <div className="flex items-center gap-1.5 group">
      <span className="font-mono text-xs text-muted-foreground">
        {id.slice(0, 8)}...
      </span>
      <Button
        variant="ghost"
        size="icon"
        className="size-6 opacity-0 group-hover:opacity-100 transition-opacity"
        onClick={() => copy(id)}
      >
        {isCopied ? (
          <Check className="size-3 text-green-500" />
        ) : (
          <Copy className="size-3" />
        )}
      </Button>
    </div>
  )
}

export interface DeviceTableData extends GlobalDevicePublic {
  deviceTypeName?: string
  roomName?: string
}

export function createColumns(
  deviceTypes: DeviceTypePublic[],
  rooms: RoomPublic[],
  skills: SkillPublic[],
): ColumnDef<DeviceTableData>[] {
  const deviceTypeMap = new Map(deviceTypes.map((dt) => [dt.id, dt.name]))
  const roomMap = new Map(rooms.map((r) => [r.id, r.name]))

  return [
    {
      accessorKey: "id",
      header: "ID",
      cell: ({ row }) => <CopyId id={row.original.id} />,
      enableColumnFilter: true,
      filterFn: "includesString",
      enableSorting: false,
    },
    {
      accessorKey: "name",
      header: "Name",
      cell: ({ row }) => (
        <span className="font-medium">{row.original.name}</span>
      ),
      enableColumnFilter: true,
      filterFn: "includesString",
      enableSorting: true,
    },
    {
      id: "device_type_name",
      accessorFn: (row) => deviceTypeMap.get(row.device_type_id) || "Unknown",
      header: "Type",
      cell: ({ row }) => {
        const typeName = deviceTypeMap.get(row.original.device_type_id)
        return (
          <span className={cn("text-muted-foreground", !typeName && "italic")}>
            {typeName || "Unknown"}
          </span>
        )
      },
      enableColumnFilter: true,
      filterFn: "equals",
      enableSorting: true,
      meta: { filterVariant: "select" },
    },
    {
      id: "room_name",
      accessorFn: (row) => (row.room_id ? roomMap.get(row.room_id) || "" : ""),
      header: "Room",
      cell: ({ row }) => {
        const roomId = row.original.room_id
        const roomName = roomId ? roomMap.get(roomId) : null
        return (
          <span className={cn("text-muted-foreground", !roomName && "italic")}>
            {roomName || "No room"}
          </span>
        )
      },
      enableColumnFilter: true,
      filterFn: "equals",
      enableSorting: true,
      meta: { filterVariant: "select" },
    },
    {
      accessorKey: "created_at",
      header: "Created",
      cell: ({ row }) => {
        const date = new Date(row.original.created_at)
        return (
          <span className={cn("text-muted-foreground")}>
            {date.toLocaleDateString()}
          </span>
        )
      },
      enableColumnFilter: false,
      enableSorting: true,
    },
    {
      id: "actions",
      header: () => <span className="sr-only">Actions</span>,
      cell: ({ row }) => (
        <div className="flex justify-end">
          <DeviceActionsMenu
            device={row.original}
            deviceTypes={deviceTypes}
            rooms={rooms}
            skills={skills}
          />
        </div>
      ),
      enableColumnFilter: false,
      enableSorting: false,
    },
  ]
}
