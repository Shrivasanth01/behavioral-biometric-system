'use client';

import { useState } from 'react';
import { ArrowRight, Search, User } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Select } from '@/components/ui/Select';
import { formatCurrency, generateMockAccounts, generateMockBeneficiaries } from '@/lib/utils';
import { BeneficiarySelect } from './BeneficiarySelect';
import type { Beneficiary } from '@/types';

interface ExternalTransferProps {
  onTransfer: (data: {
    fromAccountId: string;
    beneficiaryId?: string;
    toAccountNumber: string;
    toIfscCode: string;
    amount: number;
    description: string;
  }) => void;
  isSubmitting?: boolean;
}

export function ExternalTransfer({ onTransfer, isSubmitting }: ExternalTransferProps) {
  const accounts = generateMockAccounts();
  const beneficiaries = generateMockBeneficiaries();
  const [fromAccount, setFromAccount] = useState('');
  const [selectedBeneficiary, setSelectedBeneficiary] = useState<Beneficiary | null>(null);
  const [accountNumber, setAccountNumber] = useState('');
  const [ifscCode, setIfscCode] = useState('');
  const [bankName, setBankName] = useState('');
  const [amount, setAmount] = useState('');
  const [description, setDescription] = useState('');
  const [mode, setMode] = useState<'beneficiary' | 'manual'>('beneficiary');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!fromAccount || !amount) return;

    if (mode === 'beneficiary' && selectedBeneficiary) {
      onTransfer({
        fromAccountId: fromAccount,
        beneficiaryId: selectedBeneficiary.id,
        toAccountNumber: selectedBeneficiary.accountNumber,
        toIfscCode: selectedBeneficiary.ifscCode,
        amount: parseFloat(amount),
        description,
      });
    } else if (mode === 'manual') {
      onTransfer({
        fromAccountId: fromAccount,
        toAccountNumber: accountNumber,
        toIfscCode: ifscCode,
        amount: parseFloat(amount),
        description,
      });
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      <div className="flex gap-2">
        <button
          type="button"
          onClick={() => setMode('beneficiary')}
          className={`flex-1 py-2 text-sm font-medium rounded-lg border transition-colors ${
            mode === 'beneficiary'
              ? 'bg-primary-50 border-primary-500 text-primary-700'
              : 'border-gray-200 text-gray-500 hover:bg-gray-50'
          }`}
        >
          <User className="w-4 h-4 mx-auto mb-1" />
          Beneficiary
        </button>
        <button
          type="button"
          onClick={() => setMode('manual')}
          className={`flex-1 py-2 text-sm font-medium rounded-lg border transition-colors ${
            mode === 'manual'
              ? 'bg-primary-50 border-primary-500 text-primary-700'
              : 'border-gray-200 text-gray-500 hover:bg-gray-50'
          }`}
        >
          <Search className="w-4 h-4 mx-auto mb-1" />
          Manual Entry
        </button>
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

      {mode === 'beneficiary' ? (
        <div>
          <label className="label">Select Beneficiary</label>
          <BeneficiarySelect
            beneficiaries={beneficiaries}
            selectedId={selectedBeneficiary?.id || ''}
            onSelect={setSelectedBeneficiary}
          />
        </div>
      ) : (
        <>
          <div>
            <label className="label">Account Number</label>
            <input
              type="text"
              value={accountNumber}
              onChange={e => setAccountNumber(e.target.value)}
              className="input-field font-mono"
              placeholder="Enter account number"
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">IFSC Code</label>
              <input
                type="text"
                value={ifscCode}
                onChange={e => setIfscCode(e.target.value.toUpperCase())}
                className="input-field font-mono uppercase"
                placeholder="SBIN0001234"
              />
            </div>
            <div>
              <label className="label">Bank Name</label>
              <input
                type="text"
                value={bankName}
                onChange={e => setBankName(e.target.value)}
                className="input-field"
                placeholder="Bank name"
              />
            </div>
          </div>
        </>
      )}

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
          placeholder="Enter a note"
        />
      </div>

      <Button
        type="submit"
        className="w-full"
        disabled={!fromAccount || !amount || parseFloat(amount) <= 0}
        isLoading={isSubmitting}
        rightIcon={<ArrowRight className="w-4 h-4" />}
      >
        Transfer
      </Button>
    </form>
  );
}
