'use client';

import React, { useState, useEffect } from 'react';
import { apiService } from '@/services/api';
import { Booking } from '@/types';
import StatusBadge from '@/components/StatusBadge';
import LoadingSkeleton from '@/components/LoadingSkeleton';
import Link from 'next/link';
import { Package, Calendar, Weight, Box } from 'lucide-react';

export default function BookingsPage() {
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [page, setPage] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const limit = 20;

  useEffect(() => {
    loadBookings();
  }, [page]);

  const loadBookings = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await apiService.listBookings(limit, page * limit);
      
      if (response.length < limit) {
        setHasMore(false);
      }
      
      setBookings(response);
    } catch (err: any) {
      setError(err.message || 'Failed to load bookings');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Booking History</h1>
        <p className="text-gray-600">View and track all your recent bookings</p>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {/* Loading State */}
      {loading && <LoadingSkeleton type="list" count={5} />}

      {/* Bookings List */}
      {!loading && bookings.length === 0 && (
        <div className="text-center py-12 bg-white rounded-lg shadow-sm">
          <Package className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No bookings found</h3>
          <p className="text-gray-600 mb-6">Create your first booking to get started</p>
          <Link
            href="/create-booking"
            className="inline-block bg-primary-600 text-white px-6 py-2 rounded-lg hover:bg-primary-700 transition-colors"
          >
            Create Booking
          </Link>
        </div>
      )}

      {!loading && bookings.length > 0 && (
        <div className="space-y-4">
          {bookings.map((booking) => (
            <Link
              key={booking.id}
              href={`/track?ref_id=${booking.ref_id}`}
              className="block bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow border border-gray-200 p-6"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  {/* Reference ID and Status */}
                  <div className="flex items-center gap-3 mb-3">
                    <h3 className="text-xl font-semibold text-gray-900">
                      {booking.ref_id}
                    </h3>
                    <StatusBadge status={booking.status} />
                  </div>

                  {/* Route */}
                  <div className="flex items-center gap-2 text-gray-700 mb-3">
                    <span className="font-medium">{booking.origin}</span>
                    <span className="text-gray-400">→</span>
                    <span className="font-medium">{booking.destination}</span>
                  </div>

                  {/* Details */}
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-sm">
                    <div className="flex items-center gap-2 text-gray-600">
                      <Box className="w-4 h-4" />
                      <span>{booking.pieces} pieces</span>
                    </div>
                    <div className="flex items-center gap-2 text-gray-600">
                      <Weight className="w-4 h-4" />
                      <span>{booking.weight_kg} kg</span>
                    </div>
                    <div className="flex items-center gap-2 text-gray-600">
                      <Calendar className="w-4 h-4" />
                      <span>{formatDate(booking.created_at)}</span>
                    </div>
                  </div>
                </div>

                {/* Arrow */}
                <div className="ml-4">
                  <svg
                    className="w-6 h-6 text-gray-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 5l7 7-7 7"
                    />
                  </svg>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}

      {/* Pagination */}
      {!loading && bookings.length > 0 && (
        <div className="mt-8 flex items-center justify-between">
          <button
            onClick={() => setPage(Math.max(0, page - 1))}
            disabled={page === 0}
            className="px-4 py-2 bg-white border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Previous
          </button>

          <span className="text-gray-600">
            Page {page + 1}
          </span>

          <button
            onClick={() => setPage(page + 1)}
            disabled={!hasMore}
            className="px-4 py-2 bg-white border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}
