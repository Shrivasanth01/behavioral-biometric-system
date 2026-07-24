'use client';

import React from 'react';
import { cn } from '@/lib/utils';

interface DialogProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  description?: string;
  children?: React.ReactNode;
  footer?: React.ReactNode;
  variant?: 'default' | 'danger';
}

export function Dialog({ isOpen, onClose, title, description, children, footer, variant = 'default' }: DialogProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fade-in">
      <div className="cyber-card w-full max-w-md overflow-hidden animate-slide-up">
        <div className={cn('px-6 py-4', variant === 'danger' ? 'border-b border-red-500/30' : 'border-b border-navy-700/50')}>
          <h2 className="text-lg font-semibold text-gray-100">{title}</h2>
          {description && <p className="mt-1 text-sm text-gray-400">{description}</p>}
        </div>
        {children && <div className="px-6 py-4">{children}</div>}
        {footer && <div className="flex justify-end gap-3 px-6 py-4 border-t border-navy-700/50">{footer}</div>}
      </div>
    </div>
  );
}
