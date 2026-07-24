'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/Button';
import { cn } from '@/lib/utils';

interface OTPVerificationProps {
  length?: number;
  onVerify: (otp: string) => Promise<void>;
  onResend: () => Promise<void>;
  isLoading?: boolean;
  error?: string;
  title?: string;
  subtitle?: string;
}

export function OTPVerification({
  length = 6,
  onVerify,
  onResend,
  isLoading = false,
  error,
  title = 'Verify OTP',
  subtitle = 'Enter the 6-digit code sent to your device',
}: OTPVerificationProps) {
  const [otp, setOtp] = useState<string[]>(Array(length).fill(''));
  const [resendTimer, setResendTimer] = useState(30);
  const [canResend, setCanResend] = useState(false);
  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

  useEffect(() => {
    if (resendTimer > 0 && !canResend) {
      const timer = setInterval(() => {
        setResendTimer(prev => {
          if (prev <= 1) {
            setCanResend(true);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
      return () => clearInterval(timer);
    }
  }, [resendTimer, canResend]);

  const handleChange = (index: number, value: string) => {
    if (!/^\d*$/.test(value)) return;
    const newOtp = [...otp];
    newOtp[index] = value.slice(-1);
    setOtp(newOtp);

    if (value && index < length - 1) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  const handleKeyDown = (index: number, e: React.KeyboardEvent) => {
    if (e.key === 'Backspace' && !otp[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
    if (e.key === 'Enter') {
      handleSubmit();
    }
  };

  const handlePaste = (e: React.ClipboardEvent) => {
    e.preventDefault();
    const pasted = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, length);
    const newOtp = Array(length).fill('');
    pasted.split('').forEach((char, i) => {
      newOtp[i] = char;
    });
    setOtp(newOtp);
    const nextIndex = Math.min(pasted.length, length - 1);
    inputRefs.current[nextIndex]?.focus();
  };

  const handleSubmit = () => {
    const otpString = otp.join('');
    if (otpString.length === length) {
      onVerify(otpString);
    }
  };

  const handleResend = async () => {
    setCanResend(false);
    setResendTimer(30);
    await onResend();
    setOtp(Array(length).fill(''));
    inputRefs.current[0]?.focus();
  };

  const isComplete = otp.every(d => d !== '');

  return (
    <div className="text-center">
      <h3 className="text-lg font-semibold text-navy-900">{title}</h3>
      <p className="text-sm text-gray-500 mt-1 mb-6">{subtitle}</p>

      {error && (
        <div className="mb-4 p-3 bg-danger-50 border border-danger-200 rounded-lg text-sm text-danger-700">
          {error}
        </div>
      )}

      <div className="flex gap-2 justify-center mb-6" onPaste={handlePaste}>
        {otp.map((digit, index) => (
          <input
            key={index}
            ref={el => { inputRefs.current[index] = el; }}
            type="text"
            inputMode="numeric"
            maxLength={1}
            value={digit}
            onChange={(e) => handleChange(index, e.target.value)}
            onKeyDown={(e) => handleKeyDown(index, e)}
            className={cn(
              'w-12 h-14 text-center text-lg font-semibold border-2 rounded-lg focus:outline-none focus:ring-2 transition-all duration-200',
              digit
                ? 'border-primary-500 focus:border-primary-600 focus:ring-primary-500/20'
                : 'border-gray-300 focus:border-primary-500 focus:ring-primary-500/20'
            )}
            autoFocus={index === 0}
          />
        ))}
      </div>

      <Button
        className="w-full"
        onClick={handleSubmit}
        isLoading={isLoading}
        disabled={!isComplete}
      >
        Verify & Continue
      </Button>

      <div className="mt-4 text-sm text-gray-500">
        {canResend ? (
          <button onClick={handleResend} className="text-primary-600 hover:text-primary-700 font-medium">
            Resend OTP
          </button>
        ) : (
          <span>Resend code in <span className="font-medium text-navy-700">{resendTimer}s</span></span>
        )}
      </div>
    </div>
  );
}
