import React from 'react';
export const Progress = ({ value, className }: { value: number, className?: string }) => (
  <div className={className}><div style={{ width: `${value}%` }} /></div>
);
