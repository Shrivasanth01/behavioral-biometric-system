'use client';

import React from 'react';
import { cn } from '@/lib/utils';

interface SwitchProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  label?: string;
  description?: string;
  disabled?: boolean;
  id?: string;
}

export function Switch({ checked, onChange, label, description, disabled, id }: SwitchProps) {
  const switchId = id || `switch_${Math.random().toString(36).substring(2, 9)}`;

  return (
    <label htmlFor={switchId} className={cn('flex items-center gap-3 cursor-pointer', disabled && 'opacity-50 cursor-not-allowed')}>
      <div className="relative">
        <input
          id={switchId}
          type="checkbox"
          checked={checked}
          onChange={(e) => onChange(e.target.checked)}
          disabled={disabled}
          className="sr-only"
        />
        <div
          className={cn(
            'w-10 h-6 rounded-full transition-colors duration-200',
            checked ? 'bg-primary-600' : 'bg-gray-300'
          )}
        >
          <div
            className={cn(
              'absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform duration-200',
              checked && 'translate-x-4'
            )}
          />
        </div>
      </div>
      {(label || description) && (
        <div>
          {label && <span className="text-sm font-medium text-navy-700">{label}</span>}
          {description && <p className="text-xs text-gray-500">{description}</p>}
        </div>
      )}
    </label>
  );
}
