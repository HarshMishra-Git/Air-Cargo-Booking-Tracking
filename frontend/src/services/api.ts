import axios, { AxiosInstance, AxiosError } from 'axios';
import {
  Booking,
  BookingHistory,
  CreateBookingRequest,
  DepartBookingRequest,
  ArriveBookingRequest,
  DeliverBookingRequest,
  RouteSearchRequest,
  RouteSearchResponse,
} from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const API_VERSION = '/api/v1';

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: `${API_BASE_URL}${API_VERSION}`,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 30000,
    });

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response) {
          // Server responded with error
          const message = (error.response.data as any)?.detail || 'An error occurred';
          throw new Error(message);
        } else if (error.request) {
          // Request made but no response
          throw new Error('No response from server. Please check your connection.');
        } else {
          // Error setting up request
          throw new Error(error.message);
        }
      }
    );
  }

  // Booking endpoints
  async createBooking(data: CreateBookingRequest): Promise<Booking> {
    const response = await this.client.post<Booking>('/bookings', data);
    return response.data;
  }

  async getBooking(refId: string): Promise<Booking> {
    const response = await this.client.get<Booking>(`/bookings/${refId}`);
    return response.data;
  }

  async getBookingHistory(refId: string): Promise<BookingHistory> {
    const response = await this.client.get<BookingHistory>(`/bookings/${refId}/history`);
    return response.data;
  }

  async departBooking(refId: string, data: DepartBookingRequest): Promise<Booking> {
    const response = await this.client.post<Booking>(`/bookings/${refId}/depart`, data);
    return response.data;
  }

  async arriveBooking(refId: string, data: ArriveBookingRequest): Promise<Booking> {
    const response = await this.client.post<Booking>(`/bookings/${refId}/arrive`, data);
    return response.data;
  }

  async deliverBooking(refId: string, data: DeliverBookingRequest): Promise<Booking> {
    const response = await this.client.post<Booking>(`/bookings/${refId}/deliver`, data);
    return response.data;
  }

  async listBookings(limit: number = 20, offset: number = 0): Promise<Booking[]> {
    const response = await this.client.get<Booking[]>('/bookings', {
      params: { limit, offset }
    });
    return response.data;
  }

  async cancelBooking(refId: string): Promise<Booking> {
    const response = await this.client.delete<Booking>(`/bookings/${refId}`);
    return response.data;
  }

  // Route endpoints
  async searchRoutes(data: RouteSearchRequest): Promise<RouteSearchResponse> {
    const response = await this.client.post<RouteSearchResponse>('/routes/search', data);
    return response.data;
  }

  // Health check
  async healthCheck(): Promise<any> {
    const response = await this.client.get(`${API_BASE_URL}/health`);
    return response.data;
  }
}

export const apiService = new ApiService();