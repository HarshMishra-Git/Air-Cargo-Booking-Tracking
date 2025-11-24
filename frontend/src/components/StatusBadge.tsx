import React from 'react';
import { BookingStatus } from '@/types';

interface StatusBadgeProps {
  status: BookingStatus;
  className?: string;
}

export default function StatusBadge({ status, className = '' }: StatusBadgeProps) {
  const statusConfig = {
    BOOKED: {
      bg: 'bg-blue-100',
      text: 'text-blue-800',
      label: 'Booked',
    },
    DEPARTED: {
      bg: 'bg-yellow-100',
      text: 'text-yellow-800',
      label: 'Departed',
    },
    ARRIVED: {
      bg: 'bg-green-100',
      text: 'text-green-800',
      label: 'Arrived',
    },
    DELIVERED: {
      bg: 'bg-purple-100',
      text: 'text-purple-800',
      label: 'Delivered',
    },
    CANCELLED: {
      bg: 'bg-red-100',
      text: 'text-red-800',
      label: 'Cancelled',
    },
  };

  const config = statusConfig[status] || statusConfig.BOOKED;

  return (
    <span
      className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${config.bg} ${config.text} ${className}`}
    >
      {config.label}
    </span>
  );
}