'use client';

import React, { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { apiService } from '@/services/api';
import { BookingHistory } from '@/types';
import BookingStatusCard from '@/components/BookingStatusCard';
import Timeline from '@/components/Timeline';
import LoadingSpinner from '@/components/LoadingSpinner';
import ErrorMessage from '@/components/ErrorMessage';
import { RefreshCw } from 'lucide-react';

export default function TrackBookingPage() {
  const params = useParams();
  const refId = params.ref_id as string;

  const [data, setData] = useState<BookingHistory | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchBookingHistory = async () => {
    setLoading(true);
    setError(null);

    try {
      const history = await apiService.getBookingHistory(refId);
      setData(history);
    } catch (err: any) {
      setError(err.message || 'Failed to load booking history');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (refId) {
      fetchBookingHistory();
    }
  }, [refId]);

  if (loading) {
    return (
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="flex flex-col items-center justify-center py-20">
          <LoadingSpinner size="lg" />
          <p className="mt-4 text-gray-600">Loading booking details...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <ErrorMessage message={error} onRetry={fetchBookingHistory} />
      </div>
    );
  }

  if (!data) {
    return (
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center py-20">
          <p className="text-gray-600">No data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Booking Tracking</h1>
        <button
          onClick={fetchBookingHistory}
          className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          Refresh
        </button>
      </div>

      {/* Booking Status Card */}
      <div className="mb-8">
        <BookingStatusCard booking={data.booking} />
      </div>

      {/* Timeline */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
        <h2 className="text-2xl font-semibold text-gray-900 mb-6">Shipment Timeline</h2>
        <Timeline events={data.timeline} />
      </div>
    </div>
  );
}