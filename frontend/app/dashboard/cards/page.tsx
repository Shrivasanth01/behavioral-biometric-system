'use client';

import { useState } from 'react';
import { CreditCard, Plus, Snowflake, Ban, RotateCcw, Lock } from 'lucide-react';
import { Card, CardHeader, CardBody } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Modal } from '@/components/ui/Modal';
import { Dialog } from '@/components/ui/Dialog';
import { Tabs } from '@/components/ui/Tabs';
import { CardView } from '@/components/cards/CardView';
import { CardLimits } from '@/components/cards/CardLimits';
import { CardActions } from '@/components/cards/CardActions';
import { generateMockCards } from '@/lib/utils';
import type { Card as CardType } from '@/types';

const mockCards = generateMockCards();

export default function CardsPage() {
  const [cards, setCards] = useState(mockCards);
  const [selectedCard, setSelectedCard] = useState<CardType | null>(null);
  const [showLimits, setShowLimits] = useState(false);
  const [showRequestModal, setShowRequestModal] = useState(false);
  const [showBlockDialog, setShowBlockDialog] = useState<CardType | null>(null);
  const [requestForm, setRequestForm] = useState({ accountId: '', cardType: 'debit', cardNetwork: 'visa' });

  const handleToggleFreeze = () => {
    if (!selectedCard) return;
    setCards(prev => prev.map(c => {
      if (c.id === selectedCard.id) {
        const newStatus = c.status === 'frozen' ? 'active' : 'frozen';
        return { ...c, status: newStatus as 'active' | 'frozen' };
      }
      return c;
    }));
    setSelectedCard(prev => prev ? {
      ...prev,
      status: prev.status === 'frozen' ? 'active' : 'frozen',
    } as CardType : null);
  };

  const handleSaveLimits = (limits: Partial<CardType>) => {
    if (!selectedCard) return;
    setCards(prev => prev.map(c => c.id === selectedCard.id ? { ...c, ...limits } : c));
    setSelectedCard(prev => prev ? { ...prev, ...limits } as CardType : null);
    setShowLimits(false);
  };

  const handleBlock = () => {
    if (!showBlockDialog) return;
    setCards(prev => prev.map(c => c.id === showBlockDialog.id ? { ...c, status: 'blocked' as const } : c));
    setShowBlockDialog(null);
    setSelectedCard(null);
  };

  const handleRequestCard = () => {
    const newCard: CardType = {
      id: `card_${Date.now()}`,
      userId: 'usr_1',
      accountId: requestForm.accountId,
      cardNumber: `4532${Math.random().toString().slice(2, 14)}`,
      cardHolderName: 'RAHUL SHARMA',
      cardType: requestForm.cardType as 'debit' | 'credit',
      cardNetwork: requestForm.cardNetwork as 'visa' | 'mastercard' | 'rupay',
      expiryDate: '12/28',
      cvv: '***',
      status: 'active',
      dailyLimit: 50000,
      monthlyLimit: 200000,
      domesticLimit: 100000,
      internationalLimit: 50000,
      isVirtual: true,
      issuedAt: new Date().toISOString(),
    };
    setCards(prev => [...prev, newCard]);
    setShowRequestModal(false);
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="page-title">Cards</h1>
          <p className="page-subtitle">Manage your debit and credit cards</p>
        </div>
        <Button onClick={() => setShowRequestModal(true)} leftIcon={<Plus className="w-4 h-4" />}>
          Request New Card
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {cards.map(card => (
          <CardView
            key={card.id}
            card={card}
            onClick={() => setSelectedCard(card)}
          />
        ))}
      </div>

      <Modal
        isOpen={!!selectedCard && !showLimits}
        onClose={() => setSelectedCard(null)}
        title="Card Details"
        size="md"
      >
        {selectedCard && (
          <div className="space-y-6">
            <CardView card={selectedCard} className="cursor-default hover:scale-100" />

            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-gray-500">Card Type</p>
                <p className="font-medium text-navy-900 capitalize">{selectedCard.cardType}</p>
              </div>
              <div>
                <p className="text-gray-500">Network</p>
                <p className="font-medium text-navy-900 uppercase">{selectedCard.cardNetwork}</p>
              </div>
              <div>
                <p className="text-gray-500">Daily Limit</p>
                <p className="font-medium text-navy-900">₹{selectedCard.dailyLimit.toLocaleString()}</p>
              </div>
              <div>
                <p className="text-gray-500">Monthly Limit</p>
                <p className="font-medium text-navy-900">₹{selectedCard.monthlyLimit.toLocaleString()}</p>
              </div>
            </div>

            <CardActions
              card={selectedCard}
              onToggleFreeze={handleToggleFreeze}
              onBlock={() => { setShowBlockDialog(selectedCard); }}
              onRequestNew={() => setShowRequestModal(true)}
              onSetLimits={() => setShowLimits(true)}
            />
          </div>
        )}
      </Modal>

      <Modal
        isOpen={showLimits}
        onClose={() => setShowLimits(false)}
        title="Card Limits"
        size="md"
      >
        {selectedCard && (
          <CardLimits card={selectedCard} onSave={handleSaveLimits} />
        )}
      </Modal>

      <Modal
        isOpen={showRequestModal}
        onClose={() => setShowRequestModal(false)}
        title="Request New Card"
        size="md"
      >
        <div className="space-y-4">
          <div>
            <label className="label">Card Type</label>
            <select
              value={requestForm.cardType}
              onChange={e => setRequestForm(p => ({ ...p, cardType: e.target.value }))}
              className="input-field"
            >
              <option value="debit">Debit Card</option>
              <option value="credit">Credit Card</option>
            </select>
          </div>
          <div>
            <label className="label">Card Network</label>
            <select
              value={requestForm.cardNetwork}
              onChange={e => setRequestForm(p => ({ ...p, cardNetwork: e.target.value }))}
              className="input-field"
            >
              <option value="visa">Visa</option>
              <option value="mastercard">Mastercard</option>
              <option value="rupay">RuPay</option>
            </select>
          </div>
          <Button className="w-full" onClick={handleRequestCard}>
            Request Card
          </Button>
        </div>
      </Modal>

      <Dialog
        isOpen={!!showBlockDialog}
        onClose={() => setShowBlockDialog(null)}
        onConfirm={handleBlock}
        title="Block Card"
        message={`Are you sure you want to permanently block this card? This action cannot be undone.`}
        variant="alert"
        confirmLabel="Block Card"
      />
    </div>
  );
}
