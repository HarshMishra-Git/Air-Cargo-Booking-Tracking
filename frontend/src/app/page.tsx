'use client';

import React from 'react';
import SearchBox from '@/components/SearchBox';
import MetricsDisplay from '@/components/MetricsDisplay';
import Link from 'next/link';
import { Package, Plane, History } from 'lucide-react';

export default function HomePage() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Hero Section */}
      <div className="text-center mb-12">
        <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
          Air Cargo Booking & Tracking
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          Book air cargo shipments and track them in real-time through their entire journey
        </p>
      </div>

      {/* Metrics */}
      <div className="max-w-4xl mx-auto mb-8">
        <MetricsDisplay />
      </div>

      {/* Search Box */}
      <div className="max-w-2xl mx-auto mb-16">
        <div className="bg-white rounded-xl shadow-lg p-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4 text-center">
            Track Your Shipment
          </h2>
          <SearchBox />
        </div>
      </div>

      {/* Features */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
        <Link
          href="/create-booking"
          className="bg-white rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow border border-gray-200"
        >
          <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4">
            <Package className="w-6 h-6 text-primary-600" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Create Booking</h3>
          <p className="text-gray-600">
            Create a new air cargo booking with automatic reference ID generation
          </p>
        </Link>

        <Link
          href="/search-route"
          className="bg-white rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow border border-gray-200"
        >
          <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4">
            <Plane className="w-6 h-6 text-primary-600" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Search Routes</h3>
          <p className="text-gray-600">
            Find direct and transit flight routes between any two airports
          </p>
        </Link>

        <Link
          href="/bookings"
          className="bg-white rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow border border-gray-200"
        >
          <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4">
            <History className="w-6 h-6 text-primary-600" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Booking History</h3>
          <p className="text-gray-600">
            View recent bookings and track them with detailed timeline
          </p>
        </Link>
      </div>

      {/* Stats */}
      <div className="bg-gradient-to-r from-primary-600 to-primary-700 rounded-xl p-8 text-white">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
          <div>
            <div className="text-4xl font-bold mb-2">50K+</div>
            <div className="text-primary-100">Bookings per Day</div>
          </div>
          <div>
            <div className="text-4xl font-bold mb-2">150K+</div>
            <div className="text-primary-100">Updates per Day</div>
          </div>
          <div>
            <div className="text-4xl font-bold mb-2">100K+</div>
            <div className="text-primary-100">Available Flights</div>
          </div>
        </div>
      </div>
    </div>
  );
}