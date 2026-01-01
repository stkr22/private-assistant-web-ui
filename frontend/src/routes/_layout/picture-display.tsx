import { useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { Image } from "lucide-react"
import { Suspense } from "react"

import { PictureDisplayService } from "@/client"
import PendingPictureDisplay from "@/components/Pending/PendingPictureDisplay"
import { ImageCard } from "@/components/PictureDisplay/ImageCard"
import { UploadImage } from "@/components/PictureDisplay/UploadImage"

function getImagesQueryOptions() {
  return {
    queryFn: () =>
      PictureDisplayService.readImages({ skip: 0, limit: 100 }),
    queryKey: ["picture-display-images"],
  }
}

export const Route = createFileRoute("/_layout/picture-display")({
  component: PictureDisplay,
  head: () => ({
    meta: [
      {
        title: "Picture Display - Private Assistant",
      },
    ],
  }),
})

function ImageGalleryContent() {
  const { data: images } = useSuspenseQuery(getImagesQueryOptions())

  if (images.data.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center text-center py-12">
        <div className="rounded-full bg-muted p-4 mb-4">
          <Image className="h-8 w-8 text-muted-foreground" />
        </div>
        <h3 className="text-lg font-semibold">No images yet</h3>
        <p className="text-muted-foreground mb-4">
          Upload your first image to get started
        </p>
        <UploadImage />
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
      {images.data.map((image) => (
        <ImageCard key={image.id} image={image} />
      ))}
    </div>
  )
}

function ImageGallery() {
  return (
    <Suspense fallback={<PendingPictureDisplay />}>
      <ImageGalleryContent />
    </Suspense>
  )
}

function PictureDisplay() {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Picture Display</h1>
          <p className="text-muted-foreground">
            Manage images for the digital picture frame
          </p>
        </div>
        <UploadImage />
      </div>
      <ImageGallery />
    </div>
  )
}
