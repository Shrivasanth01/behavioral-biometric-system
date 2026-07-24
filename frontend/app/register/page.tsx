'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/lib/auth';
import { APP_NAME, API_URL } from '@/lib/constants';
import { PasswordStrength } from '@/components/auth/PasswordStrength';
import { OTPVerification } from '@/components/auth/OTPVerification';
import { Button } from '@/components/ui/Button';
import { Building2, ArrowLeft, ArrowRight, Check, Eye, EyeOff, User, Mail, Phone, Lock, Shield, Keyboard } from 'lucide-react';
import { cn } from '@/lib/utils';

interface FormData {
  name: string;
  email: string;
  phone: string;
  password: string;
  confirmPassword: string;
}

const SECURITY_QUESTIONS = [
  'What was the name of your first pet?',
  'What is your mother\'s maiden name?',
  'What was the name of your elementary school?',
  'What city were you born in?',
  'What is your favorite book?',
];

export default function RegisterPage() {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState<FormData>({
    name: '',
    email: '',
    phone: '',
    password: '',
    confirmPassword: '',
  });
  const [errors, setErrors] = useState<Partial<FormData>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [otpError, setOtpError] = useState('');
  const [registerError, setRegisterError] = useState('');
  const [registerErrorUrl, setRegisterErrorUrl] = useState('');
  const [securityQA, setSecurityQA] = useState<{ question: string; answer: string }[]>([]);
  const [baselineText, setBaselineText] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const router = useRouter();
  const { register } = useAuth();

  const validateStep1 = (): boolean => {
    const newErrors: Partial<FormData> = {};
    if (!formData.name || formData.name.length < 2) newErrors.name = 'Name must be at least 2 characters';
    if (!formData.email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) newErrors.email = 'Please enter a valid email';
    if (!formData.phone || formData.phone.replace(/\D/g, '').length < 10) newErrors.phone = 'Please enter a valid phone number';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const validateStep2 = (): boolean => {
    const newErrors: Partial<FormData> = {};
    if (!formData.password || formData.password.length < 8) newErrors.password = 'Password must be at least 8 characters';
    if (!/[A-Z]/.test(formData.password)) newErrors.password = 'Password needs an uppercase letter';
    if (!/[a-z]/.test(formData.password)) newErrors.password = 'Password needs a lowercase letter';
    if (!/[0-9]/.test(formData.password)) newErrors.password = 'Password needs a number';
    if (!/[^A-Za-z0-9]/.test(formData.password)) newErrors.password = 'Password needs a special character';
    if (formData.password !== formData.confirmPassword) newErrors.confirmPassword = 'Passwords do not match';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (step === 1 && validateStep1()) setStep(2);
    else if (step === 2 && validateStep2()) setStep(3);
  };

  const handleOTPVerify = async (otp: string) => {
    setIsLoading(true);
    setOtpError('');
    try {
      await new Promise(resolve => setTimeout(resolve, 1500));
      setStep(4);
    } catch {
      setOtpError('Invalid OTP. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleOTPResend = async () => {
    await new Promise(resolve => setTimeout(resolve, 1000));
  };

  const handleRegister = async () => {
    setIsLoading(true);
    setRegisterError('');
    try {
      const result = await register({
        full_name: formData.name,
        email: formData.email,
        phone: formData.phone,
        password: formData.password,
      });
      if (result.success) {
        router.push('/dashboard');
      } else {
        setErrors({ email: result.error || 'Registration failed. Please try again.' });
        setRegisterError(typeof result.error === 'string' ? result.error : 'Registration failed. Please try again.');
        setRegisterErrorUrl(`${API_URL}/auth/register`);
      }
    } catch {
      setErrors({ email: 'Registration failed. Please try again.' });
      setRegisterError('Registration failed. Please try again.');
      setRegisterErrorUrl(`${API_URL}/auth/register`);
    } finally {
      setIsLoading(false);
    }
  };

  const BASELINE_PARAGRAPH = `The quick brown fox jumps over the lazy dog. Pack my box with five dozen liquor jugs. How vexingly quick daft zebras jump! The five boxing wizards jump quickly. Sphinx of black quartz, judge my vow.`;

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 flex items-center justify-center p-4">
      <div className="w-full max-w-lg animate-in">
        <div className="text-center mb-8">
          <Link href="/" className="inline-flex items-center gap-2">
            <div className="w-10 h-10 bg-primary-600 rounded-xl flex items-center justify-center">
              <Building2 className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-bold text-navy-900">{APP_NAME}</span>
          </Link>
        </div>

        <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-8">
          <div className="flex items-center justify-between mb-8">
            <div>
              {step > 1 && (
                <button onClick={() => setStep(step - 1)} className="text-gray-400 hover:text-gray-600 mb-2">
                  <ArrowLeft className="w-5 h-5" />
                </button>
              )}
              <h2 className="text-xl font-bold text-navy-900">
                {step === 1 && 'Personal Details'}
                {step === 2 && 'Create Password'}
                {step === 3 && 'Verify Phone'}
                {step === 4 && 'Security Questions'}
                {step === 5 && 'Behavioral Baseline'}
              </h2>
              <p className="text-sm text-gray-500 mt-1">
                Step {step} of 5
              </p>
            </div>
            <div className="flex gap-1">
              {[1, 2, 3, 4, 5].map(s => (
                <div
                  key={s}
                  className={cn(
                    'w-8 h-1 rounded-full transition-colors',
                    s <= step ? 'bg-primary-600' : 'bg-gray-200'
                  )}
                />
              ))}
            </div>
          </div>

          {step === 1 && (
            <div className="space-y-5">
              <div>
                <label className="label">Full Name</label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    type="text"
                    value={formData.name}
                    onChange={e => setFormData(p => ({ ...p, name: e.target.value }))}
                    className="input-field pl-10"
                    placeholder="John Doe"
                  />
                </div>
                {errors.name && <p className="text-sm text-danger-600 mt-1">{errors.name}</p>}
              </div>
              <div>
                <label className="label">Email Address</label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    type="email"
                    value={formData.email}
                    onChange={e => setFormData(p => ({ ...p, email: e.target.value }))}
                    className="input-field pl-10"
                    placeholder="you@example.com"
                  />
                </div>
                {errors.email && <p className="text-sm text-danger-600 mt-1">{errors.email}</p>}
              </div>
              <div>
                <label className="label">Phone Number</label>
                <div className="relative">
                  <Phone className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    type="tel"
                    value={formData.phone}
                    onChange={e => setFormData(p => ({ ...p, phone: e.target.value }))}
                    className="input-field pl-10"
                    placeholder="+91 98765 43210"
                  />
                </div>
                {errors.phone && <p className="text-sm text-danger-600 mt-1">{errors.phone}</p>}
              </div>
              <Button className="w-full" onClick={handleNext} rightIcon={<ArrowRight className="w-4 h-4" />}>
                Continue
              </Button>
            </div>
          )}

          {step === 2 && (
            <div className="space-y-5">
              <div>
                <label className="label">Password</label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={formData.password}
                    onChange={e => setFormData(p => ({ ...p, password: e.target.value }))}
                    className="input-field pl-10 pr-10"
                    placeholder="Create a strong password"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400"
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
                <PasswordStrength password={formData.password} />
                {errors.password && <p className="text-sm text-danger-600 mt-1">{errors.password}</p>}
              </div>
              <div>
                <label className="label">Confirm Password</label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    type={showConfirmPassword ? 'text' : 'password'}
                    value={formData.confirmPassword}
                    onChange={e => setFormData(p => ({ ...p, confirmPassword: e.target.value }))}
                    className="input-field pl-10 pr-10"
                    placeholder="Confirm your password"
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400"
                  >
                    {showConfirmPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
                {errors.confirmPassword && <p className="text-sm text-danger-600 mt-1">{errors.confirmPassword}</p>}
              </div>
              <Button className="w-full" onClick={handleNext} rightIcon={<ArrowRight className="w-4 h-4" />}>
                Continue
              </Button>
            </div>
          )}

          {step === 3 && (
            <OTPVerification
              onVerify={handleOTPVerify}
              onResend={handleOTPResend}
              isLoading={isLoading}
              error={otpError}
              subtitle={`Enter the 6-digit code sent to ${formData.phone}`}
            />
          )}

          {step === 4 && (
            <div className="space-y-5">
              <p className="text-sm text-gray-500">Set up security questions to help recover your account (optional).</p>
              {securityQA.map((qa, i) => (
                <div key={i} className="p-4 bg-gray-50 rounded-lg space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-navy-700">Question {i + 1}</span>
                    <button
                      onClick={() => setSecurityQA(prev => prev.filter((_, j) => j !== i))}
                      className="text-danger-600 text-sm hover:text-danger-700"
                    >
                      Remove
                    </button>
                  </div>
                  <select
                    value={qa.question}
                    onChange={e => {
                      const newQA = [...securityQA];
                      newQA[i] = { ...newQA[i], question: e.target.value };
                      setSecurityQA(newQA);
                    }}
                    className="input-field"
                  >
                    <option value="">Select a question</option>
                    {SECURITY_QUESTIONS.map(q => (
                      <option key={q} value={q}>{q}</option>
                    ))}
                  </select>
                  <input
                    type="text"
                    value={qa.answer}
                    onChange={e => {
                      const newQA = [...securityQA];
                      newQA[i] = { ...newQA[i], answer: e.target.value };
                      setSecurityQA(newQA);
                    }}
                    className="input-field"
                    placeholder="Your answer"
                  />
                </div>
              ))}
              {securityQA.length < 3 && (
                <button
                  onClick={() => setSecurityQA(prev => [...prev, { question: '', answer: '' }])}
                  className="text-primary-600 text-sm font-medium hover:text-primary-700"
                >
                  + Add another question
                </button>
              )}
              <Button className="w-full" onClick={() => setStep(5)} rightIcon={<ArrowRight className="w-4 h-4" />}>
                Continue
              </Button>
            </div>
          )}

          {step === 5 && (
            <div className="space-y-5">
              <div className="flex items-center gap-2 p-3 bg-blue-50 text-blue-700 rounded-lg text-sm">
                <Keyboard className="w-4 h-4 shrink-0" />
                Type the paragraph below naturally. This helps us create your unique typing profile.
              </div>
              <div className="p-4 bg-gray-50 rounded-lg text-sm text-gray-600 leading-relaxed border border-gray-200">
                {BASELINE_PARAGRAPH}
              </div>
              <textarea
                value={baselineText}
                onChange={e => setBaselineText(e.target.value)}
                className="input-field h-32 resize-none"
                placeholder="Start typing the paragraph above naturally..."
              />
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-500">{baselineText.length} characters</span>
                {baselineText.length > 50 && (
                  <span className="text-success-600 flex items-center gap-1">
                    <Check className="w-4 h-4" /> Sample captured
                  </span>
                )}
              </div>
              <div className="flex gap-3">
                <Button
                  variant="secondary"
                  className="flex-1"
                  onClick={handleRegister}
                  isLoading={isLoading}
                >
                  Skip
                </Button>
                <Button
                  className="flex-1"
                  onClick={handleRegister}
                  isLoading={isLoading}
                  disabled={baselineText.length < 20}
                >
                  Complete Registration
                </Button>
              </div>
              {registerError && (
                <div className="mt-2">
                  <p className="text-sm text-danger-600">{registerError}</p>
                  {registerErrorUrl && (
                    <p className="text-xs text-gray-500 mt-1">Request URL: {registerErrorUrl}</p>
                  )}
                </div>
              )}
            </div>
          )}
        </div>

        <p className="text-center text-sm text-gray-500 mt-6">
          Already have an account?{' '}
          <Link href="/" className="text-primary-600 hover:text-primary-700 font-semibold">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
