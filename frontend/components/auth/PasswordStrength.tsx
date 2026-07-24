'use client';

import React from 'react';
import { cn } from '@/lib/utils';

interface PasswordStrengthProps {
  password: string;
}

export function PasswordStrength({ password }: PasswordStrengthProps) {
  const getStrength = (pwd: string): { score: number; label: string; color: string; bg: string } => {
    let score = 0;
    if (pwd.length >= 8) score += 1;
    if (pwd.length >= 12) score += 1;
    if (/[A-Z]/.test(pwd)) score += 1;
    if (/[a-z]/.test(pwd)) score += 1;
    if (/[0-9]/.test(pwd)) score += 1;
    if (/[^A-Za-z0-9]/.test(pwd)) score += 1;

    if (score <= 2) return { score, label: 'Weak', color: 'text-danger-600', bg: 'bg-danger-500' };
    if (score <= 3) return { score, label: 'Fair', color: 'text-warning-600', bg: 'bg-warning-500' };
    if (score <= 4) return { score, label: 'Good', color: 'text-blue-600', bg: 'bg-blue-500' };
    return { score, label: 'Strong', color: 'text-success-600', bg: 'bg-success-500' };
  };

  const strength = getStrength(password);
  const segments = 5;
  const filledSegments = Math.min(strength.score, segments);

  if (!password) return null;

  return (
    <div className="space-y-1.5">
      <div className="flex gap-1">
        {Array.from({ length: segments }).map((_, i) => (
          <div
            key={i}
            className={cn(
              'h-1.5 flex-1 rounded-full transition-all duration-300',
              i < filledSegments ? strength.bg : 'bg-gray-200'
            )}
          />
        ))}
      </div>
      <div className="flex items-center justify-between">
        <p className={cn('text-xs font-medium', strength.color)}>{strength.label}</p>
        <ul className="flex gap-3 text-xs text-gray-400">
          <li className={cn(/[A-Z]/.test(password) && 'text-success-600')}>A-Z</li>
          <li className={cn(/[0-9]/.test(password) && 'text-success-600')}>0-9</li>
          <li className={cn(/[^A-Za-z0-9]/.test(password) && 'text-success-600')}>!@#</li>
        </ul>
      </div>
    </div>
  );
}
