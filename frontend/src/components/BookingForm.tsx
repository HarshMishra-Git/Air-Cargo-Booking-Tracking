'use client';

import React, { useState } from 'react';
import { apiService } from '@/services/api';
import { CreateBookingRequest } from '@/types';
import LoadingSpinner from './LoadingSpinner';
import ErrorMessage from './ErrorMessage';
import { useRouter } from 'next/navigation';
import toast from 'react-hot-toast';
import { Plane, Package, Weight } from 'lucide-react';

export default function BookingForm() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState<CreateBookingRequest>({
    origin: '',
    destination: '',
    pieces: 1,
    weight_kg: 1,
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: name === 'pieces' || name === 'weight_kg' ? parseInt(value) || 0 : value.toUpperCase(),
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const booking = await apiService.createBooking(formData);
      toast.success(`Booking created: ${booking.ref_id}`);
      router.push(`/track/${booking.ref_id}`);
    } catch (err: any) {
      setError(err.message || 'Failed to create booking');
      toast.error('Failed to create booking');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {error && <ErrorMessage message={error} onRetry={() => setError(null)} />}

      {/* Route */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label htmlFor="origin" className="block text-sm font-medium text-gray-700 mb-2">
            <div className="flex items-center gap-2">
              <Plane className="w-4 h-4" />
              Origin Airport Code
            </div>
          </label>
          <input
            type="text"
            id="origin"
            name="origin"
            value={formData.origin}
            onChange={handleChange}
            required
            maxLength={10}
            placeholder="e.g., DEL"
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition-all uppercase"
          />
        </div>

        <div>
          <label htmlFor="destination" className="block text-sm font-medium text-gray-700 mb-2">
            <div className="flex items-center gap-2">
              <Plane className="w-4 h-4 rotate-90" />
              Destination Airport Code
            </div>
          </label>
          <input
            type="text"
            id="destination"
            name="destination"
            value={formData.destination}
            onChange={handleChange}
            required
            maxLength={10}
            placeholder="e.g., BLR"
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition-all uppercase"
          />
        </div>
      </div>

      {/* Cargo Details */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label htmlFor="pieces" className="block text-sm font-medium text-gray-700 mb-2">
            <div className="flex items-center gap-2">
              <Package className="w-4 h-4" />
              Number of Pieces
            </div>
          </label>
          <input
            type="number"
            id="pieces"
            name="pieces"
            value={formData.pieces}
            onChange={handleChange}
            required
            min={1}
            placeholder="10"
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition-all"
          />
        </div>

        <div>
          <label htmlFor="weight_kg" className="block text-sm font-medium text-gray-700 mb-2">
            <div className="flex items-center gap-2">
              <Weight className="w-4 h-4" />
              Total Weight (kg)
            </div>
          </label>
          <input
            type="number"
            id="weight_kg"
            name="weight_kg"
            value={formData.weight_kg}
            onChange={handleChange}
            required
            min={1}
            placeholder="500"
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition-all"
          />
        </div>
      </div>

      {/* Submit Button */}
      <button
        type="submit"
        disabled={loading}
        className="w-full bg-primary-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
      >
        {loading ? (
          <>
            <LoadingSpinner size="sm" />
            Creating Booking...
          </>
        ) : (
          'Create Booking'
        )}
      </button>
    </form>
  );
}