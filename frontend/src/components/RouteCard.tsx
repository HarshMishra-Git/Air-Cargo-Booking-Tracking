import React from 'react';
import { Flight, RouteOption } from '@/types';
import { formatDateTime, formatTime, calculateDuration } from '@/lib/utils';
import { Plane, Clock, ArrowRight } from 'lucide-react';

interface RouteCardProps {
  option: RouteOption | { route_type: 'direct'; flights: Flight[] };
}

export default function RouteCard({ option }: RouteCardProps) {
  const isDirect = option.route_type === 'direct';
  const flights = option.flights;

  if (flights.length === 0) return null;

  const firstFlight = flights[0];
  const lastFlight = flights[flights.length - 1];

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Plane className="w-5 h-5 text-primary-600" />
          <span className="font-semibold text-gray-900">
            {isDirect ? 'Direct Flight' : `Transit via ${'transit_airport' in option ? option.transit_airport : ''}`}
          </span>
        </div>
        <span className="text-sm text-gray-500 flex items-center gap-1">
          <Clock className="w-4 h-4" />
          {'total_duration_hours' in option
            ? `${option.total_duration_hours.toFixed(1)}h`
            : calculateDuration(firstFlight.departure_datetime, lastFlight.arrival_datetime)}
        </span>
      </div>

      {/* Flights */}
      <div className="space-y-3">
        {flights.map((flight, index) => (
          <div key={flight.id}>
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <span className="text-lg font-bold text-gray-900">{flight.origin}</span>
                  <ArrowRight className="w-4 h-4 text-gray-400" />
                  <span className="text-lg font-bold text-gray-900">{flight.destination}</span>
                </div>
                <div className="text-sm text-gray-600 mt-1">
                  {flight.airline_name} • {flight.flight_number}
                </div>
              </div>
              <div className="text-right">
                <div className="text-sm font-medium text-gray-900">
                  {formatTime(flight.departure_datetime)} - {formatTime(flight.arrival_datetime)}
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  {calculateDuration(flight.departure_datetime, flight.arrival_datetime)}
                </div>
              </div>
            </div>

            {/* Layover indicator */}
            {index < flights.length - 1 && (
              <div className="mt-2 ml-4 text-xs text-gray-500 flex items-center gap-1">
                <div className="w-1 h-1 rounded-full bg-gray-400"></div>
                Layover at {flight.destination}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}