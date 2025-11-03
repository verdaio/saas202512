'use client';

import type { Service, TimeSlot, Owner, Pet } from '@/lib/api';
import { format, parseISO } from 'date-fns';

interface Props {
  appointmentId: string;
  service: Service;
  date: string;
  slot: TimeSlot;
  owner: Owner;
  pets: Pet[];
  onStartOver: () => void;
}

export default function ConfirmationStep({
  appointmentId,
  service,
  date,
  slot,
  owner,
  pets,
  onStartOver,
}: Props) {
  return (
    <div className="text-center">
      <div className="mb-6">
        <div className="mx-auto w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-4">
          <svg
            className="w-10 h-10 text-green-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M5 13l4 4L19 7"
            />
          </svg>
        </div>
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Booking Confirmed!</h2>
        <p className="text-gray-600">
          Your appointment has been successfully booked. We've sent a confirmation to your email.
        </p>
      </div>

      {/* Appointment Details */}
      <div className="bg-gray-50 rounded-lg p-6 mb-6 text-left">
        <h3 className="font-semibold mb-4 text-center">Appointment Details</h3>

        <div className="space-y-3">
          <div className="flex justify-between">
            <span className="text-gray-600">Service:</span>
            <span className="font-medium">{service.name}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Date:</span>
            <span className="font-medium">{format(parseISO(date), 'MMMM d, yyyy')}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Time:</span>
            <span className="font-medium">{format(parseISO(slot.start_time), 'h:mm a')}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Duration:</span>
            <span className="font-medium">{service.duration_minutes} minutes</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Pet(s):</span>
            <span className="font-medium">{pets.map((p) => p.name).join(', ')}</span>
          </div>
          <div className="flex justify-between border-t pt-3">
            <span className="text-gray-600">Price:</span>
            <span className="font-bold text-lg text-primary-600">
              ${(service.price / 100).toFixed(2)}
            </span>
          </div>
        </div>
      </div>

      {/* Contact Information */}
      <div className="bg-gray-50 rounded-lg p-6 mb-6 text-left">
        <h3 className="font-semibold mb-4 text-center">Your Information</h3>
        <div className="space-y-2">
          <p className="text-gray-700">
            {owner.first_name} {owner.last_name}
          </p>
          <p className="text-gray-600">{owner.email}</p>
          <p className="text-gray-600">{owner.phone}</p>
        </div>
      </div>

      {/* Reference Number */}
      <div className="mb-6">
        <p className="text-sm text-gray-600">Confirmation Number:</p>
        <p className="text-lg font-mono font-semibold text-gray-900">{appointmentId}</p>
      </div>

      {/* Actions */}
      <div className="space-y-3">
        <button
          onClick={onStartOver}
          className="w-full px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
        >
          Book Another Appointment
        </button>
        <p className="text-sm text-gray-600">
          You'll receive SMS reminders 24 hours and 2 hours before your appointment.
        </p>
      </div>
    </div>
  );
}
