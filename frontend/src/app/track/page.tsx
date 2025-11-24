'use client';

import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import { apiService } from '@/services/api';
import { BookingHistory } from '@/types';
import BookingStatusCard from '@/components/BookingStatusCard';
import Timeline from '@/components/Timeline';
import LoadingSkeleton from '@/components/LoadingSkeleton';
import ErrorMessage from '@/components/ErrorMessage';

export default function TrackPage() {
  const searchParams = useSearchParams();
  const refId = searchParams.get('ref_id');
  
  const [bookingHistory, setBookingHistory] = useState<BookingHistory | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (refId) {
      loadBookingHistory(refId);
    }
  }, [refId]);

  const loadBookingHistory = async (ref: string) => {
    try {
      setLoading(true);
      setError('');
      const data = await apiService.getBookingHistory(ref);
      setBookingHistory(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load booking history');
    } finally {
      setLoading(false);
    }
  };

  if (!refId) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <ErrorMessage message="No booking reference ID provided" />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Track Booking</h1>

      {loading && (
        <div className="space-y-6">
          <LoadingSkeleton type="card" />
          <LoadingSkeleton type="timeline" />
        </div>
      )}

      {error && <ErrorMessage message={error} />}

      {!loading && !error && bookingHistory && (
        <div className="space-y-6">
          <BookingStatusCard booking={bookingHistory.booking} />
          <Timeline events={bookingHistory.timeline} />
        </div>
      )}
    </div>
  );
}
