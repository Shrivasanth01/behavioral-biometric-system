'use client';

import { useState } from 'react';
import { ArrowRightLeft, Building2, Globe, Smartphone, Shield, CheckCircle } from 'lucide-react';
import { Card, CardHeader, CardBody } from '@/components/ui/Card';
import { Tabs } from '@/components/ui/Tabs';
import { Modal } from '@/components/ui/Modal';
import { Button } from '@/components/ui/Button';
import { InternalTransfer } from '@/components/transfer/InternalTransfer';
import { ExternalTransfer } from '@/components/transfer/ExternalTransfer';
import { UpiTransfer } from '@/components/transfer/UpiTransfer';

const transferTabs = [
  { id: 'internal', label: 'Internal Transfer', icon: <Building2 className="w-4 h-4" /> },
  { id: 'external', label: 'External Transfer', icon: <Globe className="w-4 h-4" /> },
  { id: 'upi', label: 'UPI Transfer', icon: <Smartphone className="w-4 h-4" /> },
];

export default function TransferPage() {
  const [activeTab, setActiveTab] = useState('internal');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showOTP, setShowOTP] = useState(false);
  const [showConfirmation, setShowConfirmation] = useState(false);
  const [transferDetails, setTransferDetails] = useState<Record<string, unknown>>({});

  const handleTransfer = async (data: Record<string, unknown>) => {
    setTransferDetails(data);
    setIsSubmitting(true);
    await new Promise(resolve => setTimeout(resolve, 1000));
    setIsSubmitting(false);
    setShowOTP(true);
  };

  const handleOTPConfirm = async () => {
    setIsSubmitting(true);
    await new Promise(resolve => setTimeout(resolve, 1500));
    setIsSubmitting(false);
    setShowOTP(false);
    setShowConfirmation(true);
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="page-title">Transfer Money</h1>
        <p className="page-subtitle">Send money securely with real-time risk assessment</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <Tabs tabs={transferTabs} activeTab={activeTab} onChange={setActiveTab} variant="pills" />
            </CardHeader>
            <CardBody>
              {activeTab === 'internal' && (
                <InternalTransfer onTransfer={handleTransfer} isSubmitting={isSubmitting} />
              )}
              {activeTab === 'external' && (
                <ExternalTransfer onTransfer={handleTransfer} isSubmitting={isSubmitting} />
              )}
              {activeTab === 'upi' && (
                <UpiTransfer onTransfer={handleTransfer} isSubmitting={isSubmitting} />
              )}
            </CardBody>
          </Card>
        </div>

        <div className="space-y-4">
          <Card>
            <CardHeader>
              <h3 className="text-sm font-semibold text-navy-900">Transfer Info</h3>
            </CardHeader>
            <CardBody className="space-y-3 text-sm">
              <div className="flex items-start gap-3 p-3 bg-blue-50 rounded-lg">
                <Shield className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
                <div>
                  <p className="font-medium text-blue-800">Risk Assessment Active</p>
                  <p className="text-xs text-blue-600 mt-0.5">Behavioral analysis is running during this transfer</p>
                </div>
              </div>
              <div className="space-y-2">
                <h4 className="font-medium text-navy-700">Limits</h4>
                <div className="flex justify-between text-gray-500">
                  <span>Internal Transfer</span>
                  <span className="font-medium text-navy-900">No Limit</span>
                </div>
                <div className="flex justify-between text-gray-500">
                  <span>External Transfer</span>
                  <span className="font-medium text-navy-900">₹1,00,000/day</span>
                </div>
                <div className="flex justify-between text-gray-500">
                  <span>UPI Transfer</span>
                  <span className="font-medium text-navy-900">₹25,000/day</span>
                </div>
              </div>
              <div className="pt-3 border-t border-gray-100">
                <h4 className="font-medium text-navy-700 mb-2">Transfer Timings</h4>
                <p className="text-gray-500">IMPS: 24x7</p>
                <p className="text-gray-500">NEFT: 24x7</p>
                <p className="text-gray-500">RTGS: 24x7</p>
              </div>
            </CardBody>
          </Card>
        </div>
      </div>

      <Modal
        isOpen={showOTP}
        onClose={() => setShowOTP(false)}
        title="Verify Transfer"
        description="Enter the OTP sent to your registered mobile number"
        size="sm"
      >
        <div className="space-y-4">
          <div className="flex gap-2 justify-center">
            {Array.from({ length: 6 }).map((_, i) => (
              <input
                key={i}
                type="text"
                maxLength={1}
                className="w-10 h-12 text-center text-lg font-semibold border-2 border-gray-300 rounded-lg focus:border-primary-500 focus:outline-none"
              />
            ))}
          </div>
          <div className="flex gap-2">
            <Button variant="secondary" className="flex-1" onClick={() => setShowOTP(false)}>
              Cancel
            </Button>
            <Button className="flex-1" onClick={handleOTPConfirm} isLoading={isSubmitting}>
              Verify & Send
            </Button>
          </div>
        </div>
      </Modal>

      <Modal
        isOpen={showConfirmation}
        onClose={() => setShowConfirmation(false)}
        title="Transfer Successful"
        size="sm"
      >
        <div className="text-center space-y-4">
          <div className="w-16 h-16 bg-success-50 rounded-full flex items-center justify-center mx-auto">
            <CheckCircle className="w-8 h-8 text-success-600" />
          </div>
          <p className="text-lg font-semibold text-navy-900">₹{String(transferDetails.amount || 0)} sent successfully</p>
          <p className="text-sm text-gray-500">Transaction reference: TXN{Date.now().toString(36).toUpperCase()}</p>
          <Button className="w-full" onClick={() => { setShowConfirmation(false); }}>
            Done
          </Button>
        </div>
      </Modal>
    </div>
  );
}


