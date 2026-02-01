import { MoreHorizontal, Pencil } from "lucide-react"
import { useState } from "react"

import type { app__models_commons_api__IntentPatternPublic } from "@/client"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import DeleteIntentPattern from "./DeleteIntentPattern"
import EditIntentPattern from "./EditIntentPattern"

interface IntentPatternActionsMenuProps {
  pattern: app__models_commons_api__IntentPatternPublic
}

export function IntentPatternActionsMenu({
  pattern,
}: IntentPatternActionsMenuProps) {
  const [showEditDialog, setShowEditDialog] = useState(false)

  return (
    <>
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" className="h-8 w-8 p-0">
            <span className="sr-only">Open menu</span>
            <MoreHorizontal className="h-4 w-4" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
          <DropdownMenuItem onSelect={() => setShowEditDialog(true)}>
            <Pencil className="mr-2 h-4 w-4" />
            Edit
          </DropdownMenuItem>
          <DeleteIntentPattern pattern={pattern} onSuccess={() => {}} />
        </DropdownMenuContent>
      </DropdownMenu>

      {showEditDialog && (
        <EditIntentPattern
          pattern={pattern}
          open={showEditDialog}
          onOpenChange={setShowEditDialog}
        />
      )}
    </>
  )
}
