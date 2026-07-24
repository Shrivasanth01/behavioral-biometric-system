'use client';

import React, { useState } from 'react';
import { Save } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import type { Card } from '@/types';

interface CardLimitsProps {
  card: Card;
  onSave: (limits: Partial<Card>) => void;
}

export function CardLimits({ card, onSave }: CardLimitsProps) {
  const [limits, setLimits] = useState({
    dailyLimit: card.dailyLimit,
    monthlyLimit: card.monthlyLimit,
    domesticLimit: card.domesticLimit,
    internationalLimit: card.internationalLimit,
  });

  return (
    <div className="space-y-4">
      <div>
        <label className="label">Daily Transaction Limit</label>
        <div className="relative">
          <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500">₹</span>
          <input
            type="number"
            value={limits.dailyLimit}
            onChange={e => setLimits(p => ({ ...p, dailyLimit: parseInt(e.target.value) || 0 }))}
            className="input-field pl-8"
          />
        </div>
      </div>
      <div>
        <label className="label">Monthly Transaction Limit</label>
        <div className="relative">
          <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500">₹</span>
          <input
            type="number"
            value={limits.monthlyLimit}
            onChange={e => setLimits(p => ({ ...p, monthlyLimit: parseInt(e.target.value) || 0 }))}
            className="input-field pl-8"
          />
        </div>
      </div>
      <div>
        <label className="label">Domestic Limit (per transaction)</label>
        <div className="relative">
          <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500">₹</span>
          <input
            type="number"
            value={limits.domesticLimit}
            onChange={e => setLimits(p => ({ ...p, domesticLimit: parseInt(e.target.value) || 0 }))}
            className="input-field pl-8"
          />
        </div>
      </div>
      <div>
        <label className="label">International Limit (per transaction)</label>
        <div className="relative">
          <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500">₹</span>
          <input
            type="number"
            value={limits.internationalLimit}
            onChange={e => setLimits(p => ({ ...p, internationalLimit: parseInt(e.target.value) || 0 }))}
            className="input-field pl-8"
          />
        </div>
      </div>
      <Button className="w-full" onClick={() => onSave(limits)} leftIcon={<Save className="w-4 h-4" />}>
        Save Limits
      </Button>
    </div>
  );
}
