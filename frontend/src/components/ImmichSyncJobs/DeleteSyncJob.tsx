import { useMutation, useQueryClient } from "@tanstack/react-query"
import { Trash2 } from "lucide-react"
import { useState } from "react"

import { ImmichSyncJobsService } from "@/client"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { LoadingButton } from "@/components/ui/loading-button"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

interface DeleteSyncJobProps {
  jobId: string
  jobName: string
}

const DeleteSyncJob = ({ jobId, jobName }: DeleteSyncJobProps) => {
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const mutation = useMutation({
    mutationFn: () => ImmichSyncJobsService.deleteSyncJob({ jobId }),
    onSuccess: () => {
      showSuccessToast("Sync job deleted successfully")
      setIsOpen(false)
    },
    onError: handleError.bind(showErrorToast),
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["immich-sync-jobs"] })
    },
  })

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button variant="ghost" size="icon" className="text-destructive">
          <Trash2 className="h-4 w-4" />
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Delete Sync Job</DialogTitle>
          <DialogDescription>
            Are you sure you want to delete{" "}
            <span className="font-medium">{jobName}</span>? This action cannot
            be undone.
          </DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <DialogClose asChild>
            <Button variant="outline" disabled={mutation.isPending}>
              Cancel
            </Button>
          </DialogClose>
          <LoadingButton
            variant="destructive"
            loading={mutation.isPending}
            onClick={() => mutation.mutate()}
          >
            Delete
          </LoadingButton>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

export default DeleteSyncJob
