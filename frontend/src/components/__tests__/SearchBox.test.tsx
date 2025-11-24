import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import SearchBox from '../SearchBox';
import { apiService } from '@/services/api';

jest.mock('@/services/api');

describe('SearchBox', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders search input', () => {
    render(<SearchBox />);
    const input = screen.getByPlaceholderText(/enter booking reference/i);
    expect(input).toBeInTheDocument();
  });

  it('shows error for empty search', async () => {
    render(<SearchBox />);
    const button = screen.getByRole('button', { name: /search/i });
    
    fireEvent.click(button);
    
    await waitFor(() => {
      expect(screen.getByText(/please enter a booking reference/i)).toBeInTheDocument();
    });
  });

  it('calls API with correct ref_id', async () => {
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

    (apiService.getBooking as jest.Mock).mockResolvedValue(mockBooking);

    render(<SearchBox />);
    const input = screen.getByPlaceholderText(/enter booking reference/i);
    const button = screen.getByRole('button', { name: /search/i });

    fireEvent.change(input, { target: { value: 'ACB12345' } });
    fireEvent.click(button);

    await waitFor(() => {
      expect(apiService.getBooking).toHaveBeenCalledWith('ACB12345');
    });
  });

  it('handles API errors gracefully', async () => {
    (apiService.getBooking as jest.Mock).mockRejectedValue(new Error('Booking not found'));

    render(<SearchBox />);
    const input = screen.getByPlaceholderText(/enter booking reference/i);
    const button = screen.getByRole('button', { name: /search/i });

    fireEvent.change(input, { target: { value: 'INVALID' } });
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText(/booking not found/i)).toBeInTheDocument();
    });
  });
});
