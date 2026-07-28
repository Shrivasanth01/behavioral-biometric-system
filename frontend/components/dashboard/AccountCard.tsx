'use client';

import React from 'react';
import { Building2, Wallet, CreditCard, Landmark, ArrowUpRight, ShieldCheck } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { formatCurrency, maskAccountNumber, cn } from '@/lib/utils';
import type { Account } from '@/types';

interface AccountCardProps {
  account: Account;
  onClick?: () => void;
  selected?: boolean;
}

const typeIcons = {
  savings: Wallet,
  current: Building2,
  credit: CreditCard,
  loan: Landmark,
};

// Revolut, Monzo, and Chase Wealth Inspired Gradients
const typeThemes = {
  savings: {
    gradient: 'from-[#0075FF] via-[#3898FF] to-[#1a2333]',
    accentColor: 'text-[#00E396]',
    borderGlow: 'hover:border-[#0075FF]/60',
    label: 'Yield Savings Vault'
  },
  current: {
    gradient: 'from-[#0A0E17] via-[#161D2E] to-[#243049]',
    accentColor: 'text-white',
    borderGlow: 'hover:border-[#00E396]/60',
    label: 'Primary Checking Account'
  },
  credit: {
    gradient: 'from-[#FF4D6D] via-[#a32240] to-[#121622]',
    accentColor: 'text-[#FF4D6D]',
    borderGlow: 'hover:border-[#FF4D6D]/60',
    label: 'Monzo Credit Tier'
  },
  loan: {
    gradient: 'from-[#D4AF37] via-[#8a7222] to-[#141824]',
    accentColor: 'text-[#D4AF37]',
    borderGlow: 'hover:border-[#D4AF37]/60',
    label: 'Wealth Installment Loan'
  },
};

export function AccountCard({ account, onClick, selected }: AccountCardProps) {
  const Icon = typeIcons[account.accountType] || Wallet;
  const theme = typeThemes[account.accountType] || typeThemes.current;

  return (
    <div
      onClick={onClick}
      className={cn(
        "group relative overflow-hidden rounded-2xl border border-white/10 bg-[#0A0E17]/90 p-6 shadow-2xl backdrop-blur-xl transition-all duration-300 hover:scale-[1.02] cursor-pointer",
        theme.borderGlow,
        selected ? "ring-2 ring-[#0075FF] border-[#0075FF] bg-white/[0.03]" : ""
      )}
    >
      {/* Holographic Subtle Corner Glow */}
      <div className={cn("absolute top-0 right-0 h-40 w-40 rounded-full bg-gradient-to-br opacity-25 blur-3xl transition-opacity duration-500 group-hover:opacity-60", theme.gradient)} />

      <div className="relative z-10 flex flex-col justify-between h-full space-y-6">
        {/* Card Top Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-white/5 border border-white/10 text-white shadow-inner group-hover:bg-white/10 transition-colors">
              <Icon className="w-5 h-5" />
            </div>
            <div>
              <span className="text-xs font-mono font-semibold text-gray-400 tracking-wider uppercase block">
                {theme.label}
              </span>
              <span className="text-sm font-bold text-gray-200 font-mono tracking-widest">
                {maskAccountNumber(account.accountNumber)}
              </span>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-semibold tracking-wide bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <ShieldCheck className="w-3 h-3" /> Protected
            </span>
            <div className="h-8 w-8 rounded-full bg-white/5 flex items-center justify-center text-gray-400 group-hover:text-white group-hover:bg-white/10 transition-all">
              <ArrowUpRight className="w-4 h-4" />
            </div>
          </div>
        </div>

        {/* Balance Display Section */}
        <div>
          <span className="text-xs font-mono font-medium text-gray-400 uppercase tracking-wider block mb-1">
            Available Liquid Assets
          </span>
          <p className="text-3xl font-extrabold tracking-tight text-white">
            {formatCurrency(account.availableBalance, account.currency)}
          </p>
        </div>

        {/* Card Footer Details */}
        <div className="pt-4 border-t border-white/10 flex items-center justify-between text-xs text-gray-400 font-sans">
          <div className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-emerald-400 animate-ping inline-block" />
            <span className="text-gray-300 font-medium">{account.accountName}</span>
          </div>
          <span className="font-mono bg-white/5 px-2 py-0.5 rounded text-[11px] text-gray-400 border border-white/5">
            ROUTING: {account.ifscCode || 'CHASUS3N'}
          </span>
        </div>
      </div>
    </div>
  );
}
