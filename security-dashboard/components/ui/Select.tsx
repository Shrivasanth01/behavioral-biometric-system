'use client';

import React from 'react';
import { cn } from '@/lib/utils';

interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  options: { value: string; label: string }[];
  placeholder?: string;
}

export function Select({ label, options, placeholder, className, ...props }: SelectProps) {
  return (
    <div className="space-y-1.5">
      {label && <label className="block text-sm font-medium text-gray-400">{label}</label>}
      <select
        className={cn(
          'w-full rounded-lg border border-navy-700/60 bg-navy-800/80 px-3 py-2 text-sm text-gray-100',
          'focus:border-cyber-500 focus:outline-none focus:ring-1 focus:ring-cyber-500/50',
          'transition-all duration-200 appearance-none cursor-pointer',
          className
        )}
        {...props}
      >
        {placeholder && <option value="" className="text-gray-500">{placeholder}</option>}
        {options.map((opt) => (
          <option key={opt.value} value={opt.value} className="bg-navy-800">
            {opt.label}
          </option>
        ))}
      </select>
    </div>
  );
}
