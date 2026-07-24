import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Sentinel - Fraud Monitoring Platform',
  description: 'Behavioral biometric security operations dashboard',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-navy-950 text-gray-100">
        {children}
      </body>
    </html>
  );
}
