import * as React from "react"
import { cn } from "../../lib/utils"
import { ChevronDown } from "lucide-react"

export const Select = ({ children, ...props }: any) => (
  <div className="relative inline-block w-full">{children}</div>
)

export const SelectTrigger = ({ className, children, ...props }: any) => (
  <button
    className={cn(
      "flex h-9 w-full items-center justify-between rounded-md border border-arkhe-border bg-transparent px-3 py-2 text-sm shadow-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-arkhe-cyan disabled:cursor-not-allowed disabled:opacity-50",
      className
    )}
    {...props}
  >
    {children}
    <ChevronDown className="h-4 w-4 opacity-50" />
  </button>
)

export const SelectValue = ({ children, ...props }: any) => (
  <span className="pointer-events-none" {...props}>{children}</span>
)

export const SelectContent = ({ className, children, ...props }: any) => (
  <div
    className={cn(
      "absolute z-50 min-w-[8rem] overflow-hidden rounded-md border border-arkhe-border bg-[#0a0a0c] text-popover-foreground shadow-md data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95",
      className
    )}
    {...props}
  >
    <div className="p-1">{children}</div>
  </div>
)

export const SelectItem = ({ className, children, ...props }: any) => (
  <div
    className={cn(
      "relative flex w-full cursor-default select-none items-center rounded-sm py-1.5 pl-2 pr-8 text-sm outline-none focus:bg-arkhe-cyan/20 focus:text-arkhe-cyan data-[disabled]:pointer-events-none data-[disabled]:opacity-50",
      className
    )}
    {...props}
  >
    {children}
  </div>
)
