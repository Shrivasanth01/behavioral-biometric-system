import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { format, formatDistanceToNow, parseISO } from 'date-fns';
import { CURRENCY_SYMBOLS } from './constants';
import type {
  User, Account, Transaction, Beneficiary, Card, Loan,
  DashboardData,
} from '@/types';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatCurrency(amount: number, currency: string = 'INR'): string {
  const symbol = CURRENCY_SYMBOLS[currency] || currency;
  const formatter = new Intl.NumberFormat('en-IN', {
    style: 'decimal',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
  return `${symbol}${formatter.format(amount)}`;
}

export function formatDate(dateStr: string, formatStr: string = 'dd MMM yyyy'): string {
  try {
    return format(parseISO(dateStr), formatStr);
  } catch {
    return dateStr;
  }
}

export function formatDateTime(dateStr: string): string {
  try {
    return format(parseISO(dateStr), 'dd MMM yyyy, HH:mm');
  } catch {
    return dateStr;
  }
}

export function timeAgo(dateStr: string): string {
  try {
    return formatDistanceToNow(parseISO(dateStr), { addSuffix: true });
  } catch {
    return dateStr;
  }
}

export function maskAccountNumber(accountNumber: string): string {
  if (accountNumber.length <= 4) return accountNumber;
  return `XXXX${accountNumber.slice(-4)}`;
}

export function maskCardNumber(cardNumber: string): string {
  if (cardNumber.length <= 4) return cardNumber;
  return `•••• ${cardNumber.slice(-4)}`;
}

export function formatCardNumber(cardNumber: string): string {
  const cleaned = cardNumber.replace(/\s/g, '');
  return cleaned.replace(/(\d{4})/g, '$1 ').trim();
}

export function getInitials(name: string): string {
  return name
    .split(' ')
    .map(n => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);
}

export function generateTransactionReference(): string {
  const prefix = 'TXN';
  const timestamp = Date.now().toString(36).toUpperCase();
  const random = Math.random().toString(36).substring(2, 6).toUpperCase();
  return `${prefix}${timestamp}${random}`;
}

export function getRiskLevel(score: number): { label: string; color: string; bg: string } {
  if (score <= 30) return { label: 'High Risk', color: 'text-red-500', bg: 'bg-red-50' };
  if (score <= 60) return { label: 'Medium Risk', color: 'text-yellow-500', bg: 'bg-yellow-50' };
  if (score <= 80) return { label: 'Low Risk', color: 'text-blue-500', bg: 'bg-blue-50' };
  return { label: 'Trusted', color: 'text-green-500', bg: 'bg-green-50' };
}

export function getStatusColor(status: string): string {
  const colors: Record<string, string> = {
    active: 'bg-green-100 text-green-800',
    inactive: 'bg-gray-100 text-gray-800',
    pending: 'bg-yellow-100 text-yellow-800',
    completed: 'bg-green-100 text-green-800',
    failed: 'bg-red-100 text-red-800',
    frozen: 'bg-blue-100 text-blue-800',
    blocked: 'bg-red-100 text-red-800',
    closed: 'bg-gray-100 text-gray-800',
    approved: 'bg-green-100 text-green-800',
    rejected: 'bg-red-100 text-red-800',
    overdue: 'bg-red-100 text-red-800',
    paid: 'bg-green-100 text-green-800',
  };
  return colors[status] || 'bg-gray-100 text-gray-800';
}

export function debounce<T extends (...args: unknown[]) => unknown>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout;
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}

export function generateSessionId(): string {
  return `sess_${Date.now()}_${Math.random().toString(36).substring(2, 10)}`;
}

export function calculateEMI(
  principal: number,
  annualRate: number,
  tenureMonths: number
): number {
  const monthlyRate = annualRate / 12 / 100;
  const emi =
    (principal * monthlyRate * Math.pow(1 + monthlyRate, tenureMonths)) /
    (Math.pow(1 + monthlyRate, tenureMonths) - 1);
  return Math.round(emi);
}

export function getTotalInterest(
  principal: number,
  annualRate: number,
  tenureMonths: number
): number {
  const emi = calculateEMI(principal, annualRate, tenureMonths);
  return emi * tenureMonths - principal;
}

export function generateMockAccounts(): Account[] {
  return [
    {
      id: 'acc_1',
      userId: 'usr_1',
      accountNumber: '12345678901',
      accountType: 'savings',
      accountName: 'Primary Savings',
      currency: 'INR',
      balance: 284750.50,
      availableBalance: 284750.50,
      status: 'active',
      ifscCode: 'SBIN0001234',
      branchName: 'Main Branch',
      openedAt: '2020-03-15T00:00:00Z',
    },
    {
      id: 'acc_2',
      userId: 'usr_1',
      accountNumber: '12345678902',
      accountType: 'current',
      accountName: 'Current Account',
      currency: 'INR',
      balance: 45000.00,
      availableBalance: 42500.00,
      status: 'active',
      ifscCode: 'SBIN0001234',
      branchName: 'Main Branch',
      openedAt: '2021-06-01T00:00:00Z',
    },
    {
      id: 'acc_3',
      userId: 'usr_1',
      accountNumber: '12345678903',
      accountType: 'credit',
      accountName: 'Platinum Credit Card',
      currency: 'INR',
      balance: -12500.00,
      availableBalance: 87500.00,
      status: 'active',
      ifscCode: 'SBIN0001234',
      branchName: 'Main Branch',
      openedAt: '2022-01-10T00:00:00Z',
    },
  ] as Account[];
}

export function generateMockTransactions(): Transaction[] {
  const transactions: Transaction[] = [];
  const categories: Transaction['category'][] = ['transfer', 'payment', 'recharge', 'withdrawal', 'deposit', 'refund'];
  const descriptions = [
    'Salary credit', 'Rent payment', 'Electricity bill', 'Mobile recharge',
    'DTH recharge', 'Amazon shopping', 'Swiggy order', 'Uber ride',
    'Netflix subscription', 'Interest credit', 'Fund transfer', 'QR payment',
    'Wallet topup', 'Insurance premium', 'EMI payment',
  ];
  for (let i = 0; i < 50; i++) {
    const date = new Date();
    date.setDate(date.getDate() - i);
    const isCredit = Math.random() > 0.6;
    transactions.push({
      id: `txn_${i + 1}`,
      accountId: i % 3 === 0 ? 'acc_2' : 'acc_1',
      type: isCredit ? 'credit' : 'debit',
      category: categories[Math.floor(Math.random() * categories.length)],
      amount: Math.round(Math.random() * 50000 * 100) / 100,
      currency: 'INR',
      description: descriptions[Math.floor(Math.random() * descriptions.length)],
      reference: `REF${Date.now()}${i}`,
      status: Math.random() > 0.1 ? 'completed' : 'pending',
      transactionDate: date.toISOString(),
      createdAt: date.toISOString(),
      riskScore: Math.random() * 100,
    });
  }
  return transactions;
}

export function generateMockUser(): User {
  return {
    id: 'usr_1',
    email: 'rahul.sharma@example.com',
    name: 'Rahul Sharma',
    phone: '+91 98765 43210',
    role: 'customer',
    mfaEnabled: true,
    mfaMethod: 'app',
    behavioralProfileStatus: 'complete',
    trustedDevices: [
      {
        id: 'dev_1',
        name: 'My iPhone 15',
        deviceType: 'mobile',
        browser: 'Safari',
        os: 'iOS 17.2',
        lastUsed: new Date().toISOString(),
        isCurrent: true,
      },
      {
        id: 'dev_2',
        name: 'Work Laptop',
        deviceType: 'desktop',
        browser: 'Chrome 120',
        os: 'Windows 11',
        lastUsed: new Date(Date.now() - 86400000).toISOString(),
        isCurrent: false,
      },
    ],
    notificationPreferences: {
      email: true,
      sms: true,
      push: true,
      transactionAlerts: true,
      loginAlerts: true,
      marketingEmails: false,
      securityAlerts: true,
    },
    createdAt: '2020-03-15T00:00:00Z',
    updatedAt: new Date().toISOString(),
  };
}

export function generateMockCards(): Card[] {
  return [
    {
      id: 'card_1',
      userId: 'usr_1',
      accountId: 'acc_1',
      cardNumber: '4532015112890346',
      cardHolderName: 'RAHUL SHARMA',
      cardType: 'debit',
      cardNetwork: 'visa',
      expiryDate: '12/27',
      cvv: '***',
      status: 'active',
      dailyLimit: 50000,
      monthlyLimit: 200000,
      domesticLimit: 100000,
      internationalLimit: 50000,
      isVirtual: false,
      issuedAt: '2022-06-15T00:00:00Z',
    },
    {
      id: 'card_2',
      userId: 'usr_1',
      accountId: 'acc_3',
      cardNumber: '5240112222333444',
      cardHolderName: 'RAHUL SHARMA',
      cardType: 'credit',
      cardNetwork: 'mastercard',
      expiryDate: '09/26',
      cvv: '***',
      status: 'active',
      dailyLimit: 100000,
      monthlyLimit: 500000,
      domesticLimit: 200000,
      internationalLimit: 100000,
      isVirtual: false,
      issuedAt: '2023-01-20T00:00:00Z',
    },
    {
      id: 'card_3',
      userId: 'usr_1',
      accountId: 'acc_1',
      cardNumber: '4532015998765432',
      cardHolderName: 'RAHUL SHARMA',
      cardType: 'debit',
      cardNetwork: 'visa',
      expiryDate: '06/28',
      cvv: '***',
      status: 'frozen',
      dailyLimit: 25000,
      monthlyLimit: 100000,
      domesticLimit: 50000,
      internationalLimit: 0,
      isVirtual: true,
      issuedAt: '2024-02-01T00:00:00Z',
    },
  ];
}

export function generateMockLoans(): Loan[] {
  return [
    {
      id: 'loan_1',
      userId: 'usr_1',
      accountId: 'acc_1',
      loanType: 'personal',
      loanAmount: 500000,
      approvedAmount: 450000,
      interestRate: 12.5,
      tenureMonths: 36,
      emiAmount: 15067,
      totalPaid: 180804,
      remainingAmount: 361608,
      status: 'active',
      appliedAt: '2023-05-10T00:00:00Z',
      approvedAt: '2023-05-15T00:00:00Z',
      nextEmiDate: '2024-07-10T00:00:00Z',
      emiSchedule: [],
    },
    {
      id: 'loan_2',
      userId: 'usr_1',
      accountId: 'acc_2',
      loanType: 'car',
      loanAmount: 800000,
      approvedAmount: 750000,
      interestRate: 9.5,
      tenureMonths: 60,
      emiAmount: 15740,
      totalPaid: 94440,
      remainingAmount: 750000,
      status: 'approved',
      appliedAt: '2024-01-05T00:00:00Z',
      approvedAt: '2024-01-12T00:00:00Z',
      nextEmiDate: '2024-07-05T00:00:00Z',
      emiSchedule: [],
    },
  ];
}

export function generateMockBeneficiaries(): Beneficiary[] {
  return [
    {
      id: 'ben_1',
      userId: 'usr_1',
      name: 'Priya Patel',
      accountNumber: '23456789012',
      ifscCode: 'HDFC0004321',
      bankName: 'HDFC Bank',
      accountType: 'savings',
      phone: '+91 98765 12345',
      nickname: 'Priya',
      isUPI: true,
      upiId: 'priya.p@hdfcbank',
      maxTransferLimit: 50000,
      createdAt: '2023-08-15T00:00:00Z',
      isFrequent: true,
    },
    {
      id: 'ben_2',
      userId: 'usr_1',
      name: 'Amit Singh',
      accountNumber: '34567890123',
      ifscCode: 'ICIC0005678',
      bankName: 'ICICI Bank',
      accountType: 'savings',
      email: 'amit.singh@email.com',
      nickname: 'Amit',
      isUPI: false,
      maxTransferLimit: 100000,
      createdAt: '2023-09-20T00:00:00Z',
      isFrequent: false,
    },
    {
      id: 'ben_3',
      userId: 'usr_1',
      name: 'Sneha Reddy',
      accountNumber: '45678901234',
      ifscCode: 'SBIN0005678',
      bankName: 'State Bank of India',
      accountType: 'current',
      isUPI: true,
      upiId: 'sneha.reddy@oksbi',
      maxTransferLimit: 75000,
      createdAt: '2024-02-10T00:00:00Z',
      isFrequent: true,
    },
    {
      id: 'ben_4',
      userId: 'usr_1',
      name: 'Vikram Mehta',
      accountNumber: '56789012345',
      ifscCode: 'AXIS0009876',
      bankName: 'Axis Bank',
      accountType: 'savings',
      phone: '+91 99887 76655',
      nickname: 'Vikram',
      isUPI: false,
      maxTransferLimit: 25000,
      createdAt: '2024-03-05T00:00:00Z',
      isFrequent: false,
    },
  ];
}

export function generateDashboardData(): DashboardData {
  const user = generateMockUser();
  const accounts = generateMockAccounts();
  const transactions = generateMockTransactions();
  const totalBalance = accounts.reduce((sum, acc) => sum + (acc.accountType === 'credit' ? 0 : acc.balance), 0);

  return {
    user,
    accounts,
    recentTransactions: transactions.slice(0, 10),
    totalBalance,
    monthlySpending: 45230,
    spendingChange: -8.5,
    behavioralTrustScore: 85,
    activeCards: 2,
    pendingLoans: 0,
    spendingByCategory: [
      { category: 'Food & Dining', amount: 12500, percentage: 27.6, color: '#3b82f6' },
      { category: 'Transport', amount: 8500, percentage: 18.8, color: '#10b981' },
      { category: 'Shopping', amount: 7200, percentage: 15.9, color: '#f59e0b' },
      { category: 'Bills & Utilities', amount: 6500, percentage: 14.4, color: '#ef4444' },
      { category: 'Entertainment', amount: 4800, percentage: 10.6, color: '#8b5cf6' },
      { category: 'Others', amount: 5730, percentage: 12.7, color: '#ec4899' },
    ],
    spendingTrend: Array.from({ length: 30 }, (_, i) => {
      const date = new Date();
      date.setDate(date.getDate() - (29 - i));
      return {
        date: date.toISOString().split('T')[0],
        amount: Math.round(800 + Math.random() * 2000),
      };
    }),
  };
}


