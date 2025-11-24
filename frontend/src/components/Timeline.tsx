import React from 'react';
import { BookingEvent } from '@/types';
import { formatDateTime } from '@/lib/utils';
import { 
  CheckCircle2, 
  Circle, 
  Plane, 
  MapPin, 
  XCircle,
  Package 
} from 'lucide-react';

interface TimelineProps {
  events: BookingEvent[];
}

export default function Timeline({ events }: TimelineProps) {
  const getEventIcon = (eventType: string) => {
    switch (eventType) {
      case 'BOOKED':
        return <Package className="w-5 h-5" />;
      case 'DEPARTED':
        return <Plane className="w-5 h-5" />;
      case 'ARRIVED':
        return <MapPin className="w-5 h-5" />;
      case 'DELIVERED':
        return <CheckCircle2 className="w-5 h-5" />;
      case 'CANCELLED':
        return <XCircle className="w-5 h-5" />;
      default:
        return <Circle className="w-5 h-5" />;
    }
  };

  const getEventColor = (eventType: string) => {
    switch (eventType) {
      case 'BOOKED':
        return 'bg-blue-500 text-white';
      case 'DEPARTED':
        return 'bg-yellow-500 text-white';
      case 'ARRIVED':
        return 'bg-green-500 text-white';
      case 'DELIVERED':
        return 'bg-purple-500 text-white';
      case 'CANCELLED':
        return 'bg-red-500 text-white';
      default:
        return 'bg-gray-500 text-white';
    }
  };

  if (events.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        No events recorded yet
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {events.map((event, index) => (
        <div key={event.id} className="relative flex gap-4">
          {/* Timeline line */}
          {index !== events.length - 1 && (
            <div className="absolute left-6 top-12 bottom-0 w-0.5 bg-gray-200" />
          )}

          {/* Icon */}
          <div
            className={`flex-shrink-0 w-12 h-12 rounded-full flex items-center justify-center ${getEventColor(
              event.event_type
            )}`}
          >
            {getEventIcon(event.event_type)}
          </div>

          {/* Content */}
          <div className="flex-1 bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
            <div className="flex items-start justify-between">
              <div>
                <h4 className="font-semibold text-gray-900">{event.event_type}</h4>
                {event.location && (
                  <p className="text-sm text-gray-600 mt-1">
                    Location: <span className="font-medium">{event.location}</span>
                  </p>
                )}
                {event.flight_number && (
                  <p className="text-sm text-gray-600 mt-1">
                    Flight: <span className="font-medium">{event.flight_number}</span>
                  </p>
                )}
                {event.notes && (
                  <p className="text-sm text-gray-500 mt-2 italic">{event.notes}</p>
                )}
              </div>
              <time className="text-xs text-gray-500 whitespace-nowrap">
                {formatDateTime(event.created_at)}
              </time>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}