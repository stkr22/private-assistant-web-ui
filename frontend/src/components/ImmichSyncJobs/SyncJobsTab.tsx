import { useQuery } from "@tanstack/react-query"
import { Settings2 } from "lucide-react"

import {
  DevicesService,
  type ImmichSyncJobPublic,
  ImmichSyncJobsService,
} from "@/client"
import { Badge } from "@/components/ui/badge"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import AddSyncJob from "./AddSyncJob"
import DeleteSyncJob from "./DeleteSyncJob"
import EditSyncJob from "./EditSyncJob"

function getSyncJobsQueryOptions() {
  return {
    queryFn: () => ImmichSyncJobsService.readSyncJobs({ skip: 0, limit: 100 }),
    queryKey: ["immich-sync-jobs"],
  }
}

function getDevicesQueryOptions() {
  return {
    queryFn: () => DevicesService.readDevices({ skip: 0, limit: 100 }),
    queryKey: ["devices"],
  }
}

function SyncJobRow({
  job,
  deviceName,
}: {
  job: ImmichSyncJobPublic
  deviceName: string
}) {
  return (
    <TableRow>
      <TableCell className="font-medium">{job.name}</TableCell>
      <TableCell>{deviceName}</TableCell>
      <TableCell>
        <Badge variant={job.strategy === "SMART" ? "default" : "secondary"}>
          {job.strategy}
        </Badge>
      </TableCell>
      <TableCell>
        {job.strategy === "SMART" && job.query ? (
          <span className="text-muted-foreground text-sm truncate max-w-[200px] block">
            {job.query}
          </span>
        ) : (
          <span className="text-muted-foreground">-</span>
        )}
      </TableCell>
      <TableCell className="text-center">{job.count}</TableCell>
      <TableCell>
        <Badge variant={job.is_active ? "default" : "outline"}>
          {job.is_active ? "Active" : "Inactive"}
        </Badge>
      </TableCell>
      <TableCell>
        <div className="flex items-center gap-1">
          <EditSyncJob job={job} />
          <DeleteSyncJob jobId={job.id} jobName={job.name} />
        </div>
      </TableCell>
    </TableRow>
  )
}

function SyncJobsTable() {
  const { data: syncJobs, isLoading: isLoadingJobs } = useQuery(
    getSyncJobsQueryOptions(),
  )
  const { data: devices, isLoading: isLoadingDevices } = useQuery(
    getDevicesQueryOptions(),
  )

  const isLoading = isLoadingJobs || isLoadingDevices

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-muted-foreground">Loading sync jobs...</div>
      </div>
    )
  }

  if (!syncJobs?.data.length) {
    return (
      <div className="flex flex-col items-center justify-center text-center py-12">
        <div className="rounded-full bg-muted p-4 mb-4">
          <Settings2 className="h-8 w-8 text-muted-foreground" />
        </div>
        <h3 className="text-lg font-semibold">No sync jobs yet</h3>
        <p className="text-muted-foreground mb-4">
          Create your first sync job to automatically fetch images from Immich
        </p>
        <AddSyncJob />
      </div>
    )
  }

  // Build device lookup map
  const deviceMap = new Map(devices?.data.map((d) => [d.id, d.name]) ?? [])

  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Name</TableHead>
            <TableHead>Target Device</TableHead>
            <TableHead>Strategy</TableHead>
            <TableHead>Query</TableHead>
            <TableHead className="text-center">Count</TableHead>
            <TableHead>Status</TableHead>
            <TableHead className="w-[100px]">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {syncJobs.data.map((job) => (
            <SyncJobRow
              key={job.id}
              job={job}
              deviceName={deviceMap.get(job.target_device_id) ?? "Unknown"}
            />
          ))}
        </TableBody>
      </Table>
    </div>
  )
}

export function SyncJobsTab() {
  const { data: syncJobs } = useQuery(getSyncJobsQueryOptions())
  const hasJobs = (syncJobs?.data.length ?? 0) > 0

  return (
    <div className="flex flex-col gap-4">
      {hasJobs && (
        <div className="flex justify-end">
          <AddSyncJob />
        </div>
      )}
      <SyncJobsTable />
    </div>
  )
}

export default SyncJobsTab
