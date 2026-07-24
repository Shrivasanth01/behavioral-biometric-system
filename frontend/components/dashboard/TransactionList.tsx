'use client';

import React from 'react';
import { ArrowDownToLine, ArrowUpFromLine, ArrowRightLeft, CreditCard, Smartphone, Banknote, RotateCcw, Receipt, Percent } from 'lucide-react';
import { formatCurrency, formatDateTime, getStatusColor, cn } from '@/lib/utils';
import type { Transaction } from '@/types';

interface TransactionListProps {
  transactions: Transaction[];
  showViewAll?: boolean;
  onViewAll?: () => void;
  onTransactionClick?: (txn: Transaction) => void;
  limit?: number;
}

const categoryIcons: Record<string, React.ReactNode> = {
  transfer: <ArrowRightLeft className="w-4 h-4" />,
  payment: <CreditCard className="w-4 h-4" />,
  recharge: <Smartphone className="w-4 h-4" />,
  withdrawal: <Banknote className="w-4 h-4" />,
  deposit: <ArrowDownToLine className="w-4 h-4" />,
  refund: <RotateCcw className="w-4 h-4" />,
  fee: <Receipt className="w-4 h-4" />,
  interest: <Percent className="w-4 h-4" />,
};

const categoryBg: Record<string, string> = {
  transfer: 'bg-blue-50 text-blue-600',
  payment: 'bg-purple-50 text-purple-600',
  recharge: 'bg-emerald-50 text-emerald-600',
  withdrawal: 'bg-red-50 text-red-600',
  deposit: 'bg-green-50 text-green-600',
  refund: 'bg-orange-50 text-orange-600',
  fee: 'bg-gray-50 text-gray-600',
  interest: 'bg-cyan-50 text-cyan-600',
};

export function TransactionList({ transactions, showViewAll, onViewAll, onTransactionClick, limit }: TransactionListProps) {
  const displayTransactions = limit ? transactions.slice(0, limit) : transactions;

  if (displayTransactions.length === 0) {
    return (
      <div className="text-center py-8">
        <ArrowRightLeft className="w-12 h-12 text-gray-300 mx-auto mb-3" />
        <p className="text-gray-500">No transactions found</p>
      </div>
    );
  }

  return (
    <div className="space-y-1">
      {displayTransactions.map((txn, i) => (
        <div
          key={txn.id}
          onClick={() => onTransactionClick?.(txn)}
          className={cn(
            'flex items-center gap-3 p-3 rounded-lg transition-colors',
            onTransactionClick && 'cursor-pointer hover:bg-gray-50'
          )}
        >
          <div className={cn('w-9 h-9 rounded-lg flex items-center justify-center shrink-0', categoryBg[txn.category] || 'bg-gray-50')}>
            {categoryIcons[txn.category] || <ArrowRightLeft className="w-4 h-4" />}
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium text-navy-900 truncate">{txn.description}</p>
              <span className={cn(
                'text-sm font-semibold',
                txn.type === 'credit' ? 'text-success-600' : 'text-navy-900'
              )}>
                {txn.type === 'credit' ? '+' : '-'}{formatCurrency(txn.amount, txn.currency)}
              </span>
            </div>
            <div className="flex items-center gap-2 mt-0.5">
              <span className="text-xs text-gray-500">{formatDateTime(txn.transactionDate)}</span>
              <span className={cn('text-xs px-1.5 py-0.5 rounded-full', getStatusColor(txn.status))}>
                {txn.status}
              </span>
            </div>
          </div>
        </div>
      ))}
      {showViewAll && onViewAll && (
        <button
          onClick={onViewAll}
          className="w-full py-2 text-sm text-primary-600 hover:text-primary-700 font-medium text-center"
        >
          View All Transactions
        </button>
      )}
    </div>
  );
}
