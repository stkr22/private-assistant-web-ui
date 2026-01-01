import { EllipsisVertical } from "lucide-react"
import { useState } from "react"

import type {
  DeviceTypePublic,
  GlobalDevicePublic,
  RoomPublic,
  SkillPublic,
} from "@/client"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import DeleteDevice from "./DeleteDevice"
import EditDevice from "./EditDevice"

interface DeviceActionsMenuProps {
  device: GlobalDevicePublic
  deviceTypes: DeviceTypePublic[]
  rooms: RoomPublic[]
  skills: SkillPublic[]
}

export const DeviceActionsMenu = ({
  device,
  deviceTypes,
  rooms,
  skills,
}: DeviceActionsMenuProps) => {
  const [open, setOpen] = useState(false)

  return (
    <DropdownMenu open={open} onOpenChange={setOpen}>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon">
          <EllipsisVertical />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <EditDevice
          device={device}
          deviceTypes={deviceTypes}
          rooms={rooms}
          skills={skills}
          onSuccess={() => setOpen(false)}
        />
        <DeleteDevice id={device.id} onSuccess={() => setOpen(false)} />
      </DropdownMenuContent>
    </DropdownMenu>
  )
}

export default DeviceActionsMenu
