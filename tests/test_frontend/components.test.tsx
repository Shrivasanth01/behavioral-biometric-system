import { formatCurrency, formatDate, formatDateTime, timeAgo, maskAccountNumber, maskCardNumber, formatCardNumber, getInitials, generateTransactionReference, getRiskLevel, getStatusColor, calculateEMI, getTotalInterest } from '../lib/utils';
import { loginSchema, registerStep2Schema, transferSchema, beneficiarySchema } from '../lib/validators';
import { CURRENCY_SYMBOLS, RISK_LEVELS, ACCOUNT_TYPE_COLORS } from '../lib/constants';

describe('Utility Functions', () => {
  describe('formatCurrency', () => {
    it('formats INR correctly', () => {
      const result = formatCurrency(284750.50, 'INR');
      expect(result).toContain(CURRENCY_SYMBOLS.INR);
      expect(result).toContain('2,84,750.50');
    });

    it('formats USD correctly', () => {
      const result = formatCurrency(1000, 'USD');
      expect(result).toContain('$');
    });

    it('defaults to INR', () => {
      const result = formatCurrency(500);
      expect(result).toContain(CURRENCY_SYMBOLS.INR);
    });

    it('handles zero', () => {
      expect(formatCurrency(0)).toContain('0.00');
    });
  });

  describe('formatDate', () => {
    it('formats ISO date string', () => {
      const result = formatDate('2024-06-14T10:30:00Z');
      expect(result).toMatch(/\d{2} \w{3} \d{4}/);
    });

    it('handles invalid date', () => {
      expect(formatDate('not-a-date')).toBe('not-a-date');
    });
  });

  describe('formatDateTime', () => {
    it('includes time component', () => {
      const result = formatDateTime('2024-06-14T10:30:00Z');
      expect(result).toMatch(/\d{2}:\d{2}/);
    });
  });

  describe('timeAgo', () => {
    it('returns relative time', () => {
      const recent = new Date(Date.now() - 3600000).toISOString();
      expect(timeAgo(recent)).toContain('ago');
    });
  });

  describe('maskAccountNumber', () => {
    it('masks all but last 4 digits', () => {
      expect(maskAccountNumber('12345678901')).toBe('XXXX8901');
    });

    it('returns short numbers unchanged', () => {
      expect(maskAccountNumber('1234')).toBe('1234');
    });
  });

  describe('maskCardNumber', () => {
    it('masks with dots', () => {
      expect(maskCardNumber('4532015112890346')).toContain('0346');
    });
  });

  describe('formatCardNumber', () => {
    it('formats in groups of 4', () => {
      expect(formatCardNumber('4532015112890346')).toBe('4532 0151 1289 0346');
    });
  });

  describe('getInitials', () => {
    it('extracts first two initials', () => {
      expect(getInitials('Rahul Sharma')).toBe('RS');
    });

    it('handles single name', () => {
      expect(getInitials('Rahul')).toBe('R');
    });
  });

  describe('generateTransactionReference', () => {
    it('starts with TXN', () => {
      expect(generateTransactionReference()).toMatch(/^TXN/);
    });
  });

  describe('getRiskLevel', () => {
    it('returns High Risk for low scores', () => {
      expect(getRiskLevel(10).label).toBe('High Risk');
    });

    it('returns Trusted for high scores', () => {
      expect(getRiskLevel(90).label).toBe('Trusted');
    });

    it('returns Medium Risk for mid scores', () => {
      expect(getRiskLevel(45).label).toBe('Medium Risk');
    });
  });

  describe('getStatusColor', () => {
    it('returns green for active', () => {
      expect(getStatusColor('active')).toContain('green');
    });

    it('returns gray for unknown status', () => {
      expect(getStatusColor('unknown')).toContain('gray');
    });
  });

  describe('calculateEMI', () => {
    it('calculates EMI correctly for standard loan', () => {
      const emi = calculateEMI(500000, 10.5, 60);
      expect(emi).toBeGreaterThan(0);
      expect(emi).toBeLessThan(500000);
    });

    it('handles zero interest', () => {
      const emi = calculateEMI(120000, 0, 12);
      expect(emi).toBe(10000);
    });
  });

  describe('getTotalInterest', () => {
    it('calculates total interest correctly', () => {
      const interest = getTotalInterest(500000, 10.5, 60);
      expect(interest).toBeGreaterThan(0);
    });
  });
});

describe('Validation Schemas', () => {
  describe('loginSchema', () => {
    it('validates correct login data', () => {
      const result = loginSchema.safeParse({ email: 'test@example.com', password: 'password123' });
      expect(result.success).toBe(true);
    });

    it('rejects invalid email', () => {
      const result = loginSchema.safeParse({ email: 'invalid', password: 'password123' });
      expect(result.success).toBe(false);
    });

    it('rejects short password', () => {
      const result = loginSchema.safeParse({ email: 'test@example.com', password: '12345' });
      expect(result.success).toBe(false);
    });
  });

  describe('registerStep2Schema', () => {
    it('validates strong password match', () => {
      const result = registerStep2Schema.safeParse({
        password: 'StrongP@ss1',
        confirmPassword: 'StrongP@ss1',
      });
      expect(result.success).toBe(true);
    });

    it('rejects weak password', () => {
      const result = registerStep2Schema.safeParse({
        password: 'weak',
        confirmPassword: 'weak',
      });
      expect(result.success).toBe(false);
    });

    it('rejects mismatched passwords', () => {
      const result = registerStep2Schema.safeParse({
        password: 'StrongP@ss1',
        confirmPassword: 'DifferentP@ss1',
      });
      expect(result.success).toBe(false);
    });
  });

  describe('transferSchema', () => {
    it('validates internal transfer', () => {
      const result = transferSchema.safeParse({
        fromAccountId: 'acc_1',
        toAccountNumber: '1234567890',
        amount: 1000,
        transferType: 'internal',
      });
      expect(result.success).toBe(true);
    });

    it('rejects zero amount', () => {
      const result = transferSchema.safeParse({
        fromAccountId: 'acc_1',
        amount: 0,
        transferType: 'internal',
      });
      expect(result.success).toBe(false);
    });
  });

  describe('beneficiarySchema', () => {
    it('validates correct beneficiary', () => {
      const result = beneficiarySchema.safeParse({
        name: 'Test User',
        accountNumber: '12345678901',
        ifscCode: 'SBIN0001234',
        bankName: 'SBI',
        accountType: 'savings',
      });
      expect(result.success).toBe(true);
    });
  });
});
