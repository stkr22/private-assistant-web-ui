import { useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { Search } from "lucide-react"
import { Suspense } from "react"

import { IntentPatternsService } from "@/client"
import { DataTable } from "@/components/Common/DataTable"
import AddIntentPattern from "@/components/IntentPatterns/AddIntentPattern"
import { columns } from "@/components/IntentPatterns/columns"
import PendingIntentPatterns from "@/components/Pending/PendingIntentPatterns"

function getIntentPatternsQueryOptions() {
  return {
    queryFn: () =>
      IntentPatternsService.readIntentPatterns({ skip: 0, limit: 100 }),
    queryKey: ["intent-patterns"],
  }
}

export const Route = createFileRoute("/_layout/intent-patterns")({
  component: IntentPatterns,
  head: () => ({
    meta: [
      {
        title: "Intent Patterns - Private Assistant",
      },
    ],
  }),
})

function IntentPatternsTableContent() {
  const { data: patterns } = useSuspenseQuery(getIntentPatternsQueryOptions())

  if (!patterns || patterns.data?.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center text-center py-12">
        <div className="rounded-full bg-muted p-4 mb-4">
          <Search className="h-8 w-8 text-muted-foreground" />
        </div>
        <h3 className="text-lg font-semibold">
          No intent patterns configured yet
        </h3>
        <p className="text-muted-foreground">
          Add a new pattern to get started
        </p>
      </div>
    )
  }

  return <DataTable columns={columns} data={patterns.data} />
}

function IntentPatternsTable() {
  return (
    <Suspense fallback={<PendingIntentPatterns />}>
      <IntentPatternsTableContent />
    </Suspense>
  )
}

function IntentPatterns() {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Intent Patterns</h1>
          <p className="text-muted-foreground">
            Configure voice command intent patterns and keywords
          </p>
        </div>
        <AddIntentPattern />
      </div>
      <IntentPatternsTable />
    </div>
  )
}
