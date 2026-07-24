'use client';

import React from 'react';
import { AlertTriangle, CheckCircle, Info, X } from 'lucide-react';
import { Button } from './Button';
import { cn } from '@/lib/utils';
import { Modal } from './Modal';

interface DialogProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm?: () => void;
  title: string;
  message: string;
  variant?: 'confirm' | 'alert' | 'success' | 'info';
  confirmLabel?: string;
  cancelLabel?: string;
  isLoading?: boolean;
}

export function Dialog({
  isOpen,
  onClose,
  onConfirm,
  title,
  message,
  variant = 'info',
  confirmLabel = 'Confirm',
  cancelLabel = 'Cancel',
  isLoading = false,
}: DialogProps) {
  const icons = {
    confirm: AlertTriangle,
    alert: X,
    success: CheckCircle,
    info: Info,
  };
  const Icon = icons[variant];

  const iconColors = {
    confirm: 'bg-warning-50 text-warning-600',
    alert: 'bg-danger-50 text-danger-600',
    success: 'bg-success-50 text-success-600',
    info: 'bg-blue-50 text-blue-600',
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="sm" showClose={false}>
      <div className="text-center">
        <div className={cn('w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4', iconColors[variant])}>
          <Icon className="w-6 h-6" />
        </div>
        <h3 className="text-lg font-semibold text-navy-900 mb-2">{title}</h3>
        <p className="text-sm text-gray-500 mb-6">{message}</p>
        <div className="flex gap-3 justify-center">
          <Button variant="secondary" onClick={onClose} disabled={isLoading}>
            {cancelLabel}
          </Button>
          {onConfirm && (
            <Button
              variant={variant === 'alert' ? 'danger' : 'primary'}
              onClick={onConfirm}
              isLoading={isLoading}
            >
              {confirmLabel}
            </Button>
          )}
        </div>
      </div>
    </Modal>
  );
}
