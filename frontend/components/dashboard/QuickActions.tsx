'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { ArrowRightLeft, CreditCard, Smartphone, HandCoins, QrCode, Wallet } from 'lucide-react';
import { cn } from '@/lib/utils';

const actions = [
  { label: 'Transfer', icon: ArrowRightLeft, href: '/dashboard/transfer', color: 'bg-blue-50 text-blue-600' },
  { label: 'Pay Bills', icon: CreditCard, href: '/dashboard/payments', color: 'bg-purple-50 text-purple-600' },
  { label: 'Recharge', icon: Smartphone, href: '/dashboard/payments', color: 'bg-emerald-50 text-emerald-600' },
  { label: 'Apply Loan', icon: HandCoins, href: '/dashboard/loans', color: 'bg-orange-50 text-orange-600' },
  { label: 'UPI Pay', icon: QrCode, href: '/dashboard/transfer', color: 'bg-cyan-50 text-cyan-600' },
  { label: 'Statements', icon: Wallet, href: '/dashboard/accounts', color: 'bg-rose-50 text-rose-600' },
];

export function QuickActions() {
  const router = useRouter();

  return (
    <div className="grid grid-cols-3 md:grid-cols-6 gap-3">
      {actions.map(action => (
        <button
          key={action.label}
          onClick={() => router.push(action.href)}
          className="flex flex-col items-center gap-2 p-4 bg-white rounded-xl border border-gray-200 hover:shadow-md hover:border-gray-300 transition-all duration-200 group"
        >
          <div className={cn('w-10 h-10 rounded-lg flex items-center justify-center transition-transform group-hover:scale-110', action.color)}>
            <action.icon className="w-5 h-5" />
          </div>
          <span className="text-xs font-medium text-gray-700">{action.label}</span>
        </button>
      ))}
    </div>
  );
}
