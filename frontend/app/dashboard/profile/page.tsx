'use client';

import { useState } from 'react';
import {
  User, Shield, Smartphone, Bell, Key, Fingerprint, LogOut,
  Eye, EyeOff, Save, CheckCircle, XCircle, Monitor, Globe,
} from 'lucide-react';
import { Card, CardHeader, CardBody } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Switch } from '@/components/ui/Switch';
import { Badge } from '@/components/ui/Badge';
import { Tabs } from '@/components/ui/Tabs';
import { Avatar } from '@/components/ui/Avatar';
import { Progress } from '@/components/ui/Progress';
import { PasswordStrength } from '@/components/auth/PasswordStrength';
import { generateMockUser, formatDateTime, timeAgo, getInitials } from '@/lib/utils';
import type { User as UserType, NotificationPreferences } from '@/types';

const mockUser = generateMockUser();

export default function ProfilePage() {
  const [activeTab, setActiveTab] = useState('personal');
  const [profile, setProfile] = useState({
    name: mockUser.name,
    email: mockUser.email,
    phone: mockUser.phone,
  });
  const [passwordForm, setPasswordForm] = useState({ current: '', newPassword: '', confirm: '' });
  const [showPassword, setShowPassword] = useState({ current: false, new: false, confirm: false });
  const [notifications, setNotifications] = useState(mockUser.notificationPreferences);
  const [saved, setSaved] = useState(false);
  const [mfaEnabled, setMfaEnabled] = useState(mockUser.mfaEnabled);

  const tabs = [
    { id: 'personal', label: 'Personal Details', icon: <User className="w-4 h-4" /> },
    { id: 'security', label: 'Security', icon: <Shield className="w-4 h-4" /> },
    { id: 'devices', label: 'Devices', icon: <Smartphone className="w-4 h-4" /> },
    { id: 'notifications', label: 'Notifications', icon: <Bell className="w-4 h-4" /> },
  ];

  const handleSaveProfile = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  const handleChangePassword = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
    setPasswordForm({ current: '', newPassword: '', confirm: '' });
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="page-title">Profile & Settings</h1>
        <p className="page-subtitle">Manage your account, security, and preferences</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-1">
          <Card>
            <CardBody className="text-center">
              <Avatar name={mockUser.name} size="xl" className="mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-navy-900">{mockUser.name}</h3>
              <p className="text-sm text-gray-500">{mockUser.email}</p>
              <div className="mt-3">
                <Badge variant={mockUser.behavioralProfileStatus === 'complete' ? 'success' : 'warning'}>
                  {mockUser.behavioralProfileStatus === 'complete' ? 'Profile Complete' : 'Pending'}
                </Badge>
              </div>
              <div className="mt-4 space-y-2 text-left text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-500">Member since</span>
                  <span className="font-medium text-navy-900">{new Date(mockUser.createdAt).getFullYear()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">MFA</span>
                  <span className={mfaEnabled ? 'text-success-600' : 'text-gray-400'}>
                    {mfaEnabled ? 'Enabled' : 'Disabled'}
                  </span>
                </div>
              </div>
            </CardBody>
          </Card>
        </div>

        <div className="lg:col-span-3">
          <Card>
            <CardHeader>
              <Tabs tabs={tabs} activeTab={activeTab} onChange={setActiveTab} variant="pills" />
            </CardHeader>
            <CardBody>
              {saved && (
                <div className="mb-4 p-3 bg-success-50 border border-success-200 rounded-lg text-sm text-success-700 flex items-center gap-2">
                  <CheckCircle className="w-4 h-4" />
                  Changes saved successfully
                </div>
              )}

              {activeTab === 'personal' && (
                <div className="space-y-5 max-w-md">
                  <div>
                    <label className="label">Full Name</label>
                    <input type="text" value={profile.name}
                      onChange={e => setProfile(p => ({ ...p, name: e.target.value }))}
                      className="input-field" />
                  </div>
                  <div>
                    <label className="label">Email Address</label>
                    <input type="email" value={profile.email}
                      onChange={e => setProfile(p => ({ ...p, email: e.target.value }))}
                      className="input-field" />
                  </div>
                  <div>
                    <label className="label">Phone Number</label>
                    <input type="tel" value={profile.phone}
                      onChange={e => setProfile(p => ({ ...p, phone: e.target.value }))}
                      className="input-field" />
                  </div>
                  <Button onClick={handleSaveProfile} leftIcon={<Save className="w-4 h-4" />}>
                    Save Changes
                  </Button>
                </div>
              )}

              {activeTab === 'security' && (
                <div className="space-y-8 max-w-md">
                  <div>
                    <h3 className="text-sm font-semibold text-navy-900 mb-4">Change Password</h3>
                    <div className="space-y-4">
                      <div>
                        <label className="label">Current Password</label>
                        <div className="relative">
                          <input type={showPassword.current ? 'text' : 'password'}
                            value={passwordForm.current}
                            onChange={e => setPasswordForm(p => ({ ...p, current: e.target.value }))}
                            className="input-field pr-10" placeholder="Enter current password" />
                          <button onClick={() => setShowPassword(p => ({ ...p, current: !p.current }))}
                            className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400">
                            {showPassword.current ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                          </button>
                        </div>
                      </div>
                      <div>
                        <label className="label">New Password</label>
                        <div className="relative">
                          <input type={showPassword.new ? 'text' : 'password'}
                            value={passwordForm.newPassword}
                            onChange={e => setPasswordForm(p => ({ ...p, newPassword: e.target.value }))}
                            className="input-field pr-10" placeholder="Enter new password" />
                          <button onClick={() => setShowPassword(p => ({ ...p, new: !p.new }))}
                            className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400">
                            {showPassword.new ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                          </button>
                        </div>
                        <PasswordStrength password={passwordForm.newPassword} />
                      </div>
                      <div>
                        <label className="label">Confirm New Password</label>
                        <div className="relative">
                          <input type={showPassword.confirm ? 'text' : 'password'}
                            value={passwordForm.confirm}
                            onChange={e => setPasswordForm(p => ({ ...p, confirm: e.target.value }))}
                            className="input-field pr-10" placeholder="Confirm new password" />
                        </div>
                      </div>
                      <Button onClick={handleChangePassword} leftIcon={<Key className="w-4 h-4" />}>
                        Update Password
                      </Button>
                    </div>
                  </div>

                  <div className="pt-6 border-t border-gray-200">
                    <h3 className="text-sm font-semibold text-navy-900 mb-4">Multi-Factor Authentication</h3>
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm font-medium text-navy-900">Authenticator App</p>
                          <p className="text-xs text-gray-500">Use Google Authenticator or similar</p>
                        </div>
                        <Switch
                          checked={mfaEnabled}
                          onChange={setMfaEnabled}
                          label={mfaEnabled ? 'Enabled' : 'Disabled'}
                        />
                      </div>
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm font-medium text-navy-900">SMS Authentication</p>
                          <p className="text-xs text-gray-500">Receive codes via SMS</p>
                        </div>
                        <Switch
                          checked={false}
                          onChange={() => {}}
                        />
                      </div>
                    </div>
                  </div>

                  <div className="pt-6 border-t border-gray-200">
                    <h3 className="text-sm font-semibold text-navy-900 mb-4">Behavioral Profile</h3>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <Fingerprint className="w-4 h-4 text-primary-600" />
                          <span className="text-sm text-navy-700">Profile Status</span>
                        </div>
                        <Badge variant="success">Complete</Badge>
                      </div>
                      <div>
                        <div className="flex justify-between text-sm mb-1">
                          <span className="text-gray-500">Confidence Score</span>
                          <span className="font-medium text-navy-900">85%</span>
                        </div>
                        <Progress value={85} variant="success" />
                      </div>
                      <p className="text-xs text-gray-500">
                        Your behavioral profile captures how you type, move your mouse, and interact with the device.
                        This helps us detect unusual activity and prevent fraud.
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'devices' && (
                <div className="space-y-4">
                  <p className="text-sm text-gray-500">Devices that have accessed your account</p>
                  {mockUser.trustedDevices.map(device => (
                    <div key={device.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-xl">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center">
                          <Monitor className="w-5 h-5 text-gray-600" />
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <p className="text-sm font-medium text-navy-900">{device.name}</p>
                            {device.isCurrent && <Badge variant="info" size="sm">Current</Badge>}
                          </div>
                          <p className="text-xs text-gray-500">{device.browser} on {device.os}</p>
                          <p className="text-xs text-gray-400">Last active: {timeAgo(device.lastUsed)}</p>
                        </div>
                      </div>
                      {!device.isCurrent && (
                        <button className="text-sm text-danger-600 hover:text-danger-700 font-medium">
                          Remove
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              )}

              {activeTab === 'notifications' && (
                <div className="space-y-6 max-w-md">
                  <div className="space-y-4">
                    <h3 className="text-sm font-semibold text-navy-900">Alert Preferences</h3>
                    <div className="space-y-4">
                      <Switch
                        label="Transaction Alerts"
                        description="Get notified for all transactions above ₹1,000"
                        checked={notifications.transactionAlerts}
                        onChange={v => setNotifications(p => ({ ...p, transactionAlerts: v }))}
                      />
                      <Switch
                        label="Login Alerts"
                        description="Get notified when a new device accesses your account"
                        checked={notifications.loginAlerts}
                        onChange={v => setNotifications(p => ({ ...p, loginAlerts: v }))}
                      />
                      <Switch
                        label="Security Alerts"
                        description="Important security notifications about your account"
                        checked={notifications.securityAlerts}
                        onChange={v => setNotifications(p => ({ ...p, securityAlerts: v }))}
                      />
                    </div>
                  </div>

                  <div className="pt-6 border-t border-gray-200 space-y-4">
                    <h3 className="text-sm font-semibold text-navy-900">Notification Channels</h3>
                    <Switch
                      label="Email Notifications"
                      description="Receive notifications via email"
                      checked={notifications.email}
                      onChange={v => setNotifications(p => ({ ...p, email: v }))}
                    />
                    <Switch
                      label="SMS Notifications"
                      description="Receive notifications via SMS"
                      checked={notifications.sms}
                      onChange={v => setNotifications(p => ({ ...p, sms: v }))}
                    />
                    <Switch
                      label="Push Notifications"
                      description="Receive push notifications on your device"
                      checked={notifications.push}
                      onChange={v => setNotifications(p => ({ ...p, push: v }))}
                    />
                  </div>

                  <div className="pt-6 border-t border-gray-200 space-y-4">
                    <h3 className="text-sm font-semibold text-navy-900">Marketing</h3>
                    <Switch
                      label="Marketing Emails"
                      description="Receive offers, promotions, and product updates"
                      checked={notifications.marketingEmails}
                      onChange={v => setNotifications(p => ({ ...p, marketingEmails: v }))}
                    />
                  </div>

                  <Button onClick={handleSaveProfile} leftIcon={<Save className="w-4 h-4" />}>
                    Save Preferences
                  </Button>
                </div>
              )}
            </CardBody>
          </Card>
        </div>
      </div>
    </div>
  );
}
