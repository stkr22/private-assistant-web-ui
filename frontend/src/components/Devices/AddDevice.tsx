import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { Plus } from "lucide-react"
import { useState } from "react"
import { useForm } from "react-hook-form"
import { z } from "zod"

import {
  DevicesService,
  DeviceTypesService,
  type GlobalDeviceCreate,
  MonitoringService,
  RoomsService,
} from "@/client"
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
import { KeyValueEditor } from "@/components/ui/key-value-editor"
import { LoadingButton } from "@/components/ui/loading-button"
import { PatternArrayInput } from "@/components/ui/pattern-array-input"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

const formSchema = z.object({
  name: z.string().min(1, { message: "Name is required" }),
  device_type_id: z.string().min(1, { message: "Device type is required" }),
  skill_id: z.string().min(1, { message: "Skill is required" }),
  room_id: z.string().optional(),
  pattern: z.array(z.string()).optional(),
  device_attributes: z.record(z.string(), z.unknown()).optional(),
})

type FormData = z.infer<typeof formSchema>

const AddDevice = () => {
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const { data: deviceTypes } = useQuery({
    queryFn: () => DeviceTypesService.readDeviceTypes({ skip: 0, limit: 100 }),
    queryKey: ["device-types"],
  })

  const { data: rooms } = useQuery({
    queryFn: () => RoomsService.readRooms({ skip: 0, limit: 100 }),
    queryKey: ["rooms"],
  })

  const { data: skills } = useQuery({
    queryFn: () => MonitoringService.readSkills(),
    queryKey: ["skills"],
  })

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      name: "",
      device_type_id: "",
      skill_id: "",
      room_id: "",
      pattern: [],
      device_attributes: {},
    },
  })

  const mutation = useMutation({
    mutationFn: (data: GlobalDeviceCreate) =>
      DevicesService.createDevice({ requestBody: data }),
    onSuccess: () => {
      showSuccessToast("Device created successfully")
      form.reset()
      setIsOpen(false)
    },
    onError: handleError.bind(showErrorToast),
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["devices"] })
    },
  })

  const onSubmit = (data: FormData) => {
    const createData: GlobalDeviceCreate = {
      name: data.name,
      device_type_id: data.device_type_id,
      skill_id: data.skill_id,
      room_id: data.room_id || null,
      pattern: data.pattern?.length ? data.pattern : null,
      device_attributes:
        data.device_attributes && Object.keys(data.device_attributes).length > 0
          ? data.device_attributes
          : null,
    }
    mutation.mutate(createData)
  }

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button className="my-4">
          <Plus className="mr-2" />
          Add Device
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-lg max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Add Device</DialogTitle>
          <DialogDescription>
            Fill in the details to add a new device.
          </DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)}>
            <div className="grid gap-4 py-4">
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
                        placeholder="Device name"
                        type="text"
                        {...field}
                        required
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="device_type_id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>
                      Device Type <span className="text-destructive">*</span>
                    </FormLabel>
                    <Select onValueChange={field.onChange} value={field.value}>
                      <FormControl>
                        <SelectTrigger className="w-full">
                          <SelectValue placeholder="Select a device type" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {deviceTypes?.data.map((dt) => (
                          <SelectItem key={dt.id} value={dt.id}>
                            {dt.name}
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
                name="skill_id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>
                      Skill <span className="text-destructive">*</span>
                    </FormLabel>
                    <Select onValueChange={field.onChange} value={field.value}>
                      <FormControl>
                        <SelectTrigger className="w-full">
                          <SelectValue placeholder="Select a skill" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {skills?.data.map((skill) => (
                          <SelectItem key={skill.id} value={skill.id}>
                            {skill.name}
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
                name="room_id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Room</FormLabel>
                    <Select onValueChange={field.onChange} value={field.value}>
                      <FormControl>
                        <SelectTrigger className="w-full">
                          <SelectValue placeholder="Select a room (optional)" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {rooms?.data.map((room) => (
                          <SelectItem key={room.id} value={room.id}>
                            {room.name}
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
                name="pattern"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Patterns</FormLabel>
                    <FormControl>
                      <PatternArrayInput
                        value={field.value ?? []}
                        onChange={field.onChange}
                        placeholder="Add voice matching pattern..."
                      />
                    </FormControl>
                    <FormDescription>
                      Voice patterns for matching this device
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="device_attributes"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Custom Attributes</FormLabel>
                    <FormControl>
                      <KeyValueEditor
                        value={field.value ?? {}}
                        onChange={field.onChange}
                      />
                    </FormControl>
                    <FormDescription>
                      Custom key-value pairs for this device
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

export default AddDevice
