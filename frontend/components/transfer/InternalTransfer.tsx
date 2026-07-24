'use client';

import { useState } from 'react';
import { ArrowRight, Building2, Wallet } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Select } from '@/components/ui/Select';
import { formatCurrency, generateMockAccounts, generateMockBeneficiaries } from '@/lib/utils';

interface InternalTransferProps {
  onTransfer: (data: { fromAccountId: string; toAccountId: string; amount: number; description: string }) => void;
  isSubmitting?: boolean;
}

export function InternalTransfer({ onTransfer, isSubmitting }: InternalTransferProps) {
  const accounts = generateMockAccounts();
  const [fromAccount, setFromAccount] = useState('');
  const [toAccount, setToAccount] = useState('');
  const [amount, setAmount] = useState('');
  const [description, setDescription] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!fromAccount || !toAccount || !amount) return;
    onTransfer({
      fromAccountId: fromAccount,
      toAccountId: toAccount,
      amount: parseFloat(amount),
      description,
    });
  };

  const selectedFromAccount = accounts.find(a => a.id === fromAccount);

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      <Select
        label="From Account"
        placeholder="Select source account"
        options={accounts.map(a => ({
          value: a.id,
          label: `${a.accountName} - ${formatCurrency(a.availableBalance)}`,
        }))}
        value={fromAccount}
        onChange={e => setFromAccount(e.target.value)}
      />

      <Select
        label="To Account (Internal)"
        placeholder="Select destination account"
        options={accounts
          .filter(a => a.id !== fromAccount)
          .map(a => ({
            value: a.id,
            label: `${a.accountName} (${a.accountNumber.slice(-4)})`,
          }))}
        value={toAccount}
        onChange={e => setToAccount(e.target.value)}
      />

      <div>
        <label className="label">Amount</label>
        <div className="relative">
          <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 font-medium">₹</span>
          <input
            type="number"
            value={amount}
            onChange={e => setAmount(e.target.value)}
            className="input-field pl-8"
            placeholder="0.00"
            min="1"
            step="0.01"
          />
        </div>
        {selectedFromAccount && parseFloat(amount) > selectedFromAccount.availableBalance && (
          <p className="text-sm text-danger-600 mt-1">Insufficient balance</p>
        )}
      </div>

      <div>
        <label className="label">Description (Optional)</label>
        <input
          type="text"
          value={description}
          onChange={e => setDescription(e.target.value)}
          className="input-field"
          placeholder="Enter a note"
          maxLength={200}
        />
      </div>

      <Button
        type="submit"
        className="w-full"
        disabled={!fromAccount || !toAccount || !amount || parseFloat(amount) <= 0}
        isLoading={isSubmitting}
        rightIcon={<ArrowRight className="w-4 h-4" />}
      >
        Transfer
      </Button>
    </form>
  );
}
