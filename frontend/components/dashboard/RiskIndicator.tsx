'use client';

import React from 'react';
import { Shield, ShieldCheck, ShieldAlert, ShieldX, Activity, Lock, CheckCircle2 } from 'lucide-react';
import { Progress } from '@/components/ui/Progress';
import { cn, getRiskLevel } from '@/lib/utils';

interface RiskIndicatorProps {
  score: number;
  size?: 'sm' | 'md' | 'lg';
  showDetails?: boolean;
  modelType?: string;
}

export function RiskIndicator({ 
  score, 
  size = 'md', 
  showDetails = true,
  modelType = "IsolationForest v2.4"
}: RiskIndicatorProps) {
  const risk = getRiskLevel(score);

  const isTrusted = score >= 80;
  const isWarning = score >= 50 && score < 80;
  
  // Revolut & Secure Emerald Inspired Color Token Mappings
  const themeStyles = {
    trusted: {
      gradient: "from-[#00E396]/20 via-[#0075FF]/10 to-transparent",
      borderColor: "border-[#00E396]/30",
      textColor: "text-[#00E396]",
      badgeBg: "bg-[#00E396]/15 text-[#00E396]",
      icon: ShieldCheck,
      label: "TRUSTED BIOMETRIC SHIELD"
    },
    warning: {
      gradient: "from-[#F3E5AB]/20 via-[#FF4D6D]/10 to-transparent",
      borderColor: "border-[#D4AF37]/40",
      textColor: "text-[#D4AF37]",
      badgeBg: "bg-[#D4AF37]/15 text-[#D4AF37]",
      icon: ShieldAlert,
      label: "ELEVATED BIOMETRIC MONITORING"
    },
    danger: {
      gradient: "from-[#FF4D6D]/30 via-red-900/20 to-transparent",
      borderColor: "border-[#FF4D6D]/50",
      textColor: "text-[#FF4D6D]",
      badgeBg: "bg-[#FF4D6D]/15 text-[#FF4D6D]",
      icon: ShieldX,
      label: "ACTIVE THREAT DETECTED"
    }
  };

  const currentTheme = isTrusted ? themeStyles.trusted : isWarning ? themeStyles.warning : themeStyles.danger;
  const Icon = currentTheme.icon;

  return (
    <div className={cn(
      "relative overflow-hidden rounded-xl border backdrop-blur-xl bg-[#0A0E17]/80 p-5 transition-all duration-300 shadow-2xl group",
      currentTheme.borderColor,
      size === 'lg' ? "p-6" : size === 'sm' ? "p-3" : "p-5"
    )}>
      {/* Background Holographic Glow */}
      <div className={cn("absolute inset-0 bg-gradient-to-r opacity-60 pointer-events-none transition-opacity duration-500 group-hover:opacity-100", currentTheme.gradient)} />
      
      <div className="relative z-10 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className={cn("p-2 rounded-lg backdrop-blur-md border border-white/10 shadow-inner flex items-center justify-center", currentTheme.badgeBg)}>
              <Icon className="w-5 h-5 animate-pulse" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className={cn("text-xs font-mono font-bold tracking-wider uppercase", currentTheme.textColor)}>
                  {currentTheme.label}
                </span>
                <span className="inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-semibold bg-white/5 text-gray-300 border border-white/10">
                  {modelType}
                </span>
              </div>
              <h4 className="text-sm font-semibold text-white tracking-wide mt-0.5">
                Continuous Authentication Posture
              </h4>
            </div>
          </div>
          
          <div className="text-right">
            <span className={cn("font-extrabold tracking-tight block", currentTheme.textColor, size === 'lg' ? 'text-3xl' : 'text-2xl')}>
              {Math.round(score)}%
            </span>
            <span className="text-[10px] text-gray-400 font-mono tracking-tighter uppercase">
              Confidence Score
            </span>
          </div>
        </div>

        {/* Customized Biometric Stream Progress */}
        <div className="space-y-1.5">
          <div className="h-2 w-full bg-black/40 rounded-full overflow-hidden p-0.5 border border-white/10 shadow-inner">
            <div 
              className={cn(
                "h-full rounded-full transition-all duration-500 bg-gradient-to-r shadow-lg",
                isTrusted ? "from-[#0075FF] to-[#00E396]" : isWarning ? "from-yellow-500 to-[#D4AF37]" : "from-orange-600 to-[#FF4D6D]"
              )}
              style={{ width: `${Math.min(100, Math.max(5, score))}%` }}
            />
          </div>
          
          <div className="flex items-center justify-between text-[11px] text-gray-400 font-mono">
            <span className="flex items-center gap-1">
              <Activity className="w-3 h-3 text-[#0075FF]" /> Keystroke & Mouse Dynamics: ACTIVE
            </span>
            <span>Zero-Trust Verification</span>
          </div>
        </div>

        {showDetails && (
          <div className="pt-2 border-t border-white/10 flex items-start gap-2.5">
            <div className="mt-0.5 text-gray-400">
              {isTrusted ? <CheckCircle2 className="w-4 h-4 text-[#00E396]" /> : <Lock className="w-4 h-4 text-[#FF4D6D]" />}
            </div>
            <p className="text-xs text-gray-300 leading-relaxed font-sans">
              {score >= 80
                ? "Your real-time keystroke flight times and cursor trajectories perfectly align with your trained behavioral profile. Zero-friction clearance active."
                : score >= 60
                  ? "Minor behavioral variance recorded (e.g., posture shift or alternate input cadence). Silent secondary validation running."
                  : score >= 30
                    ? "Unusual behavioral interaction patterns observed. High-value wire transfers will trigger adaptive multi-factor authentication (MFA)."
                    : "Severe anomaly detected (potential remote access trojan or credential spoofing). Instant account protection active."}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
