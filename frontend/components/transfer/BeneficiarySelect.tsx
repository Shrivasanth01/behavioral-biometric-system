'use client';

import React from 'react';
import { User, Phone, Banknote } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { Beneficiary } from '@/types';

interface BeneficiarySelectProps {
  beneficiaries: Beneficiary[];
  selectedId: string;
  onSelect: (beneficiary: Beneficiary) => void;
}

export function BeneficiarySelect({ beneficiaries, selectedId, onSelect }: BeneficiarySelectProps) {
  if (beneficiaries.length === 0) {
    return (
      <div className="text-center py-6 text-gray-500">
        <User className="w-8 h-8 mx-auto mb-2 opacity-50" />
        <p className="text-sm">No beneficiaries added yet</p>
      </div>
    );
  }

  return (
    <div className="space-y-2 max-h-60 overflow-y-auto">
      {beneficiaries.map(ben => (
        <button
          key={ben.id}
          type="button"
          onClick={() => onSelect(ben)}
          className={cn(
            'w-full flex items-center gap-3 p-3 rounded-lg border text-left transition-all',
            selectedId === ben.id
              ? 'border-primary-500 bg-primary-50'
              : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
          )}
        >
          <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center shrink-0">
            <span className="text-sm font-semibold text-primary-700">
              {ben.name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)}
            </span>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-navy-900 truncate">{ben.name}</p>
            <p className="text-xs text-gray-500 truncate">{ben.accountNumber} • {ben.bankName}</p>
            {ben.nickname && <p className="text-xs text-primary-600">{ben.nickname}</p>}
          </div>
          <div className="text-right shrink-0">
            <p className="text-xs text-gray-400">Limit</p>
            <p className="text-xs font-medium">₹{ben.maxTransferLimit.toLocaleString()}</p>
          </div>
        </button>
      ))}
    </div>
  );
}
