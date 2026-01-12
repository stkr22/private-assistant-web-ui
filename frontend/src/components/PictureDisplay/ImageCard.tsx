import { useQuery } from "@tanstack/react-query"

import { type ImagePublic, PictureDisplayService } from "@/client"
import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { ImageActionsMenu } from "./ImageActionsMenu"

interface ImageCardProps {
  image: ImagePublic
}

export function ImageCard({ image }: ImageCardProps) {
  const { data: urlData, isLoading } = useQuery({
    queryFn: () => PictureDisplayService.getImageUrl({ imageId: image.id }),
    queryKey: ["image-url", image.id],
    staleTime: 55 * 60 * 1000, // 55 minutes (before 1hr expiry)
  })

  return (
    <Card className="overflow-hidden">
      <CardHeader className="p-0">
        <div className="aspect-video relative overflow-hidden bg-muted">
          {isLoading ? (
            <Skeleton className="w-full h-full" />
          ) : urlData ? (
            <img
              src={urlData.url}
              alt={image.title || image.source_name}
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-muted-foreground">
              Failed to load
            </div>
          )}
        </div>
      </CardHeader>
      <CardContent className="p-4">
        <h3 className="font-medium truncate">
          {image.title || image.source_name}
        </h3>
        {image.description && (
          <p className="text-sm text-muted-foreground line-clamp-2 mt-1">
            {image.description}
          </p>
        )}
        <div className="flex items-center gap-2 mt-2 text-xs text-muted-foreground">
          <span>Priority: {image.priority}</span>
          <span>|</span>
          <span>{Math.round(image.display_duration_seconds / 60)} min</span>
        </div>
        {image.tags && (
          <div className="flex flex-wrap gap-1 mt-2">
            {image.tags.split(",").map((tag: string, idx: number) => (
              <span
                key={idx}
                className="inline-flex items-center rounded-full bg-secondary px-2 py-0.5 text-xs"
              >
                {tag.trim()}
              </span>
            ))}
          </div>
        )}
      </CardContent>
      <CardFooter className="p-4 pt-0 flex justify-end">
        <ImageActionsMenu image={image} />
      </CardFooter>
    </Card>
  )
}
