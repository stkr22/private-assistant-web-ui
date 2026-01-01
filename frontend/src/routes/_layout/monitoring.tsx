import { useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { Activity } from "lucide-react"
import { Suspense } from "react"

import { MonitoringService } from "@/client"
import { DataTable } from "@/components/Common/DataTable"
import { columns } from "@/components/Monitoring/columns"
import PendingMonitoring from "@/components/Pending/PendingMonitoring"

function getSkillsQueryOptions() {
  return {
    queryFn: () => MonitoringService.readSkills(),
    queryKey: ["skills"],
    refetchInterval: 30 * 1000, // Auto-refresh every 30 seconds
  }
}

export const Route = createFileRoute("/_layout/monitoring")({
  component: Monitoring,
  head: () => ({
    meta: [
      {
        title: "Monitoring - Private Assistant",
      },
    ],
  }),
})

function SkillsTableContent() {
  const { data: skills, dataUpdatedAt } = useSuspenseQuery(
    getSkillsQueryOptions(),
  )

  if (skills.data.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center text-center py-12">
        <div className="rounded-full bg-muted p-4 mb-4">
          <Activity className="h-8 w-8 text-muted-foreground" />
        </div>
        <h3 className="text-lg font-semibold">No skills registered yet</h3>
        <p className="text-muted-foreground">
          Skills will appear here when they register with the system
        </p>
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="text-sm text-muted-foreground">
        Last updated: {new Date(dataUpdatedAt).toLocaleTimeString()}
      </div>
      <DataTable columns={columns} data={skills.data} />
    </div>
  )
}

function SkillsTable() {
  return (
    <Suspense fallback={<PendingMonitoring />}>
      <SkillsTableContent />
    </Suspense>
  )
}

function Monitoring() {
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Monitoring</h1>
        <p className="text-muted-foreground">
          View registered skills (auto-refreshes every 30 seconds)
        </p>
      </div>
      <SkillsTable />
    </div>
  )
}
