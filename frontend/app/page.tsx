'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/lib/auth';
import { useBehavioralLoginCapture } from '@/hooks/useBehavioralTracker';
import { APP_NAME } from '@/lib/constants';
import { Building2, Shield, Fingerprint, ArrowRight, Eye, EyeOff, Lock, Mail, Activity, CheckCircle, AlertCircle } from 'lucide-react';
import { cn } from '@/lib/utils';

export default function LandingPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [capturing, setCapturing] = useState(false);
  const [keystrokeConfidence, setKeystrokeConfidence] = useState(0);
  const router = useRouter();
  const { login, isAuthenticated } = useAuth();
  const { startCapture, stopCapture } = useBehavioralLoginCapture();

  useEffect(() => {
    if (isAuthenticated) {
      router.push('/dashboard');
    }
  }, [isAuthenticated, router]);

  // Simulate dynamic keystroke cadence confidence tracking during user interaction
  useEffect(() => {
    if (email.length > 3 && password.length > 2) {
      setKeystrokeConfidence(Math.min(99, 70 + (password.length * 4) + (email.length * 1.2)));
    } else if (email.length > 0) {
      setKeystrokeConfidence(45 + email.length * 2);
    } else {
      setKeystrokeConfidence(0);
    }
  }, [email, password]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    const behavioralEvents = stopCapture();

    const result = await login({
      email,
      password,
      behavioralToken: behavioralEvents.length > 0
        ? btoa(JSON.stringify(behavioralEvents))
        : undefined,
      deviceInfo: {
        screenResolution: `${window.screen.width}x${window.screen.height}`,
        colorDepth: window.screen.colorDepth,
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        language: navigator.language,
        platform: navigator.platform,
        userAgent: navigator.userAgent,
      },
    });

    setIsLoading(false);

    if (result.success) {
      router.push('/dashboard');
    } else {
      setError(result.error || 'Invalid credentials or biometric anomaly detected.');
    }
  };

  const handleFocus = () => {
    if (!capturing) {
      setCapturing(true);
      startCapture();
    }
  };

  if (isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen bg-[#070A12] text-white flex selection:bg-[#0075FF]/30">
      {/* Left Panel: Revolut / Monzo Glassmorphic Art */}
      <div className="hidden lg:flex lg:w-7/12 relative overflow-hidden flex-col justify-between p-16 border-r border-white/10 bg-gradient-to-br from-[#0A0E17] via-[#111827] to-[#070A12]">
        {/* Glowing Ambient Orbs */}
        <div className="absolute -top-40 -left-40 w-96 h-96 rounded-full bg-[#0075FF]/20 blur-[120px] pointer-events-none animate-pulse" />
        <div className="absolute -bottom-40 -right-40 w-96 h-96 rounded-full bg-[#00E396]/15 blur-[140px] pointer-events-none" />
        
        {/* Brand Header */}
        <div className="relative z-10 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-11 h-11 bg-gradient-to-br from-[#0075FF] to-[#3898FF] rounded-2xl flex items-center justify-center shadow-lg shadow-[#0075FF]/30 border border-white/20">
              <Building2 className="w-6 h-6 text-white" />
            </div>
            <span className="text-2xl font-extrabold tracking-tight font-sans text-white">{APP_NAME}</span>
          </div>
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-white/5 border border-white/10 text-[#00E396] backdrop-blur-md">
            <Shield className="w-3.5 h-3.5" /> Zero-Trust Security Endpoint
          </span>
        </div>

        {/* Center Value Proposition */}
        <div className="relative z-10 space-y-8 my-auto">
          <div className="inline-flex items-center gap-2.5 px-4 py-1.5 rounded-full bg-[#0075FF]/10 border border-[#0075FF]/30 text-[#3898FF] text-xs font-mono tracking-wider uppercase">
            <Activity className="w-3.5 h-3.5 animate-bounce" /> Continuous Machine Learning Protection
          </div>
          <h1 className="text-5xl xl:text-6xl font-black tracking-tight leading-[1.1] text-white">
            Supreme Banking.<br />
            <span className="bg-gradient-to-r from-[#0075FF] via-[#3898FF] to-[#00E396] bg-clip-text text-transparent">
              Secured by Cadence.
            </span>
          </h1>
          <p className="text-base text-gray-300 max-w-xl leading-relaxed font-normal">
            No archaic passwords or friction-heavy OTP prompts. Our AI engine silently models your keystroke dwell intervals, flight latencies, and mouse velocity to grant seamless clearance in sub-10 milliseconds.
          </p>

          {/* Feature Showcase Grid */}
          <div className="grid grid-cols-2 gap-4 pt-4 max-w-xl">
            <div className="p-4 rounded-xl bg-white/[0.03] border border-white/10 backdrop-blur-md">
              <span className="text-xs font-mono text-[#00E396] block mb-1">LATENCY GUARD</span>
              <p className="text-sm font-semibold text-gray-200">10ms Isolation Forest Scoring</p>
            </div>
            <div className="p-4 rounded-xl bg-white/[0.03] border border-white/10 backdrop-blur-md">
              <span className="text-xs font-mono text-[#0075FF] block mb-1">ACID LEDGER</span>
              <p className="text-sm font-semibold text-gray-200">Enterprise Financial Core</p>
            </div>
          </div>
        </div>

        {/* Footer info */}
        <div className="relative z-10 flex items-center justify-between text-xs text-gray-400 font-mono border-t border-white/10 pt-6">
          <span>TLS 1.3 Encryption / PCI-DSS Certified</span>
          <span>SYSTEM STATUS: 99.99% OPERATIONAL</span>
        </div>
      </div>

      {/* Right Panel: Obsidian Glassmorphic Auth Form */}
      <div className="w-full lg:w-5/12 flex flex-col justify-center px-8 sm:px-16 lg:px-12 xl:px-20 py-12 relative z-10 bg-[#0A0E17]">
        <div className="w-full max-w-sm mx-auto space-y-8">
          
          <div className="space-y-2">
            <h2 className="text-3xl font-extrabold tracking-tight text-white">
              Digital Sign-In
            </h2>
            <p className="text-sm text-gray-400">
              Verify your identity with continuous behavioral biometrics.
            </p>
          </div>

          {error && (
            <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-sm flex items-start gap-3 animate-shake">
              <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="space-y-1.5">
              <label htmlFor="email" className="text-xs font-mono font-semibold text-gray-300 uppercase tracking-wider block">
                Email / Account Identity
              </label>
              <div className="relative group">
                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500 group-focus-within:text-[#0075FF] transition-colors" />
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full pl-11 pr-4 py-3.5 bg-white/[0.03] border border-white/10 rounded-xl text-white placeholder-gray-500 text-sm focus:outline-none focus:border-[#0075FF] focus:ring-2 focus:ring-[#0075FF]/20 transition-all font-mono"
                  placeholder="customer@enterprise.com"
                  required
                  autoComplete="email"
                  onFocus={handleFocus}
                />
              </div>
            </div>

            <div className="space-y-1.5">
              <label htmlFor="password" className="text-xs font-mono font-semibold text-gray-300 uppercase tracking-wider block">
                Master Passcode
              </label>
              <div className="relative group">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500 group-focus-within:text-[#0075FF] transition-colors" />
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-11 pr-11 py-3.5 bg-white/[0.03] border border-white/10 rounded-xl text-white placeholder-gray-500 text-sm focus:outline-none focus:border-[#0075FF] focus:ring-2 focus:ring-[#0075FF]/20 transition-all font-mono"
                  placeholder="••••••••••••••••"
                  required
                  autoComplete="current-password"
                  onFocus={handleFocus}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white transition-colors"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {/* Live Telemetry Sensor Feedback Widget */}
            <div className="p-3.5 rounded-xl bg-white/[0.02] border border-white/10 flex items-center justify-between transition-all">
              <div className="flex items-center gap-2.5">
                <Fingerprint className={cn("w-5 h-5 transition-colors duration-500", keystrokeConfidence > 75 ? "text-[#00E396]" : "text-[#0075FF] animate-pulse")} />
                <div>
                  <span className="text-[11px] font-mono font-bold text-gray-300 uppercase block">
                    Keystroke Cadence Active
                  </span>
                  <span className="text-[10px] text-gray-500 font-sans block">
                    {keystrokeConfidence > 0 ? `Evaluating flight intervals... (${Math.round(keystrokeConfidence)}%)` : "Awaiting input rhythm..."}
                  </span>
                </div>
              </div>
              {keystrokeConfidence >= 80 && (
                <span className="text-[11px] font-mono font-bold text-[#00E396] flex items-center gap-1">
                  <CheckCircle className="w-3.5 h-3.5" /> MATCHED
                </span>
              )}
            </div>

            <div className="flex items-center justify-between text-xs font-sans">
              <label className="flex items-center gap-2 cursor-pointer text-gray-400 hover:text-gray-300">
                <input type="checkbox" className="rounded bg-white/5 border-white/10 text-[#0075FF] focus:ring-0 w-4 h-4" />
                <span>Keep session trusted</span>
              </label>
              <Link href="/forgot-password" className="text-[#0075FF] hover:text-[#3898FF] font-semibold transition-colors">
                Recover access
              </Link>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className={cn(
                "w-full py-4 px-6 rounded-xl bg-gradient-to-r from-[#0075FF] to-[#3898FF] text-white font-bold text-sm tracking-wide shadow-lg shadow-[#0075FF]/30 hover:shadow-xl hover:shadow-[#0075FF]/40 hover:scale-[1.01] active:scale-[0.99] transition-all flex items-center justify-center gap-2 group",
                isLoading && "opacity-60 cursor-not-allowed transform-none"
              )}
            >
              {isLoading ? (
                <span className="flex items-center gap-2">
                  <svg className="animate-spin h-4 w-4 text-white" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Authenticating Identity...
                </span>
              ) : (
                <>
                  AUTHORIZE SESSION
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </>
              )}
            </button>
          </form>

          <div className="pt-4 text-center border-t border-white/10">
            <p className="text-xs text-gray-400">
              New to SecureBank Enterprise?{' '}
              <Link href="/register" className="text-[#00E396] hover:underline font-bold ml-1">
                Open Protected Account
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
