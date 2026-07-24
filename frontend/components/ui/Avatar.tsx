'use client';

import React from 'react';
import { cn, getInitials } from '@/lib/utils';
import { User } from 'lucide-react';

interface AvatarProps {
  name?: string;
  imageUrl?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
  status?: 'online' | 'offline' | 'away';
}

export function Avatar({ name, imageUrl, size = 'md', className, status }: AvatarProps) {
  const sizes = {
    sm: 'w-8 h-8 text-xs',
    md: 'w-10 h-10 text-sm',
    lg: 'w-12 h-12 text-base',
    xl: 'w-16 h-16 text-xl',
  };

  const statusSizes = {
    sm: 'w-2.5 h-2.5 border',
    md: 'w-3 h-3 border-2',
    lg: 'w-3.5 h-3.5 border-2',
    xl: 'w-4 h-4 border-2',
  };

  const statusColors = {
    online: 'bg-success-500',
    offline: 'bg-gray-400',
    away: 'bg-warning-500',
  };

  if (imageUrl) {
    return (
      <div className={cn('relative inline-block', className)}>
        <img
          src={imageUrl}
          alt={name || 'Avatar'}
          className={cn('rounded-full object-cover', sizes[size])}
        />
        {status && (
          <span
            className={cn(
              'absolute bottom-0 right-0 rounded-full border-white',
              statusColors[status],
              statusSizes[size]
            )}
          />
        )}
      </div>
    );
  }

  return (
    <div className={cn('relative inline-block', className)}>
      <div
        className={cn(
          'rounded-full bg-primary-100 text-primary-700 flex items-center justify-center font-semibold',
          sizes[size]
        )}
      >
        {name ? getInitials(name) : <User className="w-4 h-4" />}
      </div>
      {status && (
        <span
          className={cn(
            'absolute bottom-0 right-0 rounded-full border-white',
            statusColors[status],
            statusSizes[size]
          )}
        />
      )}
    </div>
  );
}
