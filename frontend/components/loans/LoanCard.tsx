'use client';

import React from 'react';
import { Coins as HandCoins, Calendar, TrendingUp } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Badge } from '@/components/ui/Badge';
import { Progress } from '@/components/ui/Progress';
import { formatCurrency, formatDate } from '@/lib/utils';
import type { Loan } from '@/types';

interface LoanCardProps {
  loan: Loan;
  onClick?: () => void;
}

const loanTypeLabels: Record<string, string> = {
  personal: 'Personal Loan',
  home: 'Home Loan',
  car: 'Car Loan',
  education: 'Education Loan',
  business: 'Business Loan',
};

const loanTypeColors: Record<string, string> = {
  personal: 'bg-blue-50 text-blue-600',
  home: 'bg-emerald-50 text-emerald-600',
  car: 'bg-purple-50 text-purple-600',
  education: 'bg-orange-50 text-orange-600',
  business: 'bg-cyan-50 text-cyan-600',
};

export function LoanCard({ loan, onClick }: LoanCardProps) {
  const progressPercent = loan.approvedAmount > 0
    ? Math.min((loan.totalPaid / loan.approvedAmount) * 100, 100)
    : 0;

  return (
    <div
      onClick={onClick}
      className="p-5 bg-white rounded-xl border border-gray-200 hover:shadow-md hover:border-gray-300 cursor-pointer transition-all"
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className={cn('w-10 h-10 rounded-lg flex items-center justify-center', loanTypeColors[loan.loanType] || 'bg-gray-50')}>
            <HandCoins className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-navy-900">{loanTypeLabels[loan.loanType] || loan.loanType}</h3>
            <p className="text-xs text-gray-500">Applied {formatDate(loan.appliedAt)}</p>
          </div>
        </div>
        <Badge variant={
          loan.status === 'active' ? 'success' :
          loan.status === 'approved' ? 'info' :
          loan.status === 'pending' ? 'warning' :
          'neutral'
        }>
          {loan.status}
        </Badge>
      </div>

      <div className="grid grid-cols-2 gap-3 text-sm mb-4">
        <div>
          <p className="text-gray-500">Loan Amount</p>
          <p className="font-semibold text-navy-900">{formatCurrency(loan.approvedAmount)}</p>
        </div>
        <div>
          <p className="text-gray-500">Interest Rate</p>
          <p className="font-semibold text-navy-900">{loan.interestRate}%</p>
        </div>
        <div>
          <p className="text-gray-500">Monthly EMI</p>
          <p className="font-semibold text-navy-900">{formatCurrency(loan.emiAmount)}</p>
        </div>
        <div>
          <p className="text-gray-500">Tenure</p>
          <p className="font-semibold text-navy-900">{loan.tenureMonths} months</p>
        </div>
      </div>

      {loan.status === 'active' && (
        <div>
          <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
            <span>Repayment Progress</span>
            <span>{Math.round(progressPercent)}%</span>
          </div>
          <Progress value={progressPercent} variant="primary" size="sm" />
          {loan.nextEmiDate && (
            <div className="flex items-center gap-1 mt-2 text-xs text-gray-400">
              <Calendar className="w-3 h-3" />
              Next EMI: {formatDate(loan.nextEmiDate)}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
