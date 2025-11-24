'use client';

import React, { useEffect, useState } from 'react';
import { Activity, TrendingUp, Database, Zap } from 'lucide-react';

interface Metrics {
  bookings: {
    created: number;
    departed: number;
    arrived: number;
    cancelled: number;
  };
  routes: {
    searches: number;
  };
  cache: {
    hits: number;
    misses: number;
  };
}

export default function MetricsDisplay() {
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/metrics/summary`);
        const data = await response.json();
        setMetrics(data);
      } catch (error) {
        console.error('Failed to fetch metrics:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();
    const interval = setInterval(fetchMetrics, 5000); // Refresh every 5 seconds

    return () => clearInterval(interval);
  }, []);

  if (loading || !metrics) {
    return null;
  }

  const cacheHitRate = metrics.cache.hits + metrics.cache.misses > 0
    ? ((metrics.cache.hits / (metrics.cache.hits + metrics.cache.misses)) * 100).toFixed(1)
    : '0';

  return (
    <div className="bg-white rounded-lg shadow p-6 mb-6">
      <div className="flex items-center mb-4">
        <Activity className="w-5 h-5 text-primary-600 mr-2" />
        <h3 className="text-lg font-semibold text-gray-900">System Metrics</h3>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="text-center">
          <div className="text-2xl font-bold text-primary-600">{metrics.bookings.created}</div>
          <div className="text-sm text-gray-600">Bookings Created</div>
        </div>

        <div className="text-center">
          <div className="text-2xl font-bold text-green-600">{metrics.bookings.arrived}</div>
          <div className="text-sm text-gray-600">Arrived</div>
        </div>

        <div className="text-center">
          <div className="text-2xl font-bold text-blue-600">{metrics.routes.searches}</div>
          <div className="text-sm text-gray-600">Route Searches</div>
        </div>

        <div className="text-center">
          <div className="text-2xl font-bold text-purple-600">{cacheHitRate}%</div>
          <div className="text-sm text-gray-600">Cache Hit Rate</div>
        </div>
      </div>
    </div>
  );
}
