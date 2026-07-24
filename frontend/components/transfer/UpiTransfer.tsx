'use client';

import { useState } from 'react';
import { ArrowRight, QrCode, Smartphone } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Select } from '@/components/ui/Select';
import { formatCurrency, generateMockAccounts, generateMockBeneficiaries } from '@/lib/utils';
import { BeneficiarySelect } from './BeneficiarySelect';
import type { Beneficiary } from '@/types';

interface UpiTransferProps {
  onTransfer: (data: {
    fromAccountId: string;
    toUpiId: string;
    amount: number;
    description: string;
  }) => void;
  isSubmitting?: boolean;
}

export function UpiTransfer({ onTransfer, isSubmitting }: UpiTransferProps) {
  const accounts = generateMockAccounts();
  const beneficiaries = generateMockBeneficiaries().filter(b => b.isUPI);
  const [fromAccount, setFromAccount] = useState('');
  const [upiId, setUpiId] = useState('');
  const [amount, setAmount] = useState('');
  const [description, setDescription] = useState('');
  const [selectedBeneficiary, setSelectedBeneficiary] = useState<Beneficiary | null>(null);

  const handleUpiSelect = (ben: Beneficiary) => {
    setSelectedBeneficiary(ben);
    setUpiId(ben.upiId || '');
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!fromAccount || !upiId || !amount) return;
    onTransfer({
      fromAccountId: fromAccount,
      toUpiId: upiId,
      amount: parseFloat(amount),
      description,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      <div className="p-4 bg-blue-50 rounded-lg flex items-start gap-3">
        <QrCode className="w-5 h-5 text-blue-600 shrink-0 mt-0.5" />
        <div>
          <p className="text-sm font-medium text-blue-800">UPI Transfer</p>
          <p className="text-xs text-blue-600 mt-0.5">Send money using UPI ID. Instant transfer, 24x7.</p>
        </div>
      </div>

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

      {beneficiaries.length > 0 && (
        <div>
          <label className="label">UPI Beneficiaries</label>
          <BeneficiarySelect
            beneficiaries={beneficiaries}
            selectedId={selectedBeneficiary?.id || ''}
            onSelect={handleUpiSelect}
          />
        </div>
      )}

      <div>
        <label className="label">UPI ID</label>
        <div className="relative">
          <Smartphone className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            value={upiId}
            onChange={e => setUpiId(e.target.value)}
            className="input-field pl-10 font-mono"
            placeholder="username@upi"
          />
        </div>
      </div>

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
          />
        </div>
      </div>

      <div>
        <label className="label">Description (Optional)</label>
        <input
          type="text"
          value={description}
          onChange={e => setDescription(e.target.value)}
          className="input-field"
          placeholder="What's this for?"
        />
      </div>

      <Button
        type="submit"
        className="w-full"
        disabled={!fromAccount || !upiId || !amount || parseFloat(amount) <= 0}
        isLoading={isSubmitting}
        rightIcon={<ArrowRight className="w-4 h-4" />}
      >
        Pay via UPI
      </Button>
    </form>
  );
}
