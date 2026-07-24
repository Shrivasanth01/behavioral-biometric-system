'use client';

import React from 'react';
import { Building2, Wallet, CreditCard, Landmark } from 'lucide-react';
import { Card, CardBody } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { formatCurrency, maskAccountNumber, cn } from '@/lib/utils';
import type { Account } from '@/types';

interface AccountCardProps {
  account: Account;
  onClick?: () => void;
  selected?: boolean;
}

const typeIcons = {
  savings: Wallet,
  current: Building2,
  credit: CreditCard,
  loan: Landmark,
};

const typeColors = {
  savings: 'from-blue-500 to-blue-700',
  current: 'from-emerald-500 to-emerald-700',
  credit: 'from-purple-500 to-purple-700',
  loan: 'from-orange-500 to-orange-700',
};

const typeLabels = {
  savings: 'Savings Account',
  current: 'Current Account',
  credit: 'Credit Card',
  loan: 'Loan Account',
};

export function AccountCard({ account, onClick, selected }: AccountCardProps) {
  const Icon = typeIcons[account.accountType];

  return (
    <Card
      hover
      onClick={onClick}
      className={cn(
        'overflow-hidden transition-all duration-200',
        selected && 'ring-2 ring-primary-500'
      )}
    >
      <div className={cn('bg-gradient-to-r p-5 text-white', typeColors[account.accountType])}>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Icon className="w-5 h-5 opacity-80" />
            <span className="text-sm font-medium opacity-80">{typeLabels[account.accountType]}</span>
          </div>
          <Badge variant={account.status === 'active' ? 'success' : 'warning'} size="sm">
            {account.status}
          </Badge>
        </div>
        <p className="text-lg font-bold tracking-wider">
          {maskAccountNumber(account.accountNumber)}
        </p>
      </div>
      <CardBody>
        <div className="space-y-3">
          <div>
            <p className="text-xs text-gray-500">Available Balance</p>
            <p className="text-xl font-bold text-navy-900">
              {formatCurrency(account.availableBalance, account.currency)}
            </p>
          </div>
          <div className="flex items-center justify-between text-xs text-gray-500">
            <span>{account.accountName}</span>
            <span>{account.ifscCode}</span>
          </div>
        </div>
      </CardBody>
    </Card>
  );
}
