import { z } from 'zod';

export const loginSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
});

export type LoginFormData = z.infer<typeof loginSchema>;

export const registerStep1Schema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters').max(100),
  email: z.string().email('Please enter a valid email address'),
  phone: z.string()
    .min(10, 'Phone number must be at least 10 digits')
    .max(15, 'Phone number is too long')
    .regex(/^\+?[\d\s-]+$/, 'Please enter a valid phone number'),
});

export type RegisterStep1Data = z.infer<typeof registerStep1Schema>;

export const registerStep2Schema = z.object({
  password: z
    .string()
    .min(8, 'Password must be at least 8 characters')
    .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
    .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
    .regex(/[0-9]/, 'Password must contain at least one number')
    .regex(/[^A-Za-z0-9]/, 'Password must contain at least one special character'),
  confirmPassword: z.string(),
}).refine(data => data.password === data.confirmPassword, {
  message: 'Passwords do not match',
  path: ['confirmPassword'],
});

export type RegisterStep2Data = z.infer<typeof registerStep2Schema>;

export const otpSchema = z.object({
  otp: z.string().length(6, 'OTP must be 6 digits').regex(/^\d{6}$/, 'OTP must be numeric'),
});

export type OTPFormData = z.infer<typeof otpSchema>;

export const forgotPasswordSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
});

export type ForgotPasswordFormData = z.infer<typeof forgotPasswordSchema>;

export const resetPasswordSchema = z.object({
  password: z
    .string()
    .min(8, 'Password must be at least 8 characters')
    .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
    .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
    .regex(/[0-9]/, 'Password must contain at least one number'),
  confirmPassword: z.string(),
}).refine(data => data.password === data.confirmPassword, {
  message: 'Passwords do not match',
  path: ['confirmPassword'],
});

export type ResetPasswordFormData = z.infer<typeof resetPasswordSchema>;

export const transferSchema = z.object({
  fromAccountId: z.string().min(1, 'Please select a source account'),
  beneficiaryId: z.string().optional(),
  toAccountNumber: z.string().optional(),
  toIfscCode: z.string().optional(),
  toUpiId: z.string().optional(),
  amount: z.number().min(1, 'Amount must be greater than 0'),
  description: z.string().max(200, 'Description is too long').optional().default(''),
  transferType: z.enum(['internal', 'external', 'upi']),
});

export type TransferFormData = z.infer<typeof transferSchema>;

export const beneficiarySchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  accountNumber: z.string().min(9, 'Account number must be at least 9 digits').max(18),
  ifscCode: z.string().regex(/^[A-Z]{4}0[A-Z0-9]{6}$/, 'Please enter a valid IFSC code'),
  bankName: z.string().min(2, 'Bank name is required'),
  accountType: z.enum(['savings', 'current']),
  nickname: z.string().max(50).optional(),
  phone: z.string().optional(),
  email: z.string().email().optional().or(z.literal('')),
  isUPI: z.boolean().default(false),
  upiId: z.string().optional(),
  maxTransferLimit: z.number().min(1, 'Limit must be greater than 0').default(50000),
});

export type BeneficiaryFormData = z.infer<typeof beneficiarySchema>;

export const changePasswordSchema = z.object({
  currentPassword: z.string().min(1, 'Current password is required'),
  newPassword: z
    .string()
    .min(8, 'Password must be at least 8 characters')
    .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
    .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
    .regex(/[0-9]/, 'Password must contain at least one number'),
  confirmPassword: z.string(),
}).refine(data => data.newPassword === data.confirmPassword, {
  message: 'Passwords do not match',
  path: ['confirmPassword'],
});

export type ChangePasswordFormData = z.infer<typeof changePasswordSchema>;

export const cardLimitSchema = z.object({
  dailyLimit: z.number().min(1000, 'Daily limit must be at least ₹1,000'),
  monthlyLimit: z.number().min(5000, 'Monthly limit must be at least ₹5,000'),
  domesticLimit: z.number().min(1000, 'Domestic limit must be at least ₹1,000'),
  internationalLimit: z.number().min(0, 'International limit cannot be negative'),
});

export type CardLimitFormData = z.infer<typeof cardLimitSchema>;

export const loanApplicationSchema = z.object({
  loanType: z.enum(['personal', 'home', 'car', 'education', 'business']),
  amount: z.number().min(10000, 'Minimum loan amount is ₹10,000').max(10000000, 'Maximum loan amount is ₹1,00,00,000'),
  tenureMonths: z.number().min(6, 'Minimum tenure is 6 months').max(240, 'Maximum tenure is 240 months'),
});

export type LoanApplicationFormData = z.infer<typeof loanApplicationSchema>;

export const profileSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters').max(100),
  email: z.string().email('Please enter a valid email address'),
  phone: z.string().min(10, 'Phone number must be at least 10 digits'),
});

export type ProfileFormData = z.infer<typeof profileSchema>;

export const securityQuestionsSchema = z.array(
  z.object({
    question: z.string().min(1, 'Question is required'),
    answer: z.string().min(2, 'Answer must be at least 2 characters'),
  })
).min(1, 'At least one security question is required').max(3);

export type SecurityQuestionsFormData = z.infer<typeof securityQuestionsSchema>;

export const notificationPreferencesSchema = z.object({
  email: z.boolean(),
  sms: z.boolean(),
  push: z.boolean(),
  transactionAlerts: z.boolean(),
  loginAlerts: z.boolean(),
  marketingEmails: z.boolean(),
  securityAlerts: z.boolean(),
});

export type NotificationPreferencesFormData = z.infer<typeof notificationPreferencesSchema>;
