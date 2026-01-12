import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { ChevronDown, Plus } from "lucide-react"
import { useState } from "react"
import { useForm } from "react-hook-form"
import { z } from "zod"

import {
  DevicesService,
  type ImmichSyncJobCreate,
  ImmichSyncJobsService,
} from "@/client"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible"
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
import { Slider } from "@/components/ui/slider"
import { Switch } from "@/components/ui/switch"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

const formSchema = z
  .object({
    name: z.string().min(1, { message: "Name is required" }),
    target_device_id: z
      .string()
      .min(1, { message: "Target device is required" }),
    strategy: z.enum(["RANDOM", "SMART"]),
    query: z.string().optional(),
    count: z.number().min(1).max(1000),
    random_pick: z.boolean(),
    overfetch_multiplier: z.number().min(1).max(10),
    min_color_score: z.number().min(0).max(1),
    is_active: z.boolean(),
    // Optional Immich filters
    is_favorite: z.boolean().optional(),
    city: z.string().optional(),
    state: z.string().optional(),
    country: z.string().optional(),
    taken_after: z.string().optional(),
    taken_before: z.string().optional(),
    rating: z.number().min(0).max(5).optional(),
  })
  .refine(
    (data) =>
      data.strategy !== "SMART" || (data.query && data.query.length > 0),
    { message: "Query is required for SMART strategy", path: ["query"] },
  )

type FormData = z.infer<typeof formSchema>

const AddSyncJob = () => {
  const [isOpen, setIsOpen] = useState(false)
  const [showAdvanced, setShowAdvanced] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const { data: devices } = useQuery({
    queryFn: () => DevicesService.readDevices({ skip: 0, limit: 100 }),
    queryKey: ["devices"],
  })

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      name: "",
      target_device_id: "",
      strategy: "RANDOM",
      query: "",
      count: 10,
      random_pick: false,
      overfetch_multiplier: 3,
      min_color_score: 0.5,
      is_active: true,
      is_favorite: undefined,
      city: "",
      state: "",
      country: "",
      taken_after: "",
      taken_before: "",
      rating: undefined,
    },
  })

  const strategy = form.watch("strategy")

  const mutation = useMutation({
    mutationFn: (data: ImmichSyncJobCreate) =>
      ImmichSyncJobsService.createSyncJob({ requestBody: data }),
    onSuccess: () => {
      showSuccessToast("Sync job created successfully")
      form.reset()
      setIsOpen(false)
      setShowAdvanced(false)
    },
    onError: handleError.bind(showErrorToast),
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["immich-sync-jobs"] })
    },
  })

  const onSubmit = (data: FormData) => {
    const createData: ImmichSyncJobCreate = {
      name: data.name,
      target_device_id: data.target_device_id,
      strategy: data.strategy,
      query: data.strategy === "SMART" ? data.query : null,
      count: data.count,
      random_pick: data.random_pick,
      overfetch_multiplier: data.overfetch_multiplier,
      min_color_score: data.min_color_score,
      is_active: data.is_active,
      is_favorite: data.is_favorite ?? null,
      city: data.city || null,
      state: data.state || null,
      country: data.country || null,
      taken_after: data.taken_after || null,
      taken_before: data.taken_before || null,
      rating: data.rating ?? null,
    }
    mutation.mutate(createData)
  }

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button>
          <Plus className="mr-2" />
          Add Sync Job
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-lg max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Add Sync Job</DialogTitle>
          <DialogDescription>
            Configure how images are fetched from Immich for a display device.
          </DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)}>
            <div className="grid gap-4 py-4">
              {/* Name */}
              <FormField
                control={form.control}
                name="name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>
                      Name <span className="text-destructive">*</span>
                    </FormLabel>
                    <FormControl>
                      <Input
                        placeholder="e.g., family-favorites"
                        type="text"
                        {...field}
                      />
                    </FormControl>
                    <FormDescription>
                      Unique identifier for this sync job
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {/* Target Device */}
              <FormField
                control={form.control}
                name="target_device_id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>
                      Target Device <span className="text-destructive">*</span>
                    </FormLabel>
                    <Select onValueChange={field.onChange} value={field.value}>
                      <FormControl>
                        <SelectTrigger className="w-full">
                          <SelectValue placeholder="Select a device" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {devices?.data.map((device) => (
                          <SelectItem key={device.id} value={device.id}>
                            {device.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormDescription>
                      Device with display_width, display_height, orientation
                      attributes
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {/* Strategy */}
              <FormField
                control={form.control}
                name="strategy"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Strategy</FormLabel>
                    <Select onValueChange={field.onChange} value={field.value}>
                      <FormControl>
                        <SelectTrigger className="w-full">
                          <SelectValue />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="RANDOM">
                          Random - Fetch random images
                        </SelectItem>
                        <SelectItem value="SMART">
                          Smart - AI semantic search (CLIP)
                        </SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {/* Query (shown only for SMART strategy) */}
              {strategy === "SMART" && (
                <FormField
                  control={form.control}
                  name="query"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>
                        Search Query <span className="text-destructive">*</span>
                      </FormLabel>
                      <FormControl>
                        <Input
                          placeholder='e.g., "sunset at beach", "kids playing"'
                          type="text"
                          {...field}
                        />
                      </FormControl>
                      <FormDescription>
                        Natural language query for semantic search
                      </FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              )}

              {/* Count */}
              <FormField
                control={form.control}
                name="count"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Image Count: {field.value}</FormLabel>
                    <FormControl>
                      <Slider
                        min={1}
                        max={100}
                        step={1}
                        value={[field.value]}
                        onValueChange={([value]) => field.onChange(value)}
                      />
                    </FormControl>
                    <FormDescription>
                      Number of images to sync per run
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {/* Random Pick (for SMART strategy) */}
              {strategy === "SMART" && (
                <FormField
                  control={form.control}
                  name="random_pick"
                  render={({ field }) => (
                    <FormItem className="flex flex-row items-center justify-between rounded-lg border p-3">
                      <div className="space-y-0.5">
                        <FormLabel>Random Pick</FormLabel>
                        <FormDescription>
                          Add randomness to smart search results
                        </FormDescription>
                      </div>
                      <FormControl>
                        <Switch
                          checked={field.value}
                          onCheckedChange={field.onChange}
                        />
                      </FormControl>
                    </FormItem>
                  )}
                />
              )}

              {/* Is Active */}
              <FormField
                control={form.control}
                name="is_active"
                render={({ field }) => (
                  <FormItem className="flex flex-row items-center justify-between rounded-lg border p-3">
                    <div className="space-y-0.5">
                      <FormLabel>Active</FormLabel>
                      <FormDescription>
                        Enable this sync job to run on schedule
                      </FormDescription>
                    </div>
                    <FormControl>
                      <Switch
                        checked={field.value}
                        onCheckedChange={field.onChange}
                      />
                    </FormControl>
                  </FormItem>
                )}
              />

              {/* Advanced Filters Collapsible */}
              <Collapsible open={showAdvanced} onOpenChange={setShowAdvanced}>
                <CollapsibleTrigger asChild>
                  <Button variant="ghost" className="w-full justify-between">
                    Advanced Filters
                    <ChevronDown
                      className={`h-4 w-4 transition-transform ${showAdvanced ? "rotate-180" : ""}`}
                    />
                  </Button>
                </CollapsibleTrigger>
                <CollapsibleContent className="space-y-4 pt-4">
                  {/* Overfetch Multiplier */}
                  <FormField
                    control={form.control}
                    name="overfetch_multiplier"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>
                          Overfetch Multiplier: {field.value}x
                        </FormLabel>
                        <FormControl>
                          <Slider
                            min={1}
                            max={10}
                            step={1}
                            value={[field.value]}
                            onValueChange={([value]) => field.onChange(value)}
                          />
                        </FormControl>
                        <FormDescription>
                          Fetch extra images for client-side filtering
                        </FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  {/* Min Color Score */}
                  <FormField
                    control={form.control}
                    name="min_color_score"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>
                          Min Color Score: {field.value.toFixed(1)}{" "}
                          {field.value === 0 && "(disabled)"}
                        </FormLabel>
                        <FormControl>
                          <Slider
                            min={0}
                            max={1}
                            step={0.1}
                            value={[field.value]}
                            onValueChange={([value]) => field.onChange(value)}
                          />
                        </FormControl>
                        <FormDescription>
                          Color compatibility for e-ink display (0 to disable)
                        </FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  {/* Is Favorite */}
                  <FormField
                    control={form.control}
                    name="is_favorite"
                    render={({ field }) => (
                      <FormItem className="flex flex-row items-start space-x-3 space-y-0">
                        <FormControl>
                          <Checkbox
                            checked={field.value ?? false}
                            onCheckedChange={(
                              checked: boolean | "indeterminate",
                            ) =>
                              field.onChange(
                                checked === true ? true : undefined,
                              )
                            }
                          />
                        </FormControl>
                        <div className="space-y-1 leading-none">
                          <FormLabel>Favorites Only</FormLabel>
                          <FormDescription>
                            Only sync favorited images
                          </FormDescription>
                        </div>
                      </FormItem>
                    )}
                  />

                  {/* Location Filters */}
                  <div className="grid grid-cols-3 gap-2">
                    <FormField
                      control={form.control}
                      name="city"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>City</FormLabel>
                          <FormControl>
                            <Input placeholder="City" {...field} />
                          </FormControl>
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={form.control}
                      name="state"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>State</FormLabel>
                          <FormControl>
                            <Input placeholder="State" {...field} />
                          </FormControl>
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={form.control}
                      name="country"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Country</FormLabel>
                          <FormControl>
                            <Input placeholder="Country" {...field} />
                          </FormControl>
                        </FormItem>
                      )}
                    />
                  </div>

                  {/* Date Range */}
                  <div className="grid grid-cols-2 gap-2">
                    <FormField
                      control={form.control}
                      name="taken_after"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Taken After</FormLabel>
                          <FormControl>
                            <Input type="date" {...field} />
                          </FormControl>
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={form.control}
                      name="taken_before"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Taken Before</FormLabel>
                          <FormControl>
                            <Input type="date" {...field} />
                          </FormControl>
                        </FormItem>
                      )}
                    />
                  </div>

                  {/* Rating */}
                  <FormField
                    control={form.control}
                    name="rating"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>
                          Minimum Rating:{" "}
                          {field.value !== undefined ? field.value : "Any"}
                        </FormLabel>
                        <FormControl>
                          <Slider
                            min={0}
                            max={5}
                            step={1}
                            value={[field.value ?? 0]}
                            onValueChange={([value]) =>
                              field.onChange(value === 0 ? undefined : value)
                            }
                          />
                        </FormControl>
                        <FormDescription>
                          Filter by minimum rating (0-5)
                        </FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </CollapsibleContent>
              </Collapsible>
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

export default AddSyncJob
