'use client';

import React, { useState } from 'react';
import { apiService } from '@/services/api';
import { RouteSearchRequest, RouteSearchResponse } from '@/types';
import RouteCard from '@/components/RouteCard';
import LoadingSpinner from '@/components/LoadingSpinner';
import ErrorMessage from '@/components/ErrorMessage';
import { Plane, Calendar } from 'lucide-react';
import toast from 'react-hot-toast';

export default function SearchRoutePage() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<RouteSearchResponse | null>(null);
  const [formData, setFormData] = useState<RouteSearchRequest>({
    origin: '',
    destination: '',
    departure_date: '',
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: name === 'departure_date' ? value : value.toUpperCase(),
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    setResults(null);

    try {
      const data = await apiService.searchRoutes(formData);
      setResults(data);

      if (data.direct_flights.length === 0 && data.transit_routes.length === 0) {
        toast.error('No routes found for the selected criteria');
      } else {
        toast.success('Routes loaded successfully');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to search routes');
      toast.error('Failed to search routes');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
            <Plane className="w-6 h-6 text-primary-600" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900">Search Flight Routes</h1>
        </div>
        <p className="text-gray-600">
          Find direct flights and one-hop transit routes between airports
        </p>
      </div>

      {/* Search Form */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8 mb-8">
        <form onSubmit={handleSubmit} className="space-y-6">
          {error && <ErrorMessage message={error} onRetry={() => setError(null)} />}

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label htmlFor="origin" className="block text-sm font-medium text-gray-700 mb-2">
                Origin Airport
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
                Destination Airport
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

            <div>
              <label htmlFor="departure_date" className="block text-sm font-medium text-gray-700 mb-2">
                <div className="flex items-center gap-2">
                  <Calendar className="w-4 h-4" />
                  Departure Date
                </div>
              </label>
              <input
                type="date"
                id="departure_date"
                name="departure_date"
                value={formData.departure_date}
                onChange={handleChange}
                required
                min={new Date().toISOString().split('T')[0]}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition-all"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-primary-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <LoadingSpinner size="sm" />
                Searching Routes...
              </>
            ) : (
              'Search Routes'
            )}
          </button>
        </form>
      </div>

      {/* Results */}
      {results && (
        <div className="space-y-8">
          {/* Direct Flights */}
          {results.direct_flights.length > 0 && (
            <div>
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                Direct Flights ({results.direct_flights.length})
              </h2>
              <div className="space-y-4">
                {results.direct_flights.map((flight) => (
                  <RouteCard key={flight.id} option={{ route_type: 'direct', flights: [flight] }} />
                ))}
              </div>
            </div>
          )}

          {/* Transit Routes */}
          {results.transit_routes.length > 0 && (
            <div>
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                Transit Routes ({results.transit_routes.length})
              </h2>
              <div className="space-y-4">
                {results.transit_routes.map((route, index) => (
                  <RouteCard key={index} option={route} />
                ))}
              </div>
            </div>
          )}

          {/* No Results */}
          {results.direct_flights.length === 0 && results.transit_routes.length === 0 && (
            <div className="bg-gray-50 rounded-lg p-8 text-center">
              <p className="text-gray-600">No routes found for the selected criteria</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}