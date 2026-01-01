import type { ColumnDef } from "@tanstack/react-table"
import { Check, Copy } from "lucide-react"

import type { SkillPublic } from "@/client"
import { Button } from "@/components/ui/button"
import { useCopyToClipboard } from "@/hooks/useCopyToClipboard"
import { cn } from "@/lib/utils"

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

export const columns: ColumnDef<SkillPublic>[] = [
  {
    accessorKey: "id",
    header: "ID",
    cell: ({ row }) => <CopyId id={row.original.id} />,
    enableColumnFilter: false,
    enableSorting: false,
  },
  {
    accessorKey: "name",
    header: "Name",
    cell: ({ row }) => (
      <span className="font-medium">{row.original.name}</span>
    ),
    enableColumnFilter: false,
    enableSorting: true,
  },
  {
    accessorKey: "created_at",
    header: "Registered",
    cell: ({ row }) => {
      const date = new Date(row.original.created_at)
      return (
        <span className={cn("text-muted-foreground")}>
          {date.toLocaleString()}
        </span>
      )
    },
    enableColumnFilter: false,
    enableSorting: true,
  },
  {
    accessorKey: "updated_at",
    header: "Last Updated",
    cell: ({ row }) => {
      const date = new Date(row.original.updated_at)
      return (
        <span className={cn("text-muted-foreground")}>
          {date.toLocaleString()}
        </span>
      )
    },
    enableColumnFilter: false,
    enableSorting: true,
  },
]
