'use client';

import { useState } from 'react';
import { Coins as HandCoins, Calculator, Plus, TrendingUp, Calendar, CheckCircle } from 'lucide-react';
import { Card, CardHeader, CardBody } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Modal } from '@/components/ui/Modal';
import { Tabs } from '@/components/ui/Tabs';
import { Progress } from '@/components/ui/Progress';
import { formatCurrency, calculateEMI, getTotalInterest, formatDate, generateMockLoans } from '@/lib/utils';
import type { Loan } from '@/types';

const mockLoans = generateMockLoans();

export default function LoansPage() {
  const [activeTab, setActiveTab] = useState('active');
  const [showApplyModal, setShowApplyModal] = useState(false);
  const [showEMICalculator, setShowEMICalculator] = useState(false);
  const [selectedLoan, setSelectedLoan] = useState<Loan | null>(null);
  const [applyForm, setApplyForm] = useState({ loanType: 'personal', amount: 500000, tenureMonths: 36 });
  const [emiCalc, setEmiCalc] = useState({ amount: 500000, rate: 12, tenure: 36 });

  const emiResult = calculateEMI(emiCalc.amount, emiCalc.rate, emiCalc.tenure);
  const totalInterest = getTotalInterest(emiCalc.amount, emiCalc.rate, emiCalc.tenure);
  const totalPayment = emiCalc.amount + totalInterest;

  const loanTypeLabels: Record<string, string> = {
    personal: 'Personal Loan',
    home: 'Home Loan',
    car: 'Car Loan',
    education: 'Education Loan',
    business: 'Business Loan',
  };

  const tabs = [
    { id: 'active', label: 'Active Loans', badge: mockLoans.filter(l => l.status === 'active').length },
    { id: 'history', label: 'History' },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="page-title">Loans</h1>
          <p className="page-subtitle">Apply for loans, track repayments, and calculate EMIs</p>
        </div>
        <div className="flex gap-2">
          <Button variant="secondary" onClick={() => setShowEMICalculator(true)} leftIcon={<Calculator className="w-4 h-4" />}>
            EMI Calculator
          </Button>
          <Button onClick={() => setShowApplyModal(true)} leftIcon={<Plus className="w-4 h-4" />}>
            Apply for Loan
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardBody>
            <p className="text-sm text-gray-500">Total Loans</p>
            <p className="text-2xl font-bold text-navy-900">{mockLoans.length}</p>
          </CardBody>
        </Card>
        <Card>
          <CardBody>
            <p className="text-sm text-gray-500">Total Outstanding</p>
            <p className="text-2xl font-bold text-navy-900">{formatCurrency(mockLoans.reduce((s, l) => s + l.remainingAmount, 0))}</p>
          </CardBody>
        </Card>
        <Card>
          <CardBody>
            <p className="text-sm text-gray-500">Next EMI Due</p>
            <p className="text-2xl font-bold text-navy-900">{formatCurrency(mockLoans.reduce((s, l) => s + l.emiAmount, 0))}</p>
          </CardBody>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <Tabs tabs={tabs} activeTab={activeTab} onChange={setActiveTab} variant="pills" />
        </CardHeader>
        <CardBody>
          {mockLoans.length === 0 ? (
            <div className="text-center py-12">
              <HandCoins className="w-12 h-12 text-gray-300 mx-auto mb-3" />
              <p className="text-gray-500">No loans found</p>
              <Button className="mt-4" onClick={() => setShowApplyModal(true)}>Apply for a Loan</Button>
            </div>
          ) : (
            <div className="space-y-4">
              {mockLoans
                .filter(l => activeTab === 'active' ? l.status === 'active' || l.status === 'approved' : true)
                .map(loan => (
                  <div
                    key={loan.id}
                    onClick={() => setSelectedLoan(loan)}
                    className="p-4 border border-gray-200 rounded-xl hover:border-gray-300 hover:shadow-sm cursor-pointer transition-all"
                  >
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-2">
                        <div className="w-10 h-10 bg-primary-50 rounded-lg flex items-center justify-center">
                          <HandCoins className="w-5 h-5 text-primary-600" />
                        </div>
                        <div>
                          <h3 className="text-sm font-semibold text-navy-900">{loanTypeLabels[loan.loanType]}</h3>
                          <p className="text-xs text-gray-500">Applied {formatDate(loan.appliedAt)}</p>
                        </div>
                      </div>
                      <Badge variant={loan.status === 'active' ? 'success' : loan.status === 'approved' ? 'info' : 'warning'}>
                        {loan.status}
                      </Badge>
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
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
                      <div className="mt-3">
                        <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
                          <span>Progress</span>
                          <span>{Math.round((loan.totalPaid / (loan.approvedAmount + totalInterest)) * 100)}%</span>
                        </div>
                        <Progress
                          value={(loan.totalPaid / (loan.approvedAmount + totalInterest)) * 100}
                          variant="primary"
                          size="sm"
                        />
                      </div>
                    )}
                  </div>
                ))}
            </div>
          )}
        </CardBody>
      </Card>

      <Modal
        isOpen={!!selectedLoan}
        onClose={() => setSelectedLoan(null)}
        title={selectedLoan ? loanTypeLabels[selectedLoan.loanType] : ''}
        size="lg"
      >
        {selectedLoan && (
          <div className="space-y-6">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-gray-500">Loan Amount</p>
                <p className="text-lg font-bold text-navy-900">{formatCurrency(selectedLoan.approvedAmount)}</p>
              </div>
              <div>
                <p className="text-gray-500">Interest Rate</p>
                <p className="text-lg font-bold text-navy-900">{selectedLoan.interestRate}% p.a.</p>
              </div>
              <div>
                <p className="text-gray-500">Tenure</p>
                <p className="font-medium text-navy-900">{selectedLoan.tenureMonths} months</p>
              </div>
              <div>
                <p className="text-gray-500">EMI Amount</p>
                <p className="font-medium text-navy-900">{formatCurrency(selectedLoan.emiAmount)}</p>
              </div>
              <div>
                <p className="text-gray-500">Amount Paid</p>
                <p className="font-medium text-success-600">{formatCurrency(selectedLoan.totalPaid)}</p>
              </div>
              <div>
                <p className="text-gray-500">Remaining</p>
                <p className="font-medium text-primary-600">{formatCurrency(selectedLoan.remainingAmount)}</p>
              </div>
            </div>

            <div>
              <h4 className="text-sm font-semibold text-navy-900 mb-3">EMI Schedule</h4>
              <div className="space-y-1 max-h-48 overflow-y-auto">
                {Array.from({ length: Math.min(selectedLoan.tenureMonths, 12) }).map((_, i) => (
                  <div key={i} className="flex items-center justify-between py-2 px-3 rounded-lg hover:bg-gray-50 text-sm">
                    <div className="flex items-center gap-2">
                      <Calendar className="w-3 h-3 text-gray-400" />
                      <span className="text-gray-600">Month {i + 1}</span>
                    </div>
                    <span className="font-medium text-navy-900">{formatCurrency(selectedLoan.emiAmount)}</span>
                  </div>
                ))}
              </div>
            </div>

            <Button className="w-full" onClick={() => setSelectedLoan(null)}>
              Close
            </Button>
          </div>
        )}
      </Modal>

      <Modal
        isOpen={showEMICalculator}
        onClose={() => setShowEMICalculator(false)}
        title="EMI Calculator"
        size="md"
      >
        <div className="space-y-5">
          <div>
            <label className="label">Loan Amount (₹)</label>
            <input type="number" value={emiCalc.amount}
              onChange={e => setEmiCalc(p => ({ ...p, amount: parseInt(e.target.value) || 0 }))}
              className="input-field" />
          </div>
          <div>
            <label className="label">Interest Rate (% p.a.)</label>
            <input type="number" value={emiCalc.rate} step="0.1"
              onChange={e => setEmiCalc(p => ({ ...p, rate: parseFloat(e.target.value) || 0 }))}
              className="input-field" />
          </div>
          <div>
            <label className="label">Tenure (Months)</label>
            <input type="number" value={emiCalc.tenure}
              onChange={e => setEmiCalc(p => ({ ...p, tenure: parseInt(e.target.value) || 0 }))}
              className="input-field" />
          </div>

          <div className="p-4 bg-primary-50 rounded-xl space-y-3">
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Monthly EMI</span>
              <span className="text-lg font-bold text-primary-700">{formatCurrency(emiResult)}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Total Interest</span>
              <span className="font-medium text-navy-900">{formatCurrency(totalInterest)}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Total Payment</span>
              <span className="font-medium text-navy-900">{formatCurrency(totalPayment)}</span>
            </div>
          </div>

          <Button className="w-full" onClick={() => {
            setApplyForm(prev => ({ ...prev, amount: emiCalc.amount, tenureMonths: emiCalc.tenure }));
            setShowEMICalculator(false);
            setShowApplyModal(true);
          }}>
            Apply for This Loan
          </Button>
        </div>
      </Modal>

      <Modal
        isOpen={showApplyModal}
        onClose={() => setShowApplyModal(false)}
        title="Apply for Loan"
        size="md"
      >
        <div className="space-y-5">
          <div>
            <label className="label">Loan Type</label>
            <select value={applyForm.loanType}
              onChange={e => setApplyForm(p => ({ ...p, loanType: e.target.value }))}
              className="input-field">
              <option value="personal">Personal Loan</option>
              <option value="home">Home Loan</option>
              <option value="car">Car Loan</option>
              <option value="education">Education Loan</option>
              <option value="business">Business Loan</option>
            </select>
          </div>
          <div>
            <label className="label">Loan Amount (₹)</label>
            <input type="number" value={applyForm.amount}
              onChange={e => setApplyForm(p => ({ ...p, amount: parseInt(e.target.value) || 0 }))}
              className="input-field" min="10000" max="10000000" />
          </div>
          <div>
            <label className="label">Tenure (Months)</label>
            <input type="number" value={applyForm.tenureMonths}
              onChange={e => setApplyForm(p => ({ ...p, tenureMonths: parseInt(e.target.value) || 0 }))}
              className="input-field" min="6" max="240" />
          </div>

          <div className="p-4 bg-gray-50 rounded-xl space-y-2">
            <p className="text-sm font-medium text-navy-900">Estimated EMI</p>
            <p className="text-2xl font-bold text-primary-600">
              {formatCurrency(calculateEMI(applyForm.amount, 12, applyForm.tenureMonths))}
            </p>
            <p className="text-xs text-gray-500">per month @ 12% p.a. for {applyForm.tenureMonths} months</p>
          </div>

          <Button className="w-full" onClick={() => {
            setShowApplyModal(false);
          }}>
            Submit Application
          </Button>
        </div>
      </Modal>
    </div>
  );
}
