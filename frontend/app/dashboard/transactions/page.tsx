'use client';

import { useState, useMemo } from 'react';
import {
  ArrowUpDown, Search, Download, Filter, Calendar,
  ArrowUpRight, ArrowDownLeft,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Card, CardHeader, CardBody } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Select } from '@/components/ui/Select';
import { Badge } from '@/components/ui/Badge';
import { Modal } from '@/components/ui/Modal';
import { formatCurrency, formatDateTime, getStatusColor, generateMockTransactions } from '@/lib/utils';
import type { Transaction } from '@/types';

const allTransactions = generateMockTransactions();

export default function TransactionsPage() {
  const [search, setSearch] = useState('');
  const [typeFilter, setTypeFilter] = useState('all');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [dateRange, setDateRange] = useState('all');
  const [selectedTxn, setSelectedTxn] = useState<Transaction | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const perPage = 15;

  const filtered = useMemo(() => {
    let result = [...allTransactions];

    if (search) {
      const q = search.toLowerCase();
      result = result.filter(t =>
        t.description.toLowerCase().includes(q) ||
        t.reference.toLowerCase().includes(q) ||
        t.counterparty?.toLowerCase().includes(q)
      );
    }
    if (typeFilter !== 'all') result = result.filter(t => t.type === typeFilter);
    if (categoryFilter !== 'all') result = result.filter(t => t.category === categoryFilter);

    if (dateRange === 'today') {
      const today = new Date().toISOString().split('T')[0];
      result = result.filter(t => t.transactionDate.startsWith(today));
    } else if (dateRange === 'week') {
      const weekAgo = new Date(Date.now() - 7 * 86400000).toISOString();
      result = result.filter(t => t.transactionDate >= weekAgo);
    } else if (dateRange === 'month') {
      const monthAgo = new Date(Date.now() - 30 * 86400000).toISOString();
      result = result.filter(t => t.transactionDate >= monthAgo);
    }

    result.sort((a, b) => new Date(b.transactionDate).getTime() - new Date(a.transactionDate).getTime());
    return result;
  }, [search, typeFilter, categoryFilter, dateRange]);

  const totalPages = Math.ceil(filtered.length / perPage);
  const pageItems = filtered.slice((currentPage - 1) * perPage, currentPage * perPage);

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="page-title">Transactions</h1>
          <p className="page-subtitle">View and filter your complete transaction history</p>
        </div>
        <Button variant="secondary" leftIcon={<Download className="w-4 h-4" />}>
          Export CSV
        </Button>
      </div>

      <Card>
        <CardHeader>
          <div className="flex flex-col md:flex-row gap-3">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                value={search}
                onChange={e => { setSearch(e.target.value); setCurrentPage(1); }}
                className="input-field pl-10"
                placeholder="Search by description, reference..."
              />
            </div>
            <div className="flex gap-2">
              <select
                value={typeFilter}
                onChange={e => { setTypeFilter(e.target.value); setCurrentPage(1); }}
                className="input-field w-32"
              >
                <option value="all">All Types</option>
                <option value="credit">Credits</option>
                <option value="debit">Debits</option>
              </select>
              <select
                value={categoryFilter}
                onChange={e => { setCategoryFilter(e.target.value); setCurrentPage(1); }}
                className="input-field w-36"
              >
                <option value="all">All Categories</option>
                <option value="transfer">Transfer</option>
                <option value="payment">Payment</option>
                <option value="recharge">Recharge</option>
                <option value="withdrawal">Withdrawal</option>
                <option value="deposit">Deposit</option>
                <option value="refund">Refund</option>
                <option value="fee">Fee</option>
                <option value="interest">Interest</option>
              </select>
              <select
                value={dateRange}
                onChange={e => { setDateRange(e.target.value); setCurrentPage(1); }}
                className="input-field w-32"
              >
                <option value="all">All Time</option>
                <option value="today">Today</option>
                <option value="week">This Week</option>
                <option value="month">This Month</option>
              </select>
            </div>
          </div>
        </CardHeader>
        <CardBody>
          {pageItems.length === 0 ? (
            <div className="text-center py-12">
              <ArrowUpDown className="w-12 h-12 text-gray-300 mx-auto mb-3" />
              <p className="text-gray-500">No transactions match your filters</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-100">
                    <th className="text-left py-3 px-2 text-gray-500 font-medium">Date</th>
                    <th className="text-left py-3 px-2 text-gray-500 font-medium">Description</th>
                    <th className="text-left py-3 px-2 text-gray-500 font-medium">Category</th>
                    <th className="text-left py-3 px-2 text-gray-500 font-medium">Reference</th>
                    <th className="text-right py-3 px-2 text-gray-500 font-medium">Amount</th>
                    <th className="text-center py-3 px-2 text-gray-500 font-medium">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-50">
                  {pageItems.map(txn => (
                    <tr
                      key={txn.id}
                      onClick={() => setSelectedTxn(txn)}
                      className="hover:bg-gray-50 cursor-pointer transition-colors"
                    >
                      <td className="py-3 px-2 text-gray-500 whitespace-nowrap">
                        {formatDateTime(txn.transactionDate)}
                      </td>
                      <td className="py-3 px-2">
                        <div className="flex items-center gap-2">
                          <span className={txn.type === 'credit' ? 'text-success-600' : 'text-navy-900'}>
                            {txn.type === 'credit' ? <ArrowDownLeft className="w-4 h-4" /> : <ArrowUpRight className="w-4 h-4" />}
                          </span>
                          <span className="font-medium text-navy-900">{txn.description}</span>
                        </div>
                      </td>
                      <td className="py-3 px-2 capitalize text-gray-500">{txn.category}</td>
                      <td className="py-3 px-2 font-mono text-xs text-gray-400">{txn.reference}</td>
                      <td className={cn('py-3 px-2 text-right font-semibold', txn.type === 'credit' ? 'text-success-600' : 'text-navy-900')}>
                        {txn.type === 'credit' ? '+' : '-'}{formatCurrency(txn.amount, txn.currency)}
                      </td>
                      <td className="py-3 px-2 text-center">
                        <Badge variant={txn.status === 'completed' ? 'success' : txn.status === 'pending' ? 'warning' : 'danger'} size="sm">
                          {txn.status}
                        </Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {totalPages > 1 && (
            <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-100">
              <p className="text-sm text-gray-500">
                Showing {(currentPage - 1) * perPage + 1}-{Math.min(currentPage * perPage, filtered.length)} of {filtered.length}
              </p>
              <div className="flex gap-1">
                <button
                  onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                  disabled={currentPage === 1}
                  className="px-3 py-1 text-sm border border-gray-200 rounded-lg disabled:opacity-50 hover:bg-gray-50"
                >
                  Previous
                </button>
                {Array.from({ length: Math.min(totalPages, 5) }).map((_, i) => {
                  const pageNum = Math.max(1, Math.min(currentPage - 2, totalPages - 4)) + i;
                  if (pageNum > totalPages) return null;
                  return (
                    <button
                      key={pageNum}
                      onClick={() => setCurrentPage(pageNum)}
                      className={`px-3 py-1 text-sm border rounded-lg ${
                        pageNum === currentPage
                          ? 'bg-primary-600 text-white border-primary-600'
                          : 'border-gray-200 hover:bg-gray-50'
                      }`}
                    >
                      {pageNum}
                    </button>
                  );
                })}
                <button
                  onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                  disabled={currentPage === totalPages}
                  className="px-3 py-1 text-sm border border-gray-200 rounded-lg disabled:opacity-50 hover:bg-gray-50"
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </CardBody>
      </Card>

      <Modal
        isOpen={!!selectedTxn}
        onClose={() => setSelectedTxn(null)}
        title="Transaction Details"
        size="md"
      >
        {selectedTxn && (
          <div className="space-y-5">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className={selectedTxn.type === 'credit' ? 'text-success-600' : 'text-navy-900'}>
                  {selectedTxn.type === 'credit' ? <ArrowDownLeft className="w-6 h-6" /> : <ArrowUpRight className="w-6 h-6" />}
                </span>
                <div>
                  <p className="text-lg font-semibold text-navy-900">{selectedTxn.description}</p>
                  <p className="text-sm text-gray-500 capitalize">{selectedTxn.category}</p>
                </div>
              </div>
              <span className={cn('text-xl font-bold', selectedTxn.type === 'credit' ? 'text-success-600' : 'text-navy-900')}>
                {selectedTxn.type === 'credit' ? '+' : '-'}{formatCurrency(selectedTxn.amount, selectedTxn.currency)}
              </span>
            </div>

            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-gray-500">Date & Time</p>
                <p className="font-medium text-navy-900">{formatDateTime(selectedTxn.transactionDate)}</p>
              </div>
              <div>
                <p className="text-gray-500">Status</p>
                <Badge variant={selectedTxn.status === 'completed' ? 'success' : selectedTxn.status === 'pending' ? 'warning' : 'danger'}>
                  {selectedTxn.status}
                </Badge>
              </div>
              <div>
                <p className="text-gray-500">Reference</p>
                <p className="font-mono text-xs text-navy-900">{selectedTxn.reference}</p>
              </div>
              <div>
                <p className="text-gray-500">Type</p>
                <p className="font-medium capitalize text-navy-900">{selectedTxn.type}</p>
              </div>
              {selectedTxn.counterparty && (
                <div className="col-span-2">
                  <p className="text-gray-500">Counterparty</p>
                  <p className="font-medium text-navy-900">{selectedTxn.counterparty}</p>
                </div>
              )}
              {selectedTxn.riskScore !== undefined && (
                <div className="col-span-2">
                  <p className="text-gray-500">Risk Score</p>
                  <div className="flex items-center gap-2 mt-1">
                    <div className="flex-1 bg-gray-100 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${
                          selectedTxn.riskScore > 70 ? 'bg-success-500' : selectedTxn.riskScore > 40 ? 'bg-warning-500' : 'bg-danger-500'
                        }`}
                        style={{ width: `${selectedTxn.riskScore}%` }}
                      />
                    </div>
                    <span className="text-xs font-medium">{Math.round(selectedTxn.riskScore)}%</span>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}
