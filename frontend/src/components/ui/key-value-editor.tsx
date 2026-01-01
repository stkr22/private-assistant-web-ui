import { Plus, Trash2 } from "lucide-react"
import { useState } from "react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

interface KeyValueEditorProps {
  value: Record<string, unknown>
  onChange: (value: Record<string, unknown>) => void
}

export function KeyValueEditor({ value = {}, onChange }: KeyValueEditorProps) {
  const [newKey, setNewKey] = useState("")
  const [newValue, setNewValue] = useState("")

  const entries = Object.entries(value)

  const addEntry = () => {
    const trimmedKey = newKey.trim()
    if (trimmedKey && !(trimmedKey in value)) {
      // Try to parse value as JSON, fallback to string
      let parsedValue: unknown = newValue
      try {
        parsedValue = JSON.parse(newValue)
      } catch {
        // Keep as string
      }
      onChange({ ...value, [trimmedKey]: parsedValue })
      setNewKey("")
      setNewValue("")
    }
  }

  const removeEntry = (key: string) => {
    const newObj = { ...value }
    delete newObj[key]
    onChange(newObj)
  }

  const updateEntry = (oldKey: string, newVal: string) => {
    let parsedValue: unknown = newVal
    try {
      parsedValue = JSON.parse(newVal)
    } catch {
      // Keep as string
    }
    onChange({ ...value, [oldKey]: parsedValue })
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      e.preventDefault()
      addEntry()
    }
  }

  return (
    <div className="flex flex-col gap-2">
      {entries.length > 0 && (
        <div className="flex flex-col gap-2 rounded-md border p-2">
          {entries.map(([key, val]) => (
            <div key={key} className="flex items-center gap-2">
              <span className="min-w-[100px] text-sm font-medium truncate">
                {key}
              </span>
              <Input
                value={typeof val === "string" ? val : JSON.stringify(val)}
                onChange={(e) => updateEntry(key, e.target.value)}
                className="flex-1 h-8 text-sm"
              />
              <Button
                type="button"
                variant="ghost"
                size="icon"
                className="h-8 w-8"
                onClick={() => removeEntry(key)}
              >
                <Trash2 className="h-4 w-4 text-destructive" />
              </Button>
            </div>
          ))}
        </div>
      )}
      <div className="flex gap-2">
        <Input
          value={newKey}
          onChange={(e) => setNewKey(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Key"
          className="flex-1"
        />
        <Input
          value={newValue}
          onChange={(e) => setNewValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Value"
          className="flex-1"
        />
        <Button
          type="button"
          variant="outline"
          size="icon"
          onClick={addEntry}
          disabled={!newKey.trim()}
        >
          <Plus className="h-4 w-4" />
        </Button>
      </div>
    </div>
  )
}
