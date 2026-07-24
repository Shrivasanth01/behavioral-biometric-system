export interface User {
  id: string;
  email: string;
  name: string;
  phone: string;
  avatar?: string;
  role: 'customer' | 'admin';
  mfaEnabled: boolean;
  mfaMethod?: 'app' | 'sms' | 'email';
  behavioralProfileStatus: 'unavailable' | 'pending' | 'complete' | 'low_confidence';
  trustedDevices: TrustedDevice[];
  notificationPreferences: NotificationPreferences;
  createdAt: string;
  updatedAt: string;
}

export interface TrustedDevice {
  id: string;
  name: string;
  deviceType: string;
  browser: string;
  os: string;
  lastUsed: string;
  isCurrent: boolean;
}

export interface NotificationPreferences {
  email: boolean;
  sms: boolean;
  push: boolean;
  transactionAlerts: boolean;
  loginAlerts: boolean;
  marketingEmails: boolean;
  securityAlerts: boolean;
}

export interface Account {
  id: string;
  userId: string;
  accountNumber: string;
  accountType: 'savings' | 'current' | 'credit' | 'loan';
  accountName: string;
  currency: string;
  balance: number;
  availableBalance: number;
  status: 'active' | 'dormant' | 'frozen' | 'closed';
  ifscCode: string;
  branchName: string;
  openedAt: string;
}

export interface Transaction {
  id: string;
  accountId: string;
  type: 'credit' | 'debit';
  category: 'transfer' | 'payment' | 'recharge' | 'withdrawal' | 'deposit' | 'refund' | 'fee' | 'interest';
  amount: number;
  currency: string;
  description: string;
  reference: string;
  status: 'pending' | 'completed' | 'failed' | 'reversed';
  counterparty?: string;
  counterpartyAccount?: string;
  transactionDate: string;
  createdAt: string;
  riskScore?: number;
}

export interface Beneficiary {
  id: string;
  userId: string;
  name: string;
  accountNumber: string;
  ifscCode: string;
  bankName: string;
  accountType: 'savings' | 'current';
  email?: string;
  phone?: string;
  nickname?: string;
  isUPI: boolean;
  upiId?: string;
  maxTransferLimit: number;
  createdAt: string;
  isFrequent: boolean;
}

export interface Card {
  id: string;
  userId: string;
  accountId: string;
  cardNumber: string;
  cardHolderName: string;
  cardType: 'credit' | 'debit';
  cardNetwork: 'visa' | 'mastercard' | 'rupay';
  expiryDate: string;
  cvv: string;
  status: 'active' | 'frozen' | 'blocked' | 'expired';
  dailyLimit: number;
  monthlyLimit: number;
  domesticLimit: number;
  internationalLimit: number;
  isVirtual: boolean;
  issuedAt: string;
}

export interface Loan {
  id: string;
  userId: string;
  accountId: string;
  loanType: 'personal' | 'home' | 'car' | 'education' | 'business';
  loanAmount: number;
  approvedAmount: number;
  interestRate: number;
  tenureMonths: number;
  emiAmount: number;
  totalPaid: number;
  remainingAmount: number;
  status: 'pending' | 'approved' | 'active' | 'closed' | 'rejected';
  appliedAt: string;
  approvedAt?: string;
  nextEmiDate?: string;
  emiSchedule: EMISchedule[];
}

export interface EMISchedule {
  id: string;
  loanId: string;
  installmentNumber: number;
  dueDate: string;
  amount: number;
  principal: number;
  interest: number;
  status: 'pending' | 'paid' | 'overdue';
  paidAt?: string;
}

export interface BehavioralEvent {
  type: string;
  timestamp: number;
  data: Record<string, unknown>;
  sessionId: string;
  userId?: string;
}

export interface Session {
  id: string;
  userId: string;
  deviceInfo: DeviceInfo;
  ipAddress: string;
  location?: string;
  startedAt: string;
  lastActivity: string;
  isActive: boolean;
  riskScore: number;
}

export interface DeviceInfo {
  screenResolution: string;
  colorDepth: number;
  timezone: string;
  language: string;
  platform: string;
  userAgent: string;
  canvasFingerprint?: string;
  webglFingerprint?: string;
  audioFingerprint?: string;
  fonts?: string[];
}

export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> {
  success: boolean;
  data: T[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}

export interface OTPRequest {
  phone?: string;
  email?: string;
  purpose: 'registration' | 'login' | 'transfer' | 'password_reset' | 'mfa';
}

export interface OTPVerify {
  otp: string;
  requestId: string;
}

export interface TransferRequest {
  fromAccountId: string;
  toAccountNumber?: string;
  toIfscCode?: string;
  toUpiId?: string;
  beneficiaryId?: string;
  amount: number;
  description: string;
  transferType: 'internal' | 'external' | 'upi';
  otp?: string;
  requestId?: string;
}

export interface LoginRequest {
  email: string;
  password: string;
  behavioralToken?: string;
  deviceInfo?: DeviceInfo;
}

export interface RegisterRequest {
  full_name: string;
  email: string;
  phone: string;
  password: string;
}

export interface SecurityQuestion {
  question: string;
  answer: string;
}

export interface PasswordResetRequest {
  email: string;
  otp?: string;
  newPassword?: string;
  requestId?: string;
}

export interface DashboardData {
  user: User;
  accounts: Account[];
  recentTransactions: Transaction[];
  totalBalance: number;
  monthlySpending: number;
  spendingChange: number;
  behavioralTrustScore: number;
  activeCards: number;
  pendingLoans: number;
  spendingByCategory: SpendingCategory[];
  spendingTrend: SpendingTrend[];
}

export interface SpendingCategory {
  category: string;
  amount: number;
  percentage: number;
  color: string;
}

export interface SpendingTrend {
  date: string;
  amount: number;
}
