'use client';

import React, { useState } from 'react';
import { Search } from 'lucide-react';
import { useRouter } from 'next/navigation';

export default function SearchBox() {
  const [refId, setRefId] = useState('');
  const router = useRouter();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (refId.trim()) {
      router.push(`/track/${refId.trim().toUpperCase()}`);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <div className="relative">
        <input
          type="text"
          value={refId}
          onChange={(e) => setRefId(e.target.value)}
          placeholder="Enter booking reference (e.g., ACB12345)"
          className="w-full px-4 py-3 pl-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition-all"
        />
        <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
        <button
          type="submit"
          className="absolute right-2 top-1/2 -translate-y-1/2 px-4 py-1.5 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition-colors font-medium"
        >
          Track
        </button>
      </div>
    </form>
  );
}