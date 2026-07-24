'use client';

import React from 'react';
import { Snowflake, Ban, RotateCcw, Lock, AlertTriangle } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card } from '@/types';

interface CardActionsProps {
  card: Card;
  onToggleFreeze: () => void;
  onBlock: () => void;
  onRequestNew: () => void;
  onSetLimits: () => void;
}

export function CardActions({ card, onToggleFreeze, onBlock, onRequestNew, onSetLimits }: CardActionsProps) {
  return (
    <div className="space-y-3">
      <Button
        variant={card.status === 'frozen' ? 'success' : 'secondary'}
        className="w-full justify-start"
        leftIcon={<Snowflake className="w-4 h-4" />}
        onClick={onToggleFreeze}
      >
        {card.status === 'frozen' ? 'Unfreeze Card' : 'Freeze Card'}
      </Button>
      <Button
        variant="secondary"
        className="w-full justify-start"
        leftIcon={<Lock className="w-4 h-4" />}
        onClick={onSetLimits}
      >
        Set Limits
      </Button>
      <Button
        variant="secondary"
        className="w-full justify-start"
        leftIcon={<RotateCcw className="w-4 h-4" />}
        onClick={onRequestNew}
      >
        Request Replacement
      </Button>
      <Button
        variant="ghost"
        className="w-full justify-start text-danger-600 hover:text-danger-700 hover:bg-danger-50"
        leftIcon={<AlertTriangle className="w-4 h-4" />}
        onClick={onBlock}
      >
        Report Lost / Block
      </Button>
    </div>
  );
}
