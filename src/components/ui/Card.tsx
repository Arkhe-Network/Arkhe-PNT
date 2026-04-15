
/**
 * @license
 * Copyright 2026 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */

import React from 'react';

import { cn } from '../../lib/utils';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  title?: string;
  icon?: React.ReactNode;
  action?: React.ReactNode;
  status?: 'normal' | 'warning' | 'critical';
  className?: string;
  children?: React.ReactNode;
}

export function Card({ className, title, icon, action, status = 'normal', children, ...props }: CardProps) {
  return (
    <div 
      className={cn(
        "bg-arkhe-card border border-arkhe-border rounded-xl overflow-hidden flex flex-col relative",
        status === 'warning' && "border-arkhe-orange/50 shadow-[0_0_15px_rgba(255,153,0,0.1)]",
        status === 'critical' && "border-arkhe-red/50 shadow-[0_0_15px_rgba(255,51,102,0.1)]",
        className
      )}
      {...props}
    >
      {status === 'warning' && <div className="absolute top-0 left-0 w-full h-1 bg-arkhe-orange animate-pulse" />}
      {status === 'critical' && <div className="absolute top-0 left-0 w-full h-1 bg-arkhe-red animate-pulse" />}
      
      {(title || icon || action) && (
        <div className="px-4 py-3 border-b border-arkhe-border flex items-center justify-between bg-[#151619]">
          <div className="flex items-center gap-2">
            {icon && <div className="text-arkhe-muted">{icon}</div>}
            {title && <h3 className="font-mono text-xs uppercase tracking-widest text-arkhe-muted">{title}</h3>}
          </div>
          {action && <div>{action}</div>}
        </div>
      )}
      <div className="p-4 flex-1 flex flex-col">
        {children}
      </div>
    </div>
  );
}
