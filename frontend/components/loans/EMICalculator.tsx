'use client';

import React, { useState, useMemo } from 'react';
import { Calculator } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { formatCurrency, calculateEMI, getTotalInterest } from '@/lib/utils';

interface EMICalculatorProps {
  onApply?: (amount: number, tenureMonths: number) => void;
}

export function EMICalculator({ onApply }: EMICalculatorProps) {
  const [amount, setAmount] = useState(500000);
  const [rate, setRate] = useState(12);
  const [tenure, setTenure] = useState(36);

  const emi = useMemo(() => calculateEMI(amount, rate, tenure), [amount, rate, tenure]);
  const totalInterest = useMemo(() => getTotalInterest(amount, rate, tenure), [amount, rate, tenure]);
  const totalPayment = amount + totalInterest;

  return (
    <div className="space-y-5">
      <div>
        <label className="label">Loan Amount (₹)</label>
        <input
          type="range"
          min={10000}
          max={10000000}
          step={10000}
          value={amount}
          onChange={e => setAmount(parseInt(e.target.value))}
          className="w-full accent-primary-600"
        />
        <div className="flex justify-between text-sm">
          <span className="text-gray-500">₹10,000</span>
          <span className="font-semibold text-primary-700">{formatCurrency(amount)}</span>
          <span className="text-gray-500">₹1 Cr</span>
        </div>
      </div>

      <div>
        <label className="label">Interest Rate (% p.a.)</label>
        <input
          type="range"
          min={5}
          max={24}
          step={0.5}
          value={rate}
          onChange={e => setRate(parseFloat(e.target.value))}
          className="w-full accent-primary-600"
        />
        <div className="flex justify-between text-sm">
          <span className="text-gray-500">5%</span>
          <span className="font-semibold text-primary-700">{rate}%</span>
          <span className="text-gray-500">24%</span>
        </div>
      </div>

      <div>
        <label className="label">Tenure (Months)</label>
        <input
          type="range"
          min={6}
          max={240}
          step={6}
          value={tenure}
          onChange={e => setTenure(parseInt(e.target.value))}
          className="w-full accent-primary-600"
        />
        <div className="flex justify-between text-sm">
          <span className="text-gray-500">6 months</span>
          <span className="font-semibold text-primary-700">{tenure} months</span>
          <span className="text-gray-500">240 months</span>
        </div>
      </div>

      <div className="p-4 bg-primary-50 rounded-xl space-y-3">
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-600">Monthly EMI</span>
          <span className="text-xl font-bold text-primary-700">{formatCurrency(emi)}</span>
        </div>
        <div className="h-px bg-primary-200" />
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">Total Interest Payable</span>
          <span className="font-medium text-navy-900">{formatCurrency(totalInterest)}</span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">Total Payment</span>
          <span className="font-medium text-navy-900">{formatCurrency(totalPayment)}</span>
        </div>
      </div>

      {onApply && (
        <Button className="w-full" onClick={() => onApply(amount, tenure)}>
          Apply for This Loan
        </Button>
      )}
    </div>
  );
}
