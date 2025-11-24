import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import BookingForm from '../BookingForm';
import { apiService } from '@/services/api';

jest.mock('@/services/api');

describe('BookingForm', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders all form fields', () => {
    render(<BookingForm />);
    
    expect(screen.getByLabelText(/origin/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/destination/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/pieces/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/weight/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /create booking/i })).toBeInTheDocument();
  });

  it('validates required fields', async () => {
    render(<BookingForm />);
    const submitButton = screen.getByRole('button', { name: /create booking/i });
    
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/all fields are required/i)).toBeInTheDocument();
    });
  });

  it('validates origin and destination are different', async () => {
    render(<BookingForm />);
    
    fireEvent.change(screen.getByLabelText(/origin/i), { target: { value: 'DEL' } });
    fireEvent.change(screen.getByLabelText(/destination/i), { target: { value: 'DEL' } });
    fireEvent.change(screen.getByLabelText(/pieces/i), { target: { value: '10' } });
    fireEvent.change(screen.getByLabelText(/weight/i), { target: { value: '500' } });
    
    const submitButton = screen.getByRole('button', { name: /create booking/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/origin and destination must be different/i)).toBeInTheDocument();
    });
  });

  it('submits form with valid data', async () => {
    const mockBooking = {
      id: 1,
      ref_id: 'ACB12345',
      origin: 'DEL',
      destination: 'BLR',
      status: 'BOOKED',
      pieces: 10,
      weight_kg: 500,
      flight_ids: [],
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    (apiService.createBooking as jest.Mock).mockResolvedValue(mockBooking);

    render(<BookingForm />);
    
    fireEvent.change(screen.getByLabelText(/origin/i), { target: { value: 'DEL' } });
    fireEvent.change(screen.getByLabelText(/destination/i), { target: { value: 'BLR' } });
    fireEvent.change(screen.getByLabelText(/pieces/i), { target: { value: '10' } });
    fireEvent.change(screen.getByLabelText(/weight/i), { target: { value: '500' } });
    
    const submitButton = screen.getByRole('button', { name: /create booking/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(apiService.createBooking).toHaveBeenCalledWith({
        origin: 'DEL',
        destination: 'BLR',
        pieces: 10,
        weight_kg: 500,
      });
    });
  });

  it('handles API errors', async () => {
    (apiService.createBooking as jest.Mock).mockRejectedValue(new Error('Failed to create booking'));

    render(<BookingForm />);
    
    fireEvent.change(screen.getByLabelText(/origin/i), { target: { value: 'DEL' } });
    fireEvent.change(screen.getByLabelText(/destination/i), { target: { value: 'BLR' } });
    fireEvent.change(screen.getByLabelText(/pieces/i), { target: { value: '10' } });
    fireEvent.change(screen.getByLabelText(/weight/i), { target: { value: '500' } });
    
    const submitButton = screen.getByRole('button', { name: /create booking/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/failed to create booking/i)).toBeInTheDocument();
    });
  });
});
