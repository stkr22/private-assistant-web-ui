import { EllipsisVertical } from "lucide-react"
import { useState } from "react"

import type { ImagePublic } from "@/client"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { DeleteImage } from "./DeleteImage"
import { EditImage } from "./EditImage"

interface ImageActionsMenuProps {
  image: ImagePublic
}

export function ImageActionsMenu({ image }: ImageActionsMenuProps) {
  const [open, setOpen] = useState(false)

  return (
    <DropdownMenu open={open} onOpenChange={setOpen}>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon">
          <EllipsisVertical className="h-4 w-4" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <EditImage image={image} onSuccess={() => setOpen(false)} />
        <DeleteImage
          id={image.id}
          title={image.title}
          onSuccess={() => setOpen(false)}
        />
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
