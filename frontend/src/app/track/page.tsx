'use client';

import React, { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { apiService } from '@/services/api';
import { BookingHistory } from '@/types';
import BookingStatusCard from '@/components/BookingStatusCard';
import Timeline from '@/components/Timeline';
import LoadingSkeleton from '@/components/LoadingSkeleton';
import ErrorMessage from '@/components/ErrorMessage';

function TrackContent() {
  const searchParams = useSearchParams();
  const refId = searchParams.get('ref_id');
  
  const [bookingHistory, setBookingHistory] = useState<BookingHistory | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [updating, setUpdating] = useState(false);

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

  const handleDepart = async () => {
    if (!refId) return;
    try {
      setUpdating(true);
      setError('');
      await apiService.departBooking(refId, { location: bookingHistory?.booking.origin || 'DEL' });
      await loadBookingHistory(refId);
      alert('Booking marked as departed!');
    } catch (err: any) {
      setError(err.message || 'Failed to update status');
    } finally {
      setUpdating(false);
    }
  };

  const handleArrive = async () => {
    if (!refId) return;
    try {
      setUpdating(true);
      setError('');
      await apiService.arriveBooking(refId, { location: bookingHistory?.booking.destination || 'BLR' });
      await loadBookingHistory(refId);
      alert('Booking marked as arrived!');
    } catch (err: any) {
      setError(err.message || 'Failed to update status');
    } finally {
      setUpdating(false);
    }
  };

  const handleDeliver = async () => {
    if (!refId) return;
    try {
      setUpdating(true);
      setError('');
      await apiService.deliverBooking(refId, { location: bookingHistory?.booking.destination || 'BLR' });
      await loadBookingHistory(refId);
      alert('Booking marked as delivered!');
    } catch (err: any) {
      setError(err.message || 'Failed to update status');
    } finally {
      setUpdating(false);
    }
  };

  const handleCancel = async () => {
    if (!refId || !confirm('Are you sure you want to cancel this booking?')) return;
    try {
      setUpdating(true);
      setError('');
      await apiService.cancelBooking(refId);
      await loadBookingHistory(refId);
      alert('Booking cancelled!');
    } catch (err: any) {
      setError(err.message || 'Failed to cancel booking');
    } finally {
      setUpdating(false);
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
    <>
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
          
          {/* Action Buttons */}
          <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Update Status</h3>
            <div className="flex flex-wrap gap-3">
              {bookingHistory.booking.status === 'BOOKED' && (
                <button
                  onClick={handleDepart}
                  disabled={updating}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                  {updating ? 'Updating...' : 'Mark as Departed'}
                </button>
              )}
              {bookingHistory.booking.status === 'DEPARTED' && (
                <button
                  onClick={handleArrive}
                  disabled={updating}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
                >
                  {updating ? 'Updating...' : 'Mark as Arrived'}
                </button>
              )}
              {bookingHistory.booking.status === 'ARRIVED' && (
                <button
                  onClick={handleDeliver}
                  disabled={updating}
                  className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50"
                >
                  {updating ? 'Updating...' : 'Mark as Delivered'}
                </button>
              )}
              {['BOOKED', 'DEPARTED'].includes(bookingHistory.booking.status) && (
                <button
                  onClick={handleCancel}
                  disabled={updating}
                  className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
                >
                  {updating ? 'Cancelling...' : 'Cancel Booking'}
                </button>
              )}
            </div>
          </div>

          <Timeline events={bookingHistory.timeline} />
        </div>
      )}
    </>
  );
}

export default function TrackPage() {
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <Suspense fallback={<LoadingSkeleton type="card" />}>
        <TrackContent />
      </Suspense>
    </div>
  );
}
