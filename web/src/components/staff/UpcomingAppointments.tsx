'use client';

import { useState, useEffect } from 'react';
import { appointmentsApi, Appointment } from '@/lib/staffApi';
import { format, parseISO, addDays } from 'date-fns';
import Link from 'next/link';

export default function UpcomingAppointments() {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadAppointments();
  }, []);

  const loadAppointments = async () => {
    try {
      setLoading(true);
      const today = new Date();
      const endDate = addDays(today, 7);

      const data = await appointmentsApi.getByDateRange(
        today.toISOString().split('T')[0],
        endDate.toISOString().split('T')[0]
      );

      // Filter out today's appointments and only keep future ones
      const upcoming = data.filter(a => {
        const apptDate = new Date(a.scheduled_start);
        const todayDate = new Date();
        todayDate.setHours(0, 0, 0, 0);
        apptDate.setHours(0, 0, 0, 0);
        return apptDate > todayDate;
      });

      setAppointments(upcoming.slice(0, 10)); // Limit to 10
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load appointments');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toUpperCase()) {
      case 'PENDING':
        return 'bg-yellow-100 text-yellow-800';
      case 'CONFIRMED':
        return 'bg-blue-100 text-blue-800';
      case 'CHECKED_IN':
        return 'bg-purple-100 text-purple-800';
      case 'IN_PROGRESS':
        return 'bg-orange-100 text-orange-800';
      case 'COMPLETED':
        return 'bg-green-100 text-green-800';
      case 'CANCELLED':
        return 'bg-red-100 text-red-800';
      case 'NO_SHOW':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          Upcoming Appointments (Next 7 Days)
        </h2>
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          Upcoming Appointments (Next 7 Days)
        </h2>
        <div className="text-center py-8 text-red-600">{error}</div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold text-gray-900">
            Upcoming Appointments (Next 7 Days)
          </h2>
          <Link
            href="/staff/appointments"
            className="text-sm text-primary-600 hover:text-primary-700"
          >
            View All →
          </Link>
        </div>
      </div>

      <div className="divide-y divide-gray-200">
        {appointments.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            No upcoming appointments in the next 7 days
          </div>
        ) : (
          appointments.map((appointment) => (
            <Link
              key={appointment.id}
              href={`/staff/appointments/${appointment.id}`}
              className="block p-4 hover:bg-gray-50 transition"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <div>
                      <p className="text-sm font-medium text-gray-900">
                        {format(parseISO(appointment.scheduled_start), 'EEE, MMM dd')}
                      </p>
                      <p className="text-sm text-gray-500">
                        {format(parseISO(appointment.scheduled_start), 'h:mm a')}
                      </p>
                    </div>
                    <span
                      className={`px-2 py-1 text-xs font-medium rounded ${getStatusColor(
                        appointment.status
                      )}`}
                    >
                      {appointment.status.replace('_', ' ')}
                    </span>
                  </div>

                  <div className="space-y-1 text-sm">
                    <p className="text-gray-900">
                      <span className="font-medium">Customer:</span>{' '}
                      {appointment.owner?.first_name} {appointment.owner?.last_name}
                    </p>
                    <p className="text-gray-600">
                      <span className="font-medium">Service:</span>{' '}
                      {appointment.service?.name}
                    </p>
                    <p className="text-gray-600">
                      <span className="font-medium">Pet:</span>{' '}
                      {appointment.pets?.map((p) => p.name).join(', ') || 'N/A'}
                    </p>
                  </div>
                </div>

                {appointment.service && (
                  <div className="ml-4 text-right">
                    <p className="text-primary-600 font-semibold">
                      ${(appointment.service.price / 100).toFixed(2)}
                    </p>
                  </div>
                )}
              </div>
            </Link>
          ))
        )}
      </div>
    </div>
  );
}
