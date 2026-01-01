import { useMutation, useQueryClient } from "@tanstack/react-query"
import { Trash2 } from "lucide-react"
import { useState } from "react"

import { RoomsService } from "@/client"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { DropdownMenuItem } from "@/components/ui/dropdown-menu"
import { LoadingButton } from "@/components/ui/loading-button"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

interface DeleteRoomProps {
  id: string
  onSuccess: () => void
}

const DeleteRoom = ({ id, onSuccess }: DeleteRoomProps) => {
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const mutation = useMutation({
    mutationFn: () => RoomsService.deleteRoom({ roomId: id }),
    onSuccess: () => {
      showSuccessToast("The room was deleted successfully")
      setIsOpen(false)
      onSuccess()
    },
    onError: handleError.bind(showErrorToast),
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["rooms"] })
    },
  })

  const handleDelete = (e: React.FormEvent) => {
    e.preventDefault()
    mutation.mutate()
  }

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DropdownMenuItem
        variant="destructive"
        onSelect={(e) => e.preventDefault()}
        onClick={() => setIsOpen(true)}
      >
        <Trash2 />
        Delete Room
      </DropdownMenuItem>
      <DialogContent className="sm:max-w-md">
        <form onSubmit={handleDelete}>
          <DialogHeader>
            <DialogTitle>Delete Room</DialogTitle>
            <DialogDescription>
              This room will be permanently deleted. Are you sure? You will not
              be able to undo this action.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="mt-4">
            <DialogClose asChild>
              <Button
                type="button"
                variant="outline"
                disabled={mutation.isPending}
              >
                Cancel
              </Button>
            </DialogClose>
            <LoadingButton
              variant="destructive"
              type="submit"
              loading={mutation.isPending}
            >
              Delete
            </LoadingButton>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

export default DeleteRoom
