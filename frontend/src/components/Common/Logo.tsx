import { Link } from "@tanstack/react-router"
import { Bot } from "lucide-react"

import { cn } from "@/lib/utils"

interface LogoProps {
  variant?: "full" | "icon" | "responsive"
  className?: string
  asLink?: boolean
}

export function Logo({
  variant = "full",
  className,
  asLink = true,
}: LogoProps) {
  const content =
    variant === "responsive" ? (
      <>
        <div
          className={cn(
            "flex items-center gap-2 group-data-[collapsible=icon]:hidden",
            className,
          )}
        >
          <Bot className="size-6" />
          <span className="font-semibold">Private Assistant</span>
        </div>
        <Bot
          className={cn(
            "size-5 hidden group-data-[collapsible=icon]:block",
            className,
          )}
        />
      </>
    ) : variant === "full" ? (
      <div className={cn("flex items-center gap-2", className)}>
        <Bot className="size-6" />
        <span className="font-semibold">Private Assistant</span>
      </div>
    ) : (
      <Bot className={cn("size-5", className)} />
    )

  if (!asLink) {
    return content
  }

  return <Link to="/">{content}</Link>
}
