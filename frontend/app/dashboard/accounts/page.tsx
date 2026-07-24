'use client';

import { useState } from 'react';
import { Building2, Download, ArrowUpRight, ArrowDownLeft } from 'lucide-react';
import { Card, CardHeader, CardBody } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Modal } from '@/components/ui/Modal';
import { Badge } from '@/components/ui/Badge';
import { AccountCard } from '@/components/dashboard/AccountCard';
import { TransactionList } from '@/components/dashboard/TransactionList';
import { formatCurrency, generateMockAccounts, generateMockTransactions } from '@/lib/utils';
import type { Account, Transaction } from '@/types';

const mockAccounts = generateMockAccounts();
const mockTransactions = generateMockTransactions();

export default function AccountsPage() {
  const [selectedAccount, setSelectedAccount] = useState<Account | null>(null);
  const [showStatement, setShowStatement] = useState(false);

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="page-title">Accounts</h1>
        <p className="page-subtitle">Manage your bank accounts and view statements</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {mockAccounts.map(account => (
          <AccountCard
            key={account.id}
            account={account}
            onClick={() => setSelectedAccount(account)}
          />
        ))}
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-navy-900">Account Summary</h2>
            <div className="flex gap-2">
              <Button variant="secondary" size="sm" leftIcon={<Download className="w-4 h-4" />}>
                Export
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardBody>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-100">
                  <th className="text-left py-3 px-2 text-gray-500 font-medium">Account</th>
                  <th className="text-left py-3 px-2 text-gray-500 font-medium">Type</th>
                  <th className="text-left py-3 px-2 text-gray-500 font-medium">Account No.</th>
                  <th className="text-right py-3 px-2 text-gray-500 font-medium">Balance</th>
                  <th className="text-right py-3 px-2 text-gray-500 font-medium">Available</th>
                  <th className="text-center py-3 px-2 text-gray-500 font-medium">Status</th>
                  <th className="text-right py-3 px-2 text-gray-500 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {mockAccounts.map(acc => (
                  <tr key={acc.id} className="border-b border-gray-50 hover:bg-gray-50">
                    <td className="py-3 px-2 font-medium text-navy-900">{acc.accountName}</td>
                    <td className="py-3 px-2 capitalize">{acc.accountType}</td>
                    <td className="py-3 px-2 text-gray-500 font-mono">{acc.accountNumber}</td>
                    <td className="py-3 px-2 text-right font-semibold">{formatCurrency(acc.balance, acc.currency)}</td>
                    <td className="py-3 px-2 text-right">{formatCurrency(acc.availableBalance, acc.currency)}</td>
                    <td className="py-3 px-2 text-center">
                      <Badge variant={acc.status === 'active' ? 'success' : acc.status === 'frozen' ? 'warning' : 'neutral'} size="sm">
                        {acc.status}
                      </Badge>
                    </td>
                    <td className="py-3 px-2 text-right">
                      <button
                        onClick={() => setSelectedAccount(acc)}
                        className="text-primary-600 hover:text-primary-700 font-medium text-sm"
                      >
                        Details
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardBody>
      </Card>

      <Modal
        isOpen={!!selectedAccount}
        onClose={() => { setSelectedAccount(null); setShowStatement(false); }}
        title={selectedAccount?.accountName}
        description={selectedAccount?.accountNumber}
        size="lg"
      >
        {selectedAccount && (
          <div className="space-y-6">
            <div className="bg-gradient-to-r from-primary-600 to-primary-800 rounded-xl p-6 text-white">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <Building2 className="w-5 h-5 opacity-80" />
                  <span className="text-sm opacity-80 capitalize">{selectedAccount.accountType} Account</span>
                </div>
                <Badge variant={selectedAccount.status === 'active' ? 'success' : 'warning'}>
                  {selectedAccount.status}
                </Badge>
              </div>
              <p className="text-3xl font-bold mb-2">{formatCurrency(selectedAccount.balance, selectedAccount.currency)}</p>
              <p className="text-sm opacity-80">Available: {formatCurrency(selectedAccount.availableBalance, selectedAccount.currency)}</p>
            </div>

            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-gray-500">IFSC Code</p>
                <p className="font-medium text-navy-900">{selectedAccount.ifscCode}</p>
              </div>
              <div>
                <p className="text-gray-500">Branch</p>
                <p className="font-medium text-navy-900">{selectedAccount.branchName}</p>
              </div>
              <div>
                <p className="text-gray-500">Account Type</p>
                <p className="font-medium text-navy-900 capitalize">{selectedAccount.accountType}</p>
              </div>
              <div>
                <p className="text-gray-500">Opened On</p>
                <p className="font-medium text-navy-900">{new Date(selectedAccount.openedAt).toLocaleDateString('en-IN', { day: 'numeric', month: 'long', year: 'numeric' })}</p>
              </div>
            </div>

            <div className="flex gap-3">
              <Button className="flex-1" leftIcon={<ArrowUpRight className="w-4 h-4" />}>
                Transfer
              </Button>
              <Button variant="secondary" className="flex-1" leftIcon={<ArrowDownLeft className="w-4 h-4" />}>
                Deposit
              </Button>
              <Button
                variant="ghost"
                onClick={() => setShowStatement(!showStatement)}
                leftIcon={<Download className="w-4 h-4" />}
              >
                Statement
              </Button>
            </div>

            {showStatement && (
              <div>
                <h4 className="text-sm font-semibold text-navy-900 mb-3">Mini Statement</h4>
                <TransactionList
                  transactions={mockTransactions.filter(t => t.accountId === selectedAccount.id).slice(0, 5)}
                />
              </div>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
}
