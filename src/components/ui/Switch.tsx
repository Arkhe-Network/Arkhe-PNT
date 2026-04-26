import * as React from "react"
import { cn } from "../../lib/utils"

export const Switch = ({ className, checked, ...props }: any) => (
  <button
    role="switch"
    aria-checked={checked}
    className={cn(
      "peer inline-flex h-5 w-9 shrink-0 cursor-pointer items-center rounded-full border-2 border-transparent transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-arkhe-cyan focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",
      checked ? "bg-arkhe-cyan" : "bg-white/10",
      className
    )}
    {...props}
  >
    <span
      className={cn(
        "pointer-events-none block h-4 w-4 rounded-full bg-white shadow-lg ring-0 transition-transform",
        checked ? "translate-x-4" : "translate-x-0"
      )}
    />
  </button>
)
