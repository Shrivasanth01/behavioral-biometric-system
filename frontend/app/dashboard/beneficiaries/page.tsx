'use client';

import { useState } from 'react';
import { Users, Plus, Pencil, Trash2, Phone, Mail, Banknote, Star } from 'lucide-react';
import { Card, CardHeader, CardBody } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Modal } from '@/components/ui/Modal';
import { Badge } from '@/components/ui/Badge';
import { Dialog } from '@/components/ui/Dialog';
import { generateMockBeneficiaries } from '@/lib/utils';
import type { Beneficiary } from '@/types';

const mockBeneficiaries = generateMockBeneficiaries();

export default function BeneficiariesPage() {
  const [beneficiaries, setBeneficiaries] = useState(mockBeneficiaries);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState<Beneficiary | null>(null);
  const [showDeleteDialog, setShowDeleteDialog] = useState<Beneficiary | null>(null);
  const [formData, setFormData] = useState({
    name: '', accountNumber: '', ifscCode: '', bankName: '',
    accountType: 'savings' as 'savings' | 'current', nickname: '', phone: '', email: '',
    isUPI: false, upiId: '', maxTransferLimit: 50000,
  });

  const resetForm = () => {
    setFormData({
      name: '', accountNumber: '', ifscCode: '', bankName: '',
      accountType: 'savings', nickname: '', phone: '', email: '',
      isUPI: false, upiId: '', maxTransferLimit: 50000,
    });
  };

  const handleAdd = () => {
    const newBen: Beneficiary = {
      id: `ben_${Date.now()}`,
      userId: 'usr_1',
      ...formData,
      isFrequent: false,
      createdAt: new Date().toISOString(),
    };
    setBeneficiaries(prev => [newBen, ...prev]);
    setShowAddModal(false);
    resetForm();
  };

  const handleEdit = () => {
    if (!showEditModal) return;
    setBeneficiaries(prev => prev.map(b => b.id === showEditModal.id ? { ...b, ...formData } : b));
    setShowEditModal(null);
    resetForm();
  };

  const handleDelete = () => {
    if (!showDeleteDialog) return;
    setBeneficiaries(prev => prev.filter(b => b.id !== showDeleteDialog.id));
    setShowDeleteDialog(null);
  };

  const openEdit = (ben: Beneficiary) => {
    setFormData({
      name: ben.name, accountNumber: ben.accountNumber, ifscCode: ben.ifscCode,
      bankName: ben.bankName, accountType: ben.accountType, nickname: ben.nickname || '',
      phone: ben.phone || '', email: ben.email || '',
      isUPI: ben.isUPI, upiId: ben.upiId || '', maxTransferLimit: ben.maxTransferLimit,
    });
    setShowEditModal(ben);
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="page-title">Beneficiaries</h1>
          <p className="page-subtitle">Manage your trusted transfer recipients</p>
        </div>
        <Button onClick={() => { resetForm(); setShowAddModal(true); }} leftIcon={<Plus className="w-4 h-4" />}>
          Add Beneficiary
        </Button>
      </div>

      <Card>
        <CardBody>
          {beneficiaries.length === 0 ? (
            <div className="text-center py-12">
              <Users className="w-12 h-12 text-gray-300 mx-auto mb-3" />
              <p className="text-gray-500">No beneficiaries added yet</p>
              <Button className="mt-4" onClick={() => { resetForm(); setShowAddModal(true); }}>
                Add Your First Beneficiary
              </Button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {beneficiaries.map(ben => (
                <div key={ben.id} className="p-4 border border-gray-200 rounded-xl hover:border-gray-300 transition-colors">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center">
                        <span className="text-sm font-semibold text-primary-700">
                          {ben.name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)}
                        </span>
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <h3 className="text-sm font-semibold text-navy-900">{ben.name}</h3>
                          {ben.isFrequent && <Star className="w-3 h-3 text-warning-500 fill-warning-500" />}
                          {ben.isUPI && <Badge variant="info" size="sm">UPI</Badge>}
                        </div>
                        <p className="text-xs text-gray-500 font-mono mt-0.5">{ben.accountNumber}</p>
                      </div>
                    </div>
                    <div className="flex gap-1">
                      <button onClick={() => openEdit(ben)} className="p-1.5 text-gray-400 hover:text-primary-600 hover:bg-gray-100 rounded-lg">
                        <Pencil className="w-4 h-4" />
                      </button>
                      <button onClick={() => setShowDeleteDialog(ben)} className="p-1.5 text-gray-400 hover:text-danger-600 hover:bg-gray-100 rounded-lg">
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                  <div className="mt-3 grid grid-cols-2 gap-2 text-xs text-gray-500">
                    <span className="flex items-center gap-1"><Banknote className="w-3 h-3" /> {ben.bankName}</span>
                    <span className="flex items-center gap-1"><Banknote className="w-3 h-3" /> {ben.ifscCode}</span>
                    {ben.phone && <span className="flex items-center gap-1"><Phone className="w-3 h-3" /> {ben.phone}</span>}
                    {ben.email && <span className="flex items-center gap-1"><Mail className="w-3 h-3" /> {ben.email}</span>}
                  </div>
                  <div className="mt-3 pt-3 border-t border-gray-100 flex items-center justify-between">
                    <span className="text-xs text-gray-400">Max transfer limit</span>
                    <span className="text-sm font-semibold text-navy-900">₹{ben.maxTransferLimit.toLocaleString()}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardBody>
      </Card>

      <Modal
        isOpen={showAddModal}
        onClose={() => setShowAddModal(false)}
        title="Add Beneficiary"
        size="lg"
      >
        <BeneficiaryForm formData={formData} onChange={setFormData} />
        <div className="flex gap-3 mt-6">
          <Button variant="secondary" className="flex-1" onClick={() => setShowAddModal(false)}>Cancel</Button>
          <Button className="flex-1" onClick={handleAdd}>Add Beneficiary</Button>
        </div>
      </Modal>

      <Modal
        isOpen={!!showEditModal}
        onClose={() => setShowEditModal(null)}
        title="Edit Beneficiary"
        size="lg"
      >
        <BeneficiaryForm formData={formData} onChange={setFormData} />
        <div className="flex gap-3 mt-6">
          <Button variant="secondary" className="flex-1" onClick={() => setShowEditModal(null)}>Cancel</Button>
          <Button className="flex-1" onClick={handleEdit}>Save Changes</Button>
        </div>
      </Modal>

      <Dialog
        isOpen={!!showDeleteDialog}
        onClose={() => setShowDeleteDialog(null)}
        onConfirm={handleDelete}
        title="Remove Beneficiary"
        message={`Are you sure you want to remove ${showDeleteDialog?.name} from your beneficiaries?`}
        variant="alert"
        confirmLabel="Remove"
      />
    </div>
  );
}

function BeneficiaryForm({
  formData,
  onChange,
}: {
  formData: {
    name: string; accountNumber: string; ifscCode: string; bankName: string;
    accountType: 'savings' | 'current'; nickname: string; phone: string; email: string;
    isUPI: boolean; upiId: string; maxTransferLimit: number;
  };
  onChange: (data: typeof formData) => void;
}) {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div className="col-span-2">
          <label className="label">Beneficiary Name</label>
          <input type="text" value={formData.name} onChange={e => onChange({ ...formData, name: e.target.value })}
            className="input-field" placeholder="Full name" />
        </div>
        <div className="col-span-2">
          <label className="label">Account Number</label>
          <input type="text" value={formData.accountNumber} onChange={e => onChange({ ...formData, accountNumber: e.target.value })}
            className="input-field font-mono" placeholder="Account number" />
        </div>
        <div>
          <label className="label">IFSC Code</label>
          <input type="text" value={formData.ifscCode} onChange={e => onChange({ ...formData, ifscCode: e.target.value.toUpperCase() })}
            className="input-field font-mono uppercase" placeholder="SBIN0001234" />
        </div>
        <div>
          <label className="label">Bank Name</label>
          <input type="text" value={formData.bankName} onChange={e => onChange({ ...formData, bankName: e.target.value })}
            className="input-field" placeholder="Bank name" />
        </div>
        <div>
          <label className="label">Account Type</label>
          <select value={formData.accountType} onChange={e => onChange({ ...formData, accountType: e.target.value as 'savings' | 'current' })}
            className="input-field">
            <option value="savings">Savings</option>
            <option value="current">Current</option>
          </select>
        </div>
        <div>
          <label className="label">Nickname (Optional)</label>
          <input type="text" value={formData.nickname} onChange={e => onChange({ ...formData, nickname: e.target.value })}
            className="input-field" placeholder="e.g. Mom" />
        </div>
        <div>
          <label className="label">Phone (Optional)</label>
          <input type="tel" value={formData.phone} onChange={e => onChange({ ...formData, phone: e.target.value })}
            className="input-field" placeholder="Phone number" />
        </div>
        <div>
          <label className="label">Email (Optional)</label>
          <input type="email" value={formData.email} onChange={e => onChange({ ...formData, email: e.target.value })}
            className="input-field" placeholder="Email address" />
        </div>
        <div className="col-span-2">
          <label className="flex items-center gap-2 cursor-pointer">
            <input type="checkbox" checked={formData.isUPI}
              onChange={e => onChange({ ...formData, isUPI: e.target.checked })}
              className="w-4 h-4 rounded border-gray-300 text-primary-600" />
            <span className="text-sm text-navy-700">Enable UPI</span>
          </label>
        </div>
        {formData.isUPI && (
          <div className="col-span-2">
            <label className="label">UPI ID</label>
            <input type="text" value={formData.upiId} onChange={e => onChange({ ...formData, upiId: e.target.value })}
              className="input-field font-mono" placeholder="username@upi" />
          </div>
        )}
        <div className="col-span-2">
          <label className="label">Max Transfer Limit (₹)</label>
          <input type="number" value={formData.maxTransferLimit}
            onChange={e => onChange({ ...formData, maxTransferLimit: parseInt(e.target.value) || 0 })}
            className="input-field" min="1" />
        </div>
      </div>
    </div>
  );
}
