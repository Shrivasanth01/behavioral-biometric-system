'use client';

import { useState } from 'react';
import {
  Zap, Wifi, Tv, Phone, Droplets, Flame, CreditCard, ArrowRight,
  Lightbulb, FileText, Shield, Smartphone,
} from 'lucide-react';
import { Card, CardHeader, CardBody } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Tabs } from '@/components/ui/Tabs';
import { formatCurrency, formatDateTime, generateMockTransactions } from '@/lib/utils';
import type { Transaction } from '@/types';

const billCategories = [
  { id: 'mobile', label: 'Mobile Recharge', icon: Smartphone, color: 'bg-emerald-50 text-emerald-600' },
  { id: 'electricity', label: 'Electricity', icon: Zap, color: 'bg-yellow-50 text-yellow-600' },
  { id: 'dth', label: 'DTH / TV', icon: Tv, color: 'bg-purple-50 text-purple-600' },
  { id: 'broadband', label: 'Broadband', icon: Wifi, color: 'bg-blue-50 text-blue-600' },
  { id: 'gas', label: 'Gas Bill', icon: Flame, color: 'bg-orange-50 text-orange-600' },
  { id: 'water', label: 'Water Bill', icon: Droplets, color: 'bg-cyan-50 text-cyan-600' },
  { id: 'insurance', label: 'Insurance', icon: Shield, color: 'bg-rose-50 text-rose-600' },
  { id: 'other', label: 'Other Bills', icon: FileText, color: 'bg-gray-50 text-gray-600' },
];

const mockTransactions = generateMockTransactions().filter(t => t.category === 'payment' || t.category === 'recharge');

export default function PaymentsPage() {
  const [activeTab, setActiveTab] = useState('bills');
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [provider, setProvider] = useState('');
  const [consumerId, setConsumerId] = useState('');
  const [amount, setAmount] = useState('');
  const [showPaymentForm, setShowPaymentForm] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);

  const tabs = [
    { id: 'bills', label: 'Bill Payments', icon: <FileText className="w-4 h-4" /> },
    { id: 'recharge', label: 'Mobile Recharge', icon: <Smartphone className="w-4 h-4" /> },
    { id: 'history', label: 'Payment History', icon: <CreditCard className="w-4 h-4" /> },
  ];

  const handlePay = () => {
    setShowPaymentForm(false);
    setShowSuccess(true);
    setTimeout(() => setShowSuccess(false), 3000);
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="page-title">Payments & Recharge</h1>
        <p className="page-subtitle">Pay bills, recharge mobile, and manage utility payments</p>
      </div>

      <Card>
        <CardHeader>
          <Tabs tabs={tabs} activeTab={activeTab} onChange={setActiveTab} variant="pills" />
        </CardHeader>
        <CardBody>
          {activeTab === 'bills' && !showPaymentForm && !showSuccess && (
            <div className="space-y-6">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {billCategories.map(cat => (
                  <button
                    key={cat.id}
                    onClick={() => { setSelectedCategory(cat.id); setShowPaymentForm(true); }}
                    className="flex flex-col items-center gap-2 p-4 bg-white rounded-xl border border-gray-200 hover:shadow-md hover:border-gray-300 transition-all"
                  >
                    <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${cat.color}`}>
                      <cat.icon className="w-6 h-6" />
                    </div>
                    <span className="text-xs font-medium text-gray-700 text-center">{cat.label}</span>
                  </button>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'recharge' && !showPaymentForm && !showSuccess && (
            <div className="space-y-4">
              <h3 className="text-sm font-semibold text-navy-900">Mobile Recharge</h3>
              <div className="grid grid-cols-2 gap-3">
                {[
                  { name: 'Airtel', color: 'bg-red-50 text-red-600' },
                  { name: 'Jio', color: 'bg-blue-50 text-blue-600' },
                  { name: 'VI', color: 'bg-red-50 text-red-600' },
                  { name: 'BSNL', color: 'bg-emerald-50 text-emerald-600' },
                ].map(op => (
                  <button
                    key={op.name}
                    onClick={() => { setSelectedCategory('mobile'); setShowPaymentForm(true); }}
                    className="flex items-center gap-3 p-4 rounded-xl border border-gray-200 hover:border-gray-300 hover:shadow-sm transition-all"
                  >
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${op.color} font-bold text-sm`}>
                      {op.name[0]}
                    </div>
                    <span className="text-sm font-medium text-navy-900">{op.name}</span>
                  </button>
                ))}
              </div>
              <div className="mt-6">
                <h3 className="text-sm font-semibold text-navy-900 mb-3">DTH Recharge</h3>
                <div className="grid grid-cols-2 gap-3">
                  {[
                    { name: 'Tata Play', icon: Tv },
                    { name: 'Airtel DTH', icon: Tv },
                    { name: 'Dish TV', icon: Tv },
                    { name: 'Sun Direct', icon: Tv },
                  ].map(op => (
                    <button
                      key={op.name}
                      onClick={() => { setSelectedCategory('dth'); setShowPaymentForm(true); }}
                      className="flex items-center gap-3 p-4 rounded-xl border border-gray-200 hover:border-gray-300 hover:shadow-sm transition-all"
                    >
                      <div className="w-10 h-10 rounded-lg bg-purple-50 text-purple-600 flex items-center justify-center">
                        <Tv className="w-5 h-5" />
                      </div>
                      <span className="text-sm font-medium text-navy-900">{op.name}</span>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {showPaymentForm && (
            <div className="space-y-5 max-w-md">
              <h3 className="text-lg font-semibold text-navy-900">
                {selectedCategory === 'mobile' ? 'Mobile Recharge' : 'Bill Payment'}
              </h3>
              <div>
                <label className="label">Provider</label>
                <input type="text" value={provider} onChange={e => setProvider(e.target.value)}
                  className="input-field" placeholder="Select provider" />
              </div>
              <div>
                <label className="label">{selectedCategory === 'mobile' ? 'Mobile Number' : 'Consumer ID / Account Number'}</label>
                <input type="text" value={consumerId} onChange={e => setConsumerId(e.target.value)}
                  className="input-field font-mono" placeholder="Enter consumer number" />
              </div>
              <div>
                <label className="label">Amount</label>
                <div className="relative">
                  <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500">₹</span>
                  <input type="number" value={amount} onChange={e => setAmount(e.target.value)}
                    className="input-field pl-8" placeholder="0" />
                </div>
              </div>
              <div className="flex gap-3">
                <Button variant="secondary" className="flex-1" onClick={() => setShowPaymentForm(false)}>
                  Cancel
                </Button>
                <Button className="flex-1" onClick={handlePay} rightIcon={<ArrowRight className="w-4 h-4" />}>
                  Pay ₹{amount || '0'}
                </Button>
              </div>
            </div>
          )}

          {showSuccess && (
            <div className="text-center py-12">
              <div className="w-16 h-16 bg-success-50 rounded-full flex items-center justify-center mx-auto mb-4">
                <CreditCard className="w-8 h-8 text-success-600" />
              </div>
              <h3 className="text-lg font-semibold text-navy-900 mb-2">Payment Successful</h3>
              <p className="text-gray-500 mb-6">Your payment of ₹{amount} has been processed successfully.</p>
              <Button onClick={() => { setShowSuccess(false); setShowPaymentForm(false); setAmount(''); setProvider(''); setConsumerId(''); }}>
                Make Another Payment
              </Button>
            </div>
          )}

          {activeTab === 'history' && (
            <div className="space-y-2">
              {mockTransactions.length === 0 ? (
                <div className="text-center py-8">
                  <CreditCard className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                  <p className="text-gray-500">No payment history</p>
                </div>
              ) : (
                mockTransactions.map(txn => (
                  <div key={txn.id} className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50">
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 rounded-lg bg-purple-50 text-purple-600 flex items-center justify-center">
                        <CreditCard className="w-4 h-4" />
                      </div>
                      <div>
                        <p className="text-sm font-medium text-navy-900">{txn.description}</p>
                        <p className="text-xs text-gray-500">{formatDateTime(txn.transactionDate)}</p>
                      </div>
                    </div>
                    <span className="text-sm font-semibold text-navy-900">{formatCurrency(txn.amount)}</span>
                  </div>
                ))
              )}
            </div>
          )}
        </CardBody>
      </Card>
    </div>
  );
}
