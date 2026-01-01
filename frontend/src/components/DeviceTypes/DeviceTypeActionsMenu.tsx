import { EllipsisVertical } from "lucide-react"
import { useState } from "react"

import type { DeviceTypePublic } from "@/client"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import DeleteDeviceType from "./DeleteDeviceType"
import EditDeviceType from "./EditDeviceType"

interface DeviceTypeActionsMenuProps {
  deviceType: DeviceTypePublic
}

export const DeviceTypeActionsMenu = ({
  deviceType,
}: DeviceTypeActionsMenuProps) => {
  const [open, setOpen] = useState(false)

  return (
    <DropdownMenu open={open} onOpenChange={setOpen}>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon">
          <EllipsisVertical />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <EditDeviceType
          deviceType={deviceType}
          onSuccess={() => setOpen(false)}
        />
        <DeleteDeviceType id={deviceType.id} onSuccess={() => setOpen(false)} />
      </DropdownMenuContent>
    </DropdownMenu>
  )
}

export default DeviceTypeActionsMenu
