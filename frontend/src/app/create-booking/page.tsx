'use client';

import React from 'react';
import BookingForm from '@/components/BookingForm';
import { Package } from 'lucide-react';

export default function CreateBookingPage() {
  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
            <Package className="w-6 h-6 text-primary-600" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900">Create New Booking</h1>
        </div>
        <p className="text-gray-600">
          Fill in the details below to create a new air cargo booking. A unique reference ID will be generated automatically.
        </p>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
        <BookingForm />
      </div>
    </div>
  );
}