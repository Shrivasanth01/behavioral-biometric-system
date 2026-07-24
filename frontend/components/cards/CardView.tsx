'use client';

import React from 'react';
import { CreditCard, Snowflake, Ban, CheckCircle2 } from 'lucide-react';
import { Badge } from '@/components/ui/Badge';
import { formatCardNumber, cn } from '@/lib/utils';
import type { Card } from '@/types';

interface CardViewProps {
  card: Card;
  onClick?: () => void;
  className?: string;
}

const networkColors: Record<string, string> = {
  visa: 'from-blue-700 to-blue-900',
  mastercard: 'from-orange-600 to-red-700',
  rupay: 'from-emerald-600 to-emerald-800',
};

export function CardView({ card, onClick, className }: CardViewProps) {
  return (
    <div
      onClick={onClick}
      className={cn(
        'relative overflow-hidden rounded-xl p-6 text-white cursor-pointer transition-all duration-300 hover:scale-[1.02] hover:shadow-xl group',
        networkColors[card.cardNetwork] || 'from-navy-700 to-navy-900',
        'bg-gradient-to-br',
        className
      )}
    >
      <div className="absolute top-0 right-0 w-32 h-32 bg-white/5 rounded-full -translate-y-1/2 translate-x-1/2" />
      <div className="absolute bottom-0 left-0 w-24 h-24 bg-white/5 rounded-full translate-y-1/2 -translate-x-1/2" />
      <div className="relative">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-2">
            <CreditCard className="w-6 h-6 opacity-80" />
            <span className="text-xs font-medium opacity-80 uppercase">{card.cardNetwork}</span>
          </div>
          <Badge variant={card.status === 'active' ? 'success' : card.status === 'frozen' ? 'warning' : 'danger'} size="sm">
            {card.status === 'frozen' ? 'Frozen' : card.status}
          </Badge>
        </div>

        <p className="text-xl font-mono tracking-wider mb-4">{formatCardNumber(card.cardNumber)}</p>

        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs opacity-70 mb-0.5">Card Holder</p>
            <p className="text-sm font-medium">{card.cardHolderName}</p>
          </div>
          <div className="text-right">
            <p className="text-xs opacity-70 mb-0.5">Expires</p>
            <p className="text-sm font-medium">{card.expiryDate}</p>
          </div>
        </div>

        {card.isVirtual && (
          <div className="mt-3 flex items-center gap-1 text-xs text-emerald-300">
            <CheckCircle2 className="w-3 h-3" />
            Virtual Card
          </div>
        )}
      </div>
    </div>
  );
}
