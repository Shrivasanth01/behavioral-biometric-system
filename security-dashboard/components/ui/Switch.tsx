'use client';

import React, { useState } from 'react';
import { cn } from '@/lib/utils';

interface SwitchProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  label?: string;
  disabled?: boolean;
  size?: 'sm' | 'md';
}

export function Switch({ checked, onChange, label, disabled, size = 'md' }: SwitchProps) {
  const sizes = {
    sm: 'w-8 h-4',
    md: 'w-10 h-5',
  };

  const thumbSizes = {
    sm: 'w-3 h-3',
    md: 'w-4 h-4',
  };

  return (
    <label className={cn('inline-flex items-center gap-3', disabled && 'opacity-50 cursor-not-allowed')}>
      <button
        type="button"
        role="switch"
        disabled={disabled}
        onClick={() => onChange(!checked)}
        className={cn(
          'relative inline-flex shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200',
          'focus:outline-none focus:ring-2 focus:ring-cyber-500/50 focus:ring-offset-1 focus:ring-offset-navy-900',
          sizes[size],
          checked ? 'bg-cyber-600' : 'bg-navy-700'
        )}
      >
        <span
          className={cn(
            'pointer-events-none inline-block rounded-full bg-white shadow transform ring-0 transition duration-200',
            thumbSizes[size],
            checked ? 'translate-x-5' : 'translate-x-0'
          )}
        />
      </button>
      {label && <span className="text-sm text-gray-400">{label}</span>}
    </label>
  );
}
