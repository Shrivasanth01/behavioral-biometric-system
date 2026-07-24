import { API_URL } from './constants';
import type {
  ApiResponse, AuthTokens, LoginRequest, RegisterRequest,
  TransferRequest, OTPRequest, OTPVerify, PasswordResetRequest,
  User, Account, Transaction, Beneficiary, Card, Loan,
  DashboardData, PaginatedResponse, BehavioralEvent,
} from '@/types';

let accessToken: string | null = null;
let refreshToken: string | null = null;
let refreshPromise: Promise<boolean> | null = null;

export function setTokens(tokens: AuthTokens): void {
  accessToken = tokens.accessToken;
  refreshToken = tokens.refreshToken;
  if (typeof window !== 'undefined') {
    localStorage.setItem('access_token', tokens.accessToken);
    localStorage.setItem('refresh_token', tokens.refreshToken);
  }
}

export function clearTokens(): void {
  accessToken = null;
  refreshToken = null;
  if (typeof window !== 'undefined') {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }
}

export function loadTokens(): void {
  if (typeof window !== 'undefined') {
    accessToken = localStorage.getItem('access_token');
    refreshToken = localStorage.getItem('refresh_token');
  }
}

export function getAccessToken(): string | null {
  return accessToken;
}

async function refreshAccessToken(): Promise<boolean> {
  if (!refreshToken) return false;
  try {
    const response = await fetch(`${API_URL}/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refreshToken }),
    });
    if (!response.ok) {
      clearTokens();
      return false;
    }
    const data: ApiResponse<AuthTokens> = await response.json();
    if (data.success && data.data) {
      setTokens(data.data);
      return true;
    }
    return false;
  } catch {
    return false;
  }
}

export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  loadTokens();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };
  if (accessToken) {
    headers['Authorization'] = `Bearer ${accessToken}`;
  }

  let response: Response;
  try {
    response = await fetch(`${API_URL}${endpoint}`, {
      ...options,
      headers,
    });
  } catch (err) {
    // network error (CORS blocked, connection refused, DNS failure)
    // Log to console so developers can inspect details in browser devtools
    // and return a structured ApiResponse for the UI to display.
    // eslint-disable-next-line no-console
    console.error('Network error while calling API', API_URL + endpoint, err);
    return { success: false, error: (err as Error).message || 'Network error' } as ApiResponse<T>;
  }

  // Catch network-level issues (CORS, DNS, connection refused) with a clearer error

  if (response.status === 401 && refreshToken) {
    if (!refreshPromise) {
      refreshPromise = refreshAccessToken();
    }
    const refreshed = await refreshPromise;
    refreshPromise = null;

    if (refreshed) {
      headers['Authorization'] = `Bearer ${accessToken}`;
      response = await fetch(`${API_URL}${endpoint}`, {
        ...options,
        headers,
      });
    } else {
      clearTokens();
      return { success: false, error: 'Session expired. Please login again.' };
    }
  }

  let data: ApiResponse<T>;
  try {
    data = await response.json();
  } catch (err) {
    // Non-JSON response (server error pages, empty responses)
    // eslint-disable-next-line no-console
    console.error('Failed to parse JSON response from', API_URL + endpoint, err);
    return { success: false, error: response.statusText || `HTTP ${response.status}` } as ApiResponse<T>;
  }

  return data;
}

export const api = {
  auth: {
    login: (data: LoginRequest) =>
      apiRequest<{ user: User; tokens: AuthTokens }>('/auth/login', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    register: (data: RegisterRequest) =>
      apiRequest<{ user: User; tokens: AuthTokens }>('/auth/register', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    logout: () =>
      apiRequest<null>('/auth/logout', { method: 'POST' }),
    me: () =>
      apiRequest<User>('/auth/me'),
    sendOTP: (data: OTPRequest) =>
      apiRequest<{ requestId: string }>('/auth/send-otp', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    verifyOTP: (data: OTPVerify) =>
      apiRequest<{ verified: boolean }>('/auth/verify-otp', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    forgotPassword: (data: PasswordResetRequest) =>
      apiRequest<{ requestId: string }>('/auth/forgot-password', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    resetPassword: (data: PasswordResetRequest) =>
      apiRequest<null>('/auth/reset-password', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    changePassword: (data: { currentPassword: string; newPassword: string }) =>
      apiRequest<null>('/auth/change-password', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    setupMFA: (method: 'app' | 'sms' | 'email') =>
      apiRequest<{ secret?: string; qrCode?: string }>('/auth/mfa/setup', {
        method: 'POST',
        body: JSON.stringify({ method }),
      }),
    verifyMFA: (data: { code: string; method: string }) =>
      apiRequest<{ enabled: boolean }>('/auth/mfa/verify', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    disableMFA: () =>
      apiRequest<null>('/auth/mfa/disable', { method: 'POST' }),
  },

  accounts: {
    list: () =>
      apiRequest<Account[]>('/accounts'),
    get: (id: string) =>
      apiRequest<Account>(`/accounts/${id}`),
    statement: (id: string, params?: { from?: string; to?: string }) => {
      const query = params ? `?${new URLSearchParams(params as Record<string, string>)}` : '';
      return apiRequest<Transaction[]>(`/accounts/${id}/statement${query}`);
    },
  },

  transactions: {
    list: (params?: { page?: number; limit?: number; type?: string; from?: string; to?: string }) => {
      const query = params ? `?${new URLSearchParams(params as Record<string, string>)}` : '';
      return apiRequest<PaginatedResponse<Transaction>>(`/transactions${query}`);
    },
    get: (id: string) =>
      apiRequest<Transaction>(`/transactions/${id}`),
  },

  transfers: {
    create: (data: TransferRequest) =>
      apiRequest<{ transaction: Transaction; riskScore?: number }>('/transfers', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    verifyOTP: (data: { transferId: string; otp: string; requestId: string }) =>
      apiRequest<{ completed: boolean }>('/transfers/verify-otp', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
  },

  beneficiaries: {
    list: () =>
      apiRequest<Beneficiary[]>('/beneficiaries'),
    create: (data: Partial<Beneficiary>) =>
      apiRequest<Beneficiary>('/beneficiaries', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    update: (id: string, data: Partial<Beneficiary>) =>
      apiRequest<Beneficiary>(`/beneficiaries/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      }),
    delete: (id: string) =>
      apiRequest<null>(`/beneficiaries/${id}`, { method: 'DELETE' }),
  },

  cards: {
    list: () =>
      apiRequest<Card[]>('/cards'),
    get: (id: string) =>
      apiRequest<Card>(`/cards/${id}`),
    toggleFreeze: (id: string) =>
      apiRequest<Card>(`/cards/${id}/toggle-freeze`, { method: 'POST' }),
    updateLimits: (id: string, data: Partial<Card>) =>
      apiRequest<Card>(`/cards/${id}/limits`, {
        method: 'PUT',
        body: JSON.stringify(data),
      }),
    request: (data: { accountId: string; cardType: string; cardNetwork: string }) =>
      apiRequest<Card>('/cards/request', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
  },

  loans: {
    list: () =>
      apiRequest<Loan[]>('/loans'),
    get: (id: string) =>
      apiRequest<Loan>(`/loans/${id}`),
    apply: (data: { loanType: string; amount: number; tenureMonths: number }) =>
      apiRequest<Loan>('/loans/apply', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
  },

  dashboard: {
    get: () =>
      apiRequest<DashboardData>('/dashboard'),
  },

  profile: {
    update: (data: Partial<User>) =>
      apiRequest<User>('/profile', {
        method: 'PUT',
        body: JSON.stringify(data),
      }),
    updateNotifications: (data: User['notificationPreferences']) =>
      apiRequest<User>('/profile/notifications', {
        method: 'PUT',
        body: JSON.stringify(data),
      }),
    removeDevice: (deviceId: string) =>
      apiRequest<null>(`/profile/devices/${deviceId}`, { method: 'DELETE' }),
  },

  behavioral: {
    uploadEvents: (events: BehavioralEvent[]) =>
      apiRequest<null>('/behavioral/events', {
        method: 'POST',
        body: JSON.stringify({ events }),
      }),
    getProfile: () =>
      apiRequest<{ status: string; confidence: number; traits: Record<string, unknown> }>('/behavioral/profile'),
    baseline: () =>
      apiRequest<{ status: string }>('/behavioral/baseline'),
  },
};
