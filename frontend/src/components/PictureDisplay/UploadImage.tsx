import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { ImagePlus, Upload } from "lucide-react"
import { useRef, useState } from "react"
import { useForm } from "react-hook-form"
import { z } from "zod"

import { PictureDisplayService } from "@/client"
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
import { LoadingButton } from "@/components/ui/loading-button"
import { Slider } from "@/components/ui/slider"
import { Textarea } from "@/components/ui/textarea"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

const MAX_FILE_SIZE = 10 * 1024 * 1024 // 10MB

const formSchema = z.object({
  file: z
    .instanceof(File, { message: "Please select an image file" })
    .refine((f) => f.size <= MAX_FILE_SIZE, "File must be less than 10MB")
    .refine((f) => f.type.startsWith("image/"), "File must be an image"),
  title: z.string().max(255).optional(),
  description: z.string().max(1000).optional(),
  tags: z.string().max(500).optional(),
  display_duration_seconds: z.number().min(5).max(300),
  priority: z.number().min(1).max(10),
})

type FormData = z.infer<typeof formSchema>

export function UploadImage() {
  const [isOpen, setIsOpen] = useState(false)
  const [preview, setPreview] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    mode: "onBlur",
    defaultValues: {
      title: "",
      description: "",
      tags: "",
      display_duration_seconds: 30,
      priority: 5,
    },
  })

  const mutation = useMutation({
    mutationFn: (data: FormData) =>
      PictureDisplayService.uploadImage({
        formData: {
          file: data.file,
          title: data.title || null,
          description: data.description || null,
          tags: data.tags || null,
          display_duration_seconds: data.display_duration_seconds,
          priority: data.priority,
        },
      }),
    onSuccess: () => {
      showSuccessToast("Image uploaded successfully")
      form.reset()
      setPreview(null)
      setIsOpen(false)
    },
    onError: handleError.bind(showErrorToast),
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["picture-display-images"] })
    },
  })

  const onSubmit = (data: FormData) => {
    mutation.mutate(data)
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      form.setValue("file", file, { shouldValidate: true })
      const url = URL.createObjectURL(file)
      setPreview(url)
    }
  }

  const handleDialogChange = (open: boolean) => {
    setIsOpen(open)
    if (!open) {
      form.reset()
      setPreview(null)
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={handleDialogChange}>
      <DialogTrigger asChild>
        <Button>
          <Upload className="mr-2 h-4 w-4" />
          Upload Image
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-lg max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Upload Image</DialogTitle>
          <DialogDescription>
            Upload a new image to the picture display.
          </DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)}>
            <div className="grid gap-4 py-4">
              <FormField
                control={form.control}
                name="file"
                render={() => (
                  <FormItem>
                    <FormLabel>
                      Image <span className="text-destructive">*</span>
                    </FormLabel>
                    <FormControl>
                      <button
                        type="button"
                        className="w-full border-2 border-dashed rounded-lg p-4 text-center cursor-pointer hover:border-primary transition-colors"
                        onClick={() => fileInputRef.current?.click()}
                      >
                        <input
                          ref={fileInputRef}
                          type="file"
                          accept="image/*"
                          className="hidden"
                          onChange={handleFileChange}
                        />
                        {preview ? (
                          <img
                            src={preview}
                            alt="Preview"
                            className="max-h-48 mx-auto rounded"
                          />
                        ) : (
                          <div className="py-8 text-muted-foreground">
                            <ImagePlus className="h-10 w-10 mx-auto mb-2" />
                            <p>Click to select an image</p>
                            <p className="text-xs mt-1">Max 10MB</p>
                          </div>
                        )}
                      </button>
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="title"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Title</FormLabel>
                    <FormControl>
                      <Input placeholder="Image title (optional)" {...field} />
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
                        placeholder="Image description (optional)"
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
                Upload
              </LoadingButton>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}
