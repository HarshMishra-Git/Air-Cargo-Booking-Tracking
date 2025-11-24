import { render, screen } from '@testing-library/react';
import StatusBadge from '../StatusBadge';

describe('StatusBadge', () => {
  it('renders BOOKED status correctly', () => {
    render(<StatusBadge status="BOOKED" />);
    expect(screen.getByText('BOOKED')).toBeInTheDocument();
  });

  it('renders DEPARTED status correctly', () => {
    render(<StatusBadge status="DEPARTED" />);
    expect(screen.getByText('DEPARTED')).toBeInTheDocument();
  });

  it('renders ARRIVED status correctly', () => {
    render(<StatusBadge status="ARRIVED" />);
    expect(screen.getByText('ARRIVED')).toBeInTheDocument();
  });

  it('renders DELIVERED status correctly', () => {
    render(<StatusBadge status="DELIVERED" />);
    expect(screen.getByText('DELIVERED')).toBeInTheDocument();
  });

  it('renders CANCELLED status correctly', () => {
    render(<StatusBadge status="CANCELLED" />);
    expect(screen.getByText('CANCELLED')).toBeInTheDocument();
  });

  it('applies correct styling for each status', () => {
    const { rerender } = render(<StatusBadge status="BOOKED" />);
    let badge = screen.getByText('BOOKED');
    expect(badge).toHaveClass('bg-blue-100');

    rerender(<StatusBadge status="DEPARTED" />);
    badge = screen.getByText('DEPARTED');
    expect(badge).toHaveClass('bg-yellow-100');

    rerender(<StatusBadge status="ARRIVED" />);
    badge = screen.getByText('ARRIVED');
    expect(badge).toHaveClass('bg-green-100');

    rerender(<StatusBadge status="DELIVERED" />);
    badge = screen.getByText('DELIVERED');
    expect(badge).toHaveClass('bg-purple-100');

    rerender(<StatusBadge status="CANCELLED" />);
    badge = screen.getByText('CANCELLED');
    expect(badge).toHaveClass('bg-red-100');
  });
});
