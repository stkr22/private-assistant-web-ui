import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { Pencil } from "lucide-react"
import { useState } from "react"
import { useForm } from "react-hook-form"
import { z } from "zod"

import {
  DevicesService,
  type DeviceTypePublic,
  type GlobalDevicePublic,
  type RoomPublic,
  type SkillPublic,
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
} from "@/components/ui/dialog"
import { DropdownMenuItem } from "@/components/ui/dropdown-menu"
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

interface EditDeviceProps {
  device: GlobalDevicePublic
  deviceTypes: DeviceTypePublic[]
  rooms: RoomPublic[]
  skills: SkillPublic[]
  onSuccess: () => void
}

const EditDevice = ({
  device,
  deviceTypes,
  rooms,
  skills,
  onSuccess,
}: EditDeviceProps) => {
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      name: device.name,
      device_type_id: device.device_type_id,
      skill_id: device.skill_id,
      room_id: device.room_id ?? "",
      pattern: device.pattern ?? [],
      device_attributes:
        (device.device_attributes as Record<string, unknown>) ?? {},
    },
  })

  const mutation = useMutation({
    mutationFn: (data: FormData) =>
      DevicesService.updateDevice({
        deviceId: device.id,
        requestBody: {
          name: data.name,
          device_type_id: data.device_type_id,
          skill_id: data.skill_id,
          room_id: data.room_id || null,
          pattern: data.pattern?.length ? data.pattern : null,
          device_attributes:
            data.device_attributes &&
            Object.keys(data.device_attributes).length > 0
              ? data.device_attributes
              : null,
        },
      }),
    onSuccess: () => {
      showSuccessToast("Device updated successfully")
      setIsOpen(false)
      onSuccess()
    },
    onError: handleError.bind(showErrorToast),
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["devices"] })
    },
  })

  const onSubmit = (data: FormData) => {
    mutation.mutate(data)
  }

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DropdownMenuItem
        onSelect={(e) => e.preventDefault()}
        onClick={() => setIsOpen(true)}
      >
        <Pencil />
        Edit Device
      </DropdownMenuItem>
      <DialogContent className="sm:max-w-lg max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Edit Device</DialogTitle>
          <DialogDescription>Update the device details.</DialogDescription>
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
                        {deviceTypes.map((dt) => (
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
                        {skills.map((skill) => (
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
                        {rooms.map((room) => (
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

export default EditDevice
