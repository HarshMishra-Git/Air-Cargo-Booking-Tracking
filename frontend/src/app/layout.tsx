'use client';

import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { Toaster } from 'react-hot-toast';
import Link from 'next/link';
import { Plane, Menu, X } from 'lucide-react';
import { useState } from 'react';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Air Cargo Booking & Tracking',
  description: 'Book and track air cargo shipments in real-time',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="min-h-screen bg-gray-50 flex flex-col">
          {/* Navigation */}
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

          {/* Main Content */}
          <main>{children}</main>

          {/* Footer */}
          <footer className="bg-white border-t border-gray-200 mt-auto">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
              <p className="text-center text-gray-500 text-sm">
                © 2025 Air Cargo Booking & Tracking System. All rights reserved.
              </p>
            </div>
          </footer>
        </div>

        <Toaster position="top-right" />
      </body>
    </html>
  );
}