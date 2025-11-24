import React from 'react';
import { Booking } from '@/types';
import StatusBadge from './StatusBadge';
import { formatDateTime } from '@/lib/utils';
import { Package, MapPin, Weight, Calendar } from 'lucide-react';

interface BookingStatusCardProps {
  booking: Booking;
}

export default function BookingStatusCard({ booking }: BookingStatusCardProps) {
  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-primary-600 to-primary-700 px-6 py-4 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold">{booking.ref_id}</h2>
            <p className="text-primary-100 text-sm mt-1">Booking Reference</p>
          </div>
          <StatusBadge status={booking.status} className="bg-white text-primary-700" />
        </div>
      </div>

      {/* Content */}
      <div className="p-6 space-y-4">
        {/* Route */}
        <div className="flex items-center gap-4">
          <div className="flex-1">
            <p className="text-sm text-gray-500">Origin</p>
            <p className="text-lg font-semibold text-gray-900">{booking.origin}</p>
          </div>
          <div className="text-gray-400">
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </div>
          <div className="flex-1">
            <p className="text-sm text-gray-500">Destination</p>
            <p className="text-lg font-semibold text-gray-900">{booking.destination}</p>
          </div>
        </div>

        {/* Details Grid */}
        <div className="grid grid-cols-2 gap-4 pt-4 border-t border-gray-200">
          <div className="flex items-center gap-3">
            <Package className="w-5 h-5 text-gray-400" />
            <div>
              <p className="text-sm text-gray-500">Pieces</p>
              <p className="font-semibold text-gray-900">{booking.pieces}</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <Weight className="w-5 h-5 text-gray-400" />
            <div>
              <p className="text-sm text-gray-500">Weight</p>
              <p className="font-semibold text-gray-900">{booking.weight_kg} kg</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <Calendar className="w-5 h-5 text-gray-400" />
            <div>
              <p className="text-sm text-gray-500">Created</p>
              <p className="text-xs text-gray-700">{formatDateTime(booking.created_at)}</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <Calendar className="w-5 h-5 text-gray-400" />
            <div>
              <p className="text-sm text-gray-500">Updated</p>
              <p className="text-xs text-gray-700">{formatDateTime(booking.updated_at)}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}