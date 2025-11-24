export type BookingStatus = 'BOOKED' | 'DEPARTED' | 'ARRIVED' | 'DELIVERED' | 'CANCELLED';

export type EventType = 'BOOKED' | 'DEPARTED' | 'ARRIVED' | 'DELIVERED' | 'CANCELLED';

export interface Flight {
  id: number;
  flight_number: string;
  airline_name: string;
  departure_datetime: string;
  arrival_datetime: string;
  origin: string;
  destination: string;
  created_at: string;
  updated_at: string;
}

export interface Booking {
  id: number;
  ref_id: string;
  origin: string;
  destination: string;
  pieces: number;
  weight_kg: number;
  status: BookingStatus;
  flight_ids: number[];
  created_at: string;
  updated_at: string;
}

export interface BookingEvent {
  id: number;
  event_type: EventType;
  location: string | null;
  flight_id: number | null;
  flight_number: string | null;
  notes: string | null;
  created_at: string;
}

export interface BookingHistory {
  booking: Booking;
  timeline: BookingEvent[];
}

export interface CreateBookingRequest {
  origin: string;
  destination: string;
  pieces: number;
  weight_kg: number;
  flight_ids?: number[];
}

export interface DepartBookingRequest {
  location: string;
  flight_id?: number;
  flight_number?: string;
  notes?: string;
}

export interface ArriveBookingRequest {
  location: string;
  flight_id?: number;
  flight_number?: string;
  notes?: string;
}

export interface DeliverBookingRequest {
  location: string;
  notes?: string;
}

export interface RouteOption {
  route_type: 'direct' | 'transit';
  flights: Flight[];
  total_duration_hours: number;
  transit_airport: string | null;
}

export interface RouteSearchRequest {
  origin: string;
  destination: string;
  departure_date: string;
}

export interface RouteSearchResponse {
  origin: string;
  destination: string;
  departure_date: string;
  direct_flights: Flight[];
  transit_routes: RouteOption[];
}