import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { Pencil } from "lucide-react"
import { useState } from "react"
import { useForm } from "react-hook-form"
import { z } from "zod"

import { PictureDisplayService, type PictureDisplayImagePublic } from "@/client"
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
import { LoadingButton } from "@/components/ui/loading-button"
import { Slider } from "@/components/ui/slider"
import { Textarea } from "@/components/ui/textarea"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

const formSchema = z.object({
  title: z.string().max(255).optional(),
  description: z.string().max(1000).optional(),
  tags: z.string().max(500).optional(),
  display_duration_seconds: z.number().min(5).max(300),
  priority: z.number().min(1).max(10),
})

type FormData = z.infer<typeof formSchema>

interface EditImageProps {
  image: PictureDisplayImagePublic
  onSuccess: () => void
}

export function EditImage({ image, onSuccess }: EditImageProps) {
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    mode: "onBlur",
    defaultValues: {
      title: image.title ?? "",
      description: image.description ?? "",
      tags: image.tags ?? "",
      display_duration_seconds: image.display_duration_seconds,
      priority: image.priority,
    },
  })

  const mutation = useMutation({
    mutationFn: (data: FormData) =>
      PictureDisplayService.updateImage({
        imageId: image.id,
        requestBody: {
          title: data.title || null,
          description: data.description || null,
          tags: data.tags || null,
          display_duration_seconds: data.display_duration_seconds,
          priority: data.priority,
        },
      }),
    onSuccess: () => {
      showSuccessToast("Image updated successfully")
      setIsOpen(false)
      onSuccess()
    },
    onError: handleError.bind(showErrorToast),
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["picture-display-images"] })
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
        <Pencil className="mr-2 h-4 w-4" />
        Edit
      </DropdownMenuItem>
      <DialogContent className="sm:max-w-md max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Edit Image</DialogTitle>
          <DialogDescription>
            Update the image metadata. The image file cannot be changed.
          </DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)}>
            <div className="grid gap-4 py-4">
              <FormField
                control={form.control}
                name="title"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Title</FormLabel>
                    <FormControl>
                      <Input placeholder="Image title" {...field} />
                    </FormControl>
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
                        placeholder="Image description"
                        className="resize-none"
                        rows={3}
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="tags"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Tags</FormLabel>
                    <FormControl>
                      <Input
                        placeholder="nature, landscape, sunset"
                        {...field}
                      />
                    </FormControl>
                    <FormDescription>Comma-separated tags</FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="display_duration_seconds"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Display Duration: {field.value}s</FormLabel>
                    <FormControl>
                      <Slider
                        value={[field.value]}
                        onValueChange={(v: number[]) => field.onChange(v[0])}
                        min={5}
                        max={300}
                        step={5}
                      />
                    </FormControl>
                    <FormDescription>
                      How long to display (5-300 seconds)
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="priority"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Priority: {field.value}</FormLabel>
                    <FormControl>
                      <Slider
                        value={[field.value]}
                        onValueChange={(v: number[]) => field.onChange(v[0])}
                        min={1}
                        max={10}
                        step={1}
                      />
                    </FormControl>
                    <FormDescription>
                      Higher priority images appear more often (1-10)
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
