'use client';

import React, { useState } from 'react';
import { HandCoins, Calculator } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { EMICalculator } from './EMICalculator';
import { calculateEMI, formatCurrency } from '@/lib/utils';

interface LoanApplicationProps {
  onSubmit: (data: { loanType: string; amount: number; tenureMonths: number }) => void;
  isSubmitting?: boolean;
}

const LOAN_TYPES = [
  { value: 'personal', label: 'Personal Loan', description: 'For personal expenses, travel, or debt consolidation', rate: 12.5 },
  { value: 'home', label: 'Home Loan', description: 'For purchasing or renovating a home', rate: 8.5 },
  { value: 'car', label: 'Car Loan', description: 'For purchasing a new or used car', rate: 9.5 },
  { value: 'education', label: 'Education Loan', description: 'For higher education expenses', rate: 10.5 },
  { value: 'business', label: 'Business Loan', description: 'For business expansion or working capital', rate: 13.5 },
];

export function LoanApplication({ onSubmit, isSubmitting }: LoanApplicationProps) {
  const [loanType, setLoanType] = useState('personal');
  const [amount, setAmount] = useState(500000);
  const [tenureMonths, setTenureMonths] = useState(36);
  const [showCalculator, setShowCalculator] = useState(false);

  const selectedLoan = LOAN_TYPES.find(l => l.value === loanType);
  const estimatedEMI = calculateEMI(amount, selectedLoan?.rate || 12, tenureMonths);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({ loanType, amount, tenureMonths });
  };

  return (
    <div className="space-y-6">
      {showCalculator ? (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-navy-900">EMI Calculator</h3>
            <button
              onClick={() => setShowCalculator(false)}
              className="text-sm text-primary-600 hover:text-primary-700"
            >
              Back to Application
            </button>
          </div>
          <EMICalculator
            onApply={(amt, tenure) => {
              setAmount(amt);
              setTenureMonths(tenure);
              setShowCalculator(false);
            }}
          />
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="label">Loan Type</label>
            <div className="grid grid-cols-1 gap-2">
              {LOAN_TYPES.map(lt => (
                <button
                  key={lt.value}
                  type="button"
                  onClick={() => setLoanType(lt.value)}
                  className={`text-left p-3 rounded-lg border transition-all ${
                    loanType === lt.value
                      ? 'border-primary-500 bg-primary-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <p className="text-sm font-medium text-navy-900">{lt.label}</p>
                  <p className="text-xs text-gray-500 mt-0.5">{lt.description}</p>
                  <p className="text-xs text-primary-600 mt-1">Interest: {lt.rate}% p.a.</p>
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="label">Loan Amount (₹)</label>
            <div className="relative">
              <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500">₹</span>
              <input
                type="number"
                value={amount}
                onChange={e => setAmount(parseInt(e.target.value) || 0)}
                className="input-field pl-8"
                min={10000}
                max={10000000}
              />
            </div>
            <div className="flex justify-between text-xs text-gray-400 mt-1">
              <span>Min: ₹10,000</span>
              <span>Max: ₹1,00,00,000</span>
            </div>
          </div>

          <div>
            <label className="label">Tenure (Months)</label>
            <input
              type="range"
              min={6}
              max={240}
              step={6}
              value={tenureMonths}
              onChange={e => setTenureMonths(parseInt(e.target.value))}
              className="w-full accent-primary-600"
            />
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">6 months</span>
              <span className="font-semibold text-primary-700">{tenureMonths} months ({(tenureMonths / 12).toFixed(1)} years)</span>
              <span className="text-gray-500">240 months</span>
            </div>
          </div>

          <div className="p-4 bg-gray-50 rounded-xl space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Estimated Monthly EMI</span>
              <span className="text-lg font-bold text-primary-700">{formatCurrency(estimatedEMI)}</span>
            </div>
            <p className="text-xs text-gray-400">
              @ {selectedLoan?.rate || 12}% p.a. for {tenureMonths} months
            </p>
          </div>

          <div className="flex gap-3">
            <Button
              type="button"
              variant="secondary"
              className="flex-1"
              onClick={() => setShowCalculator(true)}
              leftIcon={<Calculator className="w-4 h-4" />}
            >
              Calculate EMI
            </Button>
            <Button
              type="submit"
              className="flex-1"
              isLoading={isSubmitting}
            >
              Submit Application
            </Button>
          </div>
        </form>
      )}
    </div>
  );
}
