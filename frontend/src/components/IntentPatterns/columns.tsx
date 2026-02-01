import type { ColumnDef } from "@tanstack/react-table"
import { Check, Copy, Tag } from "lucide-react"

import type {
  app__models_commons_api__IntentPatternPublic,
  IntentPatternKeywordPublic,
} from "@/client"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { useCopyToClipboard } from "@/hooks/useCopyToClipboard"
import { IntentPatternActionsMenu } from "./IntentPatternActionsMenu"

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

export const columns: ColumnDef<app__models_commons_api__IntentPatternPublic>[] =
  [
    {
      accessorKey: "id",
      header: "ID",
      cell: ({ row }) => <CopyId id={row.original.id} />,
      enableColumnFilter: false,
      enableSorting: false,
    },
    {
      accessorKey: "intent_type",
      header: "Intent Type",
      cell: ({ row }) => (
        <div className="flex items-center gap-2">
          <Tag className="h-4 w-4 text-muted-foreground" />
          <span className="font-medium">{row.original.intent_type}</span>
        </div>
      ),
      enableColumnFilter: true,
      enableSorting: true,
    },
    {
      accessorKey: "keywords",
      header: "Keywords",
      cell: ({ row }) => {
        const keywords = row.original.keywords || []
        const primaryKeywords = keywords.filter(
          (k: IntentPatternKeywordPublic) => k.keyword_type === "primary",
        )
        const negativeKeywords = keywords.filter(
          (k: IntentPatternKeywordPublic) => k.keyword_type === "negative",
        )

        return (
          <div className="flex flex-wrap gap-1">
            {primaryKeywords
              .slice(0, 3)
              .map((kw: IntentPatternKeywordPublic) => (
                <Badge key={kw.id} variant="default" className="text-xs">
                  {kw.is_regex ? `/${kw.keyword}/` : kw.keyword}
                </Badge>
              ))}
            {negativeKeywords.length > 0 && (
              <Badge variant="destructive" className="text-xs">
                -{negativeKeywords.length} negative
              </Badge>
            )}
            {primaryKeywords.length > 3 && (
              <Badge variant="outline" className="text-xs">
                +{primaryKeywords.length - 3} more
              </Badge>
            )}
          </div>
        )
      },
      enableColumnFilter: false,
      enableSorting: false,
    },
    {
      accessorKey: "priority",
      header: "Priority",
      cell: ({ row }) => (
        <Badge variant="secondary">{row.original.priority}</Badge>
      ),
      enableColumnFilter: false,
      enableSorting: true,
    },
    {
      accessorKey: "enabled",
      header: "Status",
      cell: ({ row }) => (
        <Badge variant={row.original.enabled ? "default" : "outline"}>
          {row.original.enabled ? "Enabled" : "Disabled"}
        </Badge>
      ),
      enableColumnFilter: false,
      enableSorting: true,
      meta: {
        filterVariant: "select",
      },
    },
    {
      accessorKey: "description",
      header: "Description",
      cell: ({ row }) => (
        <span className="text-muted-foreground text-sm">
          {row.original.description || "-"}
        </span>
      ),
      enableColumnFilter: true,
      enableSorting: false,
    },
    {
      id: "actions",
      header: () => <span className="sr-only">Actions</span>,
      cell: ({ row }) => (
        <div className="flex justify-end">
          <IntentPatternActionsMenu pattern={row.original} />
        </div>
      ),
      enableColumnFilter: false,
      enableSorting: false,
    },
  ]
