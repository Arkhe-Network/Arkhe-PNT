import React from 'react';
export const Badge = ({ children, className, variant }: { children: React.ReactNode, className?: string, variant?: string }) => (
  <span className={className}>{children}</span>
);
