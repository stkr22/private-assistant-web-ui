import { Code, Minus, Plus } from "lucide-react"
import { useState } from "react"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import { Input } from "@/components/ui/input"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

interface Keyword {
  keyword: string
  keyword_type: "primary" | "negative"
  is_regex: boolean
  weight: number
}

interface KeywordEditorProps {
  value: Keyword[]
  onChange: (value: Keyword[]) => void
}

export function KeywordEditor({ value, onChange }: KeywordEditorProps) {
  const [newKeyword, setNewKeyword] = useState("")
  const [newKeywordType, setNewKeywordType] = useState<"primary" | "negative">(
    "primary",
  )
  const [newIsRegex, setNewIsRegex] = useState(false)

  const addKeyword = () => {
    if (!newKeyword.trim()) return

    onChange([
      ...value,
      {
        keyword: newKeyword.trim(),
        keyword_type: newKeywordType,
        is_regex: newIsRegex,
        weight: 1.0,
      },
    ])

    setNewKeyword("")
    setNewKeywordType("primary")
    setNewIsRegex(false)
  }

  const removeKeyword = (index: number) => {
    onChange(value.filter((_, i) => i !== index))
  }

  return (
    <div className="space-y-3 border rounded-md p-4">
      {/* Existing keywords */}
      {value.length > 0 && (
        <div className="space-y-2">
          {value.map((kw, index) => (
            <div
              key={index}
              className="flex items-center gap-2 p-2 bg-muted rounded-md"
            >
              <Badge
                variant={
                  kw.keyword_type === "primary" ? "default" : "destructive"
                }
              >
                {kw.keyword_type === "primary" ? "Primary" : "Negative"}
              </Badge>
              {kw.is_regex && (
                <Code className="h-3 w-3 text-muted-foreground" />
              )}
              <span className="flex-1 font-mono text-sm">
                {kw.is_regex ? `/${kw.keyword}/` : kw.keyword}
              </span>
              <Button
                type="button"
                variant="ghost"
                size="icon"
                className="h-6 w-6"
                onClick={() => removeKeyword(index)}
              >
                <Minus className="h-3 w-3" />
              </Button>
            </div>
          ))}
        </div>
      )}

      {/* Add new keyword */}
      <div className="flex items-end gap-2">
        <div className="flex-1">
          <Input
            placeholder="Keyword or regex pattern..."
            value={newKeyword}
            onChange={(e) => setNewKeyword(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                e.preventDefault()
                addKeyword()
              }
            }}
          />
        </div>
        <Select
          value={newKeywordType}
          onValueChange={(v) => setNewKeywordType(v as "primary" | "negative")}
        >
          <SelectTrigger className="w-32">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="primary">Primary</SelectItem>
            <SelectItem value="negative">Negative</SelectItem>
          </SelectContent>
        </Select>
        <div className="flex items-center gap-2">
          <Checkbox
            id="new-keyword-regex"
            checked={newIsRegex}
            onCheckedChange={(checked) => setNewIsRegex(!!checked)}
          />
          <label htmlFor="new-keyword-regex" className="text-sm">
            Regex
          </label>
        </div>
        <Button type="button" onClick={addKeyword}>
          <Plus className="h-4 w-4" />
        </Button>
      </div>
    </div>
  )
}
