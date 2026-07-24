'use client';

import React, { useState } from 'react';
import { Card, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';

interface UserSearchCardProps {
  onSearch: (query: string) => void;
  isLoading?: boolean;
  className?: string;
}

export function UserSearchCard({ onSearch, isLoading, className }: UserSearchCardProps) {
  const [query, setQuery] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) onSearch(query.trim());
  };

  return (
    <Card className={className}>
      <CardTitle>Investigate User</CardTitle>
      <CardContent>
        <form onSubmit={handleSubmit} className="flex gap-3">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search by User ID, Email, or Phone..."
            className="cyber-input flex-1"
          />
          <Button type="submit" isLoading={isLoading}>
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            Search
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
