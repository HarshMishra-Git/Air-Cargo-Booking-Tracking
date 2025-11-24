import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { Toaster } from 'react-hot-toast';
import Link from 'next/link';
import { Plane } from 'lucide-react';

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
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="min-h-screen bg-gray-50">
          {/* Navigation */}
          <nav className="bg-white border-b border-gray-200">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex justify-between items-center h-16">
                <Link href="/" className="flex items-center gap-2">
                  <Plane className="w-8 h-8 text-primary-600" />
                  <span className="text-xl font-bold text-gray-900">
                    Air Cargo System
                  </span>
                </Link>
                <div className="flex items-center gap-4">
                  <Link
                    href="/create-booking"
                    className="text-gray-700 hover:text-primary-600 font-medium transition-colors"
                  >
                    New Booking
                  </Link>
                  <Link
                    href="/search-route"
                    className="text-gray-700 hover:text-primary-600 font-medium transition-colors"
                  >
                    Search Routes
                  </Link>
                </div>
              </div>
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