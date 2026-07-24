'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  Wallet, ArrowUpDown, CreditCard, HandCoins, TrendingUp, TrendingDown,
  PieChart, Eye, EyeOff,
} from 'lucide-react';
import { Card, CardHeader, CardBody } from '@/components/ui/Card';
import { AccountCard } from '@/components/dashboard/AccountCard';
import { TransactionList } from '@/components/dashboard/TransactionList';
import { BalanceChart } from '@/components/dashboard/BalanceChart';
import { RiskIndicator } from '@/components/dashboard/RiskIndicator';
import { QuickActions } from '@/components/dashboard/QuickActions';
import { StatCard } from '@/components/dashboard/StatCard';
import { formatCurrency, cn } from '@/lib/utils';
import { generateDashboardData, generateMockAccounts } from '@/lib/utils';

const mockData = generateDashboardData();

export default function DashboardPage() {
  const [showBalances, setShowBalances] = useState(true);
  const router = useRouter();
  const accounts = generateMockAccounts();

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="page-title">Welcome back, {mockData.user.name.split(' ')[0]}</h1>
          <p className="page-subtitle">Here&apos;s your financial overview</p>
        </div>
        <button
          onClick={() => setShowBalances(!showBalances)}
          className="p-2 text-gray-400 hover:text-navy-700 hover:bg-gray-100 rounded-lg transition-colors"
        >
          {showBalances ? <Eye className="w-5 h-5" /> : <EyeOff className="w-5 h-5" />}
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Balance"
          value={showBalances ? formatCurrency(mockData.totalBalance) : '••••••'}
          icon={<Wallet className="w-5 h-5" />}
          subtitle="All accounts combined"
          trend={{ value: 12.5, isPositive: true }}
          color="primary"
        />
        <StatCard
          title="Monthly Spending"
          value={showBalances ? formatCurrency(mockData.monthlySpending) : '••••••'}
          icon={<ArrowUpDown className="w-5 h-5" />}
          subtitle="This month"
          trend={{ value: mockData.spendingChange, isPositive: mockData.spendingChange >= 0 }}
          color={mockData.spendingChange >= 0 ? 'success' : 'danger'}
        />
        <StatCard
          title="Active Cards"
          value={String(mockData.activeCards)}
          icon={<CreditCard className="w-5 h-5" />}
          subtitle="3 total cards"
          color="warning"
        />
        <StatCard
          title="Behavioral Trust"
          value={`${mockData.behavioralTrustScore}%`}
          icon={<TrendingUp className="w-5 h-5" />}
          subtitle="Profile confidence"
          trend={{ value: 5, isPositive: true }}
          color="success"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-navy-900">Spending Trend</h2>
                <div className="flex items-center gap-2 text-sm text-gray-500">
                  <div className="flex items-center gap-1">
                    <span className="w-2 h-2 bg-primary-500 rounded-full" />
                    Last 30 days
                  </div>
                </div>
              </div>
            </CardHeader>
            <CardBody>
              <BalanceChart data={mockData.spendingTrend} />
            </CardBody>
          </Card>

          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-navy-900">Quick Actions</h2>
              </div>
            </CardHeader>
            <CardBody>
              <QuickActions />
            </CardBody>
          </Card>

          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-navy-900">Recent Transactions</h2>
                <button
                  onClick={() => router.push('/dashboard/transactions')}
                  className="text-sm text-primary-600 hover:text-primary-700 font-medium"
                >
                  View All
                </button>
              </div>
            </CardHeader>
            <CardBody>
              <TransactionList
                transactions={mockData.recentTransactions}
                onTransactionClick={(txn) => console.log(txn)}
              />
            </CardBody>
          </Card>
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <h2 className="text-lg font-semibold text-navy-900">Your Accounts</h2>
            </CardHeader>
            <CardBody className="space-y-4">
              {accounts.slice(0, 2).map(account => (
                <AccountCard
                  key={account.id}
                  account={account}
                  onClick={() => router.push('/dashboard/accounts')}
                />
              ))}
              <button
                onClick={() => router.push('/dashboard/accounts')}
                className="w-full py-2 text-sm text-primary-600 hover:text-primary-700 font-medium text-center"
              >
                View All Accounts
              </button>
            </CardBody>
          </Card>

          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-navy-900">Behavioral Profile</h2>
                <RiskIndicator score={mockData.behavioralTrustScore} size="sm" showDetails={false} />
              </div>
            </CardHeader>
            <CardBody>
              <RiskIndicator score={mockData.behavioralTrustScore} />
            </CardBody>
          </Card>

          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-navy-900">Spending by Category</h2>
                <PieChart className="w-4 h-4 text-gray-400" />
              </div>
            </CardHeader>
            <CardBody>
              <div className="space-y-3">
                {mockData.spendingByCategory.map(cat => (
                  <div key={cat.category}>
                    <div className="flex items-center justify-between text-sm mb-1">
                      <div className="flex items-center gap-2">
                        <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: cat.color }} />
                        <span className="text-navy-700">{cat.category}</span>
                      </div>
                      <span className="text-gray-500">{formatCurrency(cat.amount)}</span>
                    </div>
                    <div className="w-full bg-gray-100 rounded-full h-1.5">
                      <div
                        className="h-1.5 rounded-full transition-all duration-500"
                        style={{ width: `${cat.percentage}%`, backgroundColor: cat.color }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </CardBody>
          </Card>
        </div>
      </div>
    </div>
  );
}
