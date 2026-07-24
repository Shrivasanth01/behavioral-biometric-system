export const APP_NAME = process.env.NEXT_PUBLIC_APP_NAME || 'SecureBank';

export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

export const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws';

export const SESSION_TIMEOUT = Number(process.env.NEXT_PUBLIC_SESSION_TIMEOUT) || 900000;

export const MAX_LOGIN_ATTEMPTS = Number(process.env.NEXT_PUBLIC_MAX_LOGIN_ATTEMPTS) || 5;

export const BEHAVIORAL_SAMPLE_RATE = Number(process.env.NEXT_PUBLIC_BEHAVIORAL_SAMPLE_RATE) || 50;

export const BEHAVIORAL_BATCH_SIZE = Number(process.env.NEXT_PUBLIC_BEHAVIORAL_BATCH_SIZE) || 100;

export const BEHAVIORAL_UPLOAD_INTERVAL = Number(process.env.NEXT_PUBLIC_BEHAVIORAL_UPLOAD_INTERVAL) || 30000;

export const CURRENCY_SYMBOLS: Record<string, string> = {
  INR: '₹',
  USD: '$',
  EUR: '€',
  GBP: '£',
};

export const ACCOUNT_TYPE_COLORS: Record<string, string> = {
  savings: 'bg-blue-500',
  current: 'bg-emerald-500',
  credit: 'bg-purple-500',
  loan: 'bg-orange-500',
};

export const TRANSACTION_CATEGORY_ICONS: Record<string, string> = {
  transfer: 'ArrowRightLeft',
  payment: 'CreditCard',
  recharge: 'Smartphone',
  withdrawal: 'Banknote',
  deposit: 'ArrowDownToLine',
  refund: 'RotateCcw',
  fee: 'Receipt',
  interest: 'Percent',
};

export const RISK_LEVELS = [
  { min: 0, max: 30, label: 'High Risk', color: 'text-red-500', bg: 'bg-red-50' },
  { min: 30, max: 60, label: 'Medium Risk', color: 'text-yellow-500', bg: 'bg-yellow-50' },
  { min: 60, max: 80, label: 'Low Risk', color: 'text-blue-500', bg: 'bg-blue-50' },
  { min: 80, max: 100, label: 'Trusted', color: 'text-green-500', bg: 'bg-green-50' },
];

export const NAV_ITEMS = [
  { label: 'Dashboard', href: '/dashboard', icon: 'LayoutDashboard' },
  { label: 'Accounts', href: '/dashboard/accounts', icon: 'Landmark' },
  { label: 'Transfer', href: '/dashboard/transfer', icon: 'ArrowRightLeft' },
  { label: 'Payments', href: '/dashboard/payments', icon: 'CreditCard' },
  { label: 'Beneficiaries', href: '/dashboard/beneficiaries', icon: 'Users' },
  { label: 'Cards', href: '/dashboard/cards', icon: 'CreditCard' },
  { label: 'Loans', href: '/dashboard/loans', icon: 'HandCoins' },
  { label: 'Transactions', href: '/dashboard/transactions', icon: 'ArrowUpDown' },
  { label: 'Profile', href: '/dashboard/profile', icon: 'UserCircle' },
];

export const SPENDING_COLORS = [
  '#3b82f6',
  '#10b981',
  '#f59e0b',
  '#ef4444',
  '#8b5cf6',
  '#ec4899',
  '#14b8a6',
  '#f97316',
];
