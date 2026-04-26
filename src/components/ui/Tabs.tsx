import * as React from "react"
import { cn } from "../../lib/utils"

export const Tabs = ({ className, children, ...props }: any) => (
  <div className={cn("w-full", className)} {...props}>{children}</div>
)

export const TabsList = ({ className, children, ...props }: any) => (
  <div
    className={cn(
      "inline-flex h-9 items-center justify-center rounded-lg bg-black/40 p-1 text-muted-foreground",
      className
    )}
    {...props}
  >
    {children}
  </div>
)

export const TabsTrigger = ({ className, children, ...props }: any) => (
  <button
    className={cn(
      "inline-flex items-center justify-center whitespace-nowrap rounded-md px-3 py-1 text-sm font-medium ring-offset-background transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-arkhe-cyan focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 data-[state=active]:bg-arkhe-cyan data-[state=active]:text-black data-[state=active]:shadow-sm",
      className
    )}
    {...props}
  >
    {children}
  </button>
)

export const TabsContent = ({ className, children, ...props }: any) => (
  <div
    className={cn(
      "mt-2 ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-arkhe-cyan focus-visible:ring-offset-2",
      className
    )}
    {...props}
  >
    {children}
  </div>
)
