'use client';

import Link from 'next/link';
import { Plane, Menu, X } from 'lucide-react';
import { useState } from 'react';

export default function Navigation() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <nav className="bg-gradient-to-r from-primary-600 to-primary-700 shadow-lg sticky top-0 z-50">
      <div className="w-full px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2 text-white hover:opacity-90 transition-opacity">
            <Plane className="w-8 h-8" />
            <span className="text-xl font-bold hidden sm:inline">
              Air Cargo System
            </span>
            <span className="text-xl font-bold sm:hidden">
              ACS
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-3">
            <Link
              href="/create-booking"
              className="px-4 py-2 bg-white text-primary-600 rounded-lg font-medium hover:bg-primary-50 transition-colors shadow-sm"
            >
              New Booking
            </Link>
            <Link
              href="/search-route"
              className="px-4 py-2 bg-white text-primary-600 rounded-lg font-medium hover:bg-primary-50 transition-colors shadow-sm"
            >
              Search Routes
            </Link>
            <Link
              href="/"
              className="px-4 py-2 bg-white/10 text-white rounded-lg font-medium hover:bg-white/20 transition-colors border border-white/30"
            >
              Track Shipment
            </Link>
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden p-2 text-white hover:bg-white/10 rounded-lg transition-colors"
          >
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <div className="md:hidden pb-4 space-y-2">
            <Link
              href="/create-booking"
              onClick={() => setMobileMenuOpen(false)}
              className="block px-4 py-2 bg-white text-primary-600 rounded-lg font-medium hover:bg-primary-50 transition-colors text-center"
            >
              New Booking
            </Link>
            <Link
              href="/search-route"
              onClick={() => setMobileMenuOpen(false)}
              className="block px-4 py-2 bg-white text-primary-600 rounded-lg font-medium hover:bg-primary-50 transition-colors text-center"
            >
              Search Routes
            </Link>
            <Link
              href="/"
              onClick={() => setMobileMenuOpen(false)}
              className="block px-4 py-2 bg-white/10 text-white rounded-lg font-medium hover:bg-white/20 transition-colors border border-white/30 text-center"
            >
              Track Shipment
            </Link>
          </div>
        )}
      </div>
    </nav>
  );
}
