import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { Plus } from "lucide-react"
import { useState } from "react"
import { useForm } from "react-hook-form"
import { z } from "zod"

import type { IntentPatternCreate } from "@/client"
import { IntentPatternsService } from "@/client"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
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
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { LoadingButton } from "@/components/ui/loading-button"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"
import { KeywordEditor } from "./KeywordEditor"

// Intent types from private-assistant-commons IntentType enum
const INTENT_TYPES = [
  "device.on",
  "device.off",
  "device.set",
  "device.open",
  "device.close",
  "media.play",
  "media.stop",
  "media.next",
  "media.volume_up",
  "media.volume_down",
  "media.volume_set",
  "device.query",
  "media.query",
  "data.query",
  "scene.apply",
  "schedule.set",
  "schedule.cancel",
]

const keywordSchema = z.object({
  keyword: z.string().min(1, { message: "Keyword is required" }),
  keyword_type: z.enum(["primary", "negative"]),
  is_regex: z.boolean(),
  weight: z.number().min(0).max(10),
})

const formSchema = z.object({
  intent_type: z.string().min(1, { message: "Intent type is required" }),
  enabled: z.boolean(),
  priority: z.number().int().min(0),
  description: z.string().optional().or(z.literal("")),
  keywords: z
    .array(keywordSchema)
    .min(1, { message: "At least one keyword required" }),
})

type FormData = z.infer<typeof formSchema>

const AddIntentPattern = () => {
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    mode: "onChange",
    criteriaMode: "all",
    defaultValues: {
      intent_type: "",
      enabled: true,
      priority: 0,
      description: "",
      keywords: [],
    },
  })

  const mutation = useMutation({
    mutationFn: (data: IntentPatternCreate) =>
      IntentPatternsService.createIntentPattern({ requestBody: data }),
    onSuccess: () => {
      showSuccessToast("Intent pattern created successfully")
      form.reset()
      setIsOpen(false)
    },
    onError: handleError.bind(showErrorToast),
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["intent-patterns"] })
    },
  })

  const onSubmit = (data: FormData) => {
    mutation.mutate(data as IntentPatternCreate)
  }

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button className="my-4">
          <Plus className="mr-2" />
          Add Intent Pattern
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Add Intent Pattern</DialogTitle>
          <DialogDescription>
            Configure a new voice command intent pattern with keywords.
          </DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)}>
            <div className="grid gap-4 py-4">
              <FormField
                control={form.control}
                name="intent_type"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>
                      Intent Type <span className="text-destructive">*</span>
                    </FormLabel>
                    <Select onValueChange={field.onChange} value={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select intent type" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {INTENT_TYPES.map((type) => (
                          <SelectItem key={type} value={type}>
                            {type}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="description"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Description</FormLabel>
                    <FormControl>
                      <Textarea
                        placeholder="Human-readable description..."
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <div className="grid grid-cols-2 gap-4">
                <FormField
                  control={form.control}
                  name="priority"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Priority</FormLabel>
                      <FormControl>
                        <Input
                          type="number"
                          {...field}
                          onChange={(e) =>
                            field.onChange(Number(e.target.value))
                          }
                        />
                      </FormControl>
                      <FormDescription>Higher = checked first</FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="enabled"
                  render={({ field }) => (
                    <FormItem className="flex items-center gap-2 space-y-0 pt-8">
                      <FormControl>
                        <Checkbox
                          checked={field.value}
                          onCheckedChange={field.onChange}
                        />
                      </FormControl>
                      <FormLabel className="!mt-0">Enabled</FormLabel>
                    </FormItem>
                  )}
                />
              </div>

              <FormField
                control={form.control}
                name="keywords"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>
                      Keywords <span className="text-destructive">*</span>
                    </FormLabel>
                    <FormControl>
                      <KeywordEditor
                        value={field.value}
                        onChange={field.onChange}
                      />
                    </FormControl>
                    <FormDescription>
                      Primary keywords trigger the intent, negative keywords
                      exclude matches
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <DialogFooter>
              <DialogClose asChild>
                <Button variant="outline" disabled={mutation.isPending}>
                  Cancel
                </Button>
              </DialogClose>
              <LoadingButton type="submit" loading={mutation.isPending}>
                Save
              </LoadingButton>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}

export default AddIntentPattern
