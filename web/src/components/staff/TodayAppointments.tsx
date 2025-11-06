'use client';

import { useState, useEffect } from 'react';
import { appointmentsApi, Appointment } from '@/lib/staffApi';
import { format, parseISO } from 'date-fns';

interface Props {
  onAction?: () => void;
}

export default function TodayAppointments({ onAction }: Props) {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  useEffect(() => {
    loadAppointments();
  }, []);

  const loadAppointments = async () => {
    try {
      setLoading(true);
      const data = await appointmentsApi.getToday();
      setAppointments(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load appointments');
    } finally {
      setLoading(false);
    }
  };

  const handleCheckIn = async (id: string) => {
    try {
      setActionLoading(id);
      await appointmentsApi.checkIn(id);
      await loadAppointments();
      onAction?.();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to check in');
    } finally {
      setActionLoading(null);
    }
  };

  const handleStart = async (id: string) => {
    try {
      setActionLoading(id);
      await appointmentsApi.start(id);
      await loadAppointments();
      onAction?.();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to start');
    } finally {
      setActionLoading(null);
    }
  };

  const handleComplete = async (id: string) => {
    try {
      setActionLoading(id);
      await appointmentsApi.complete(id);
      await loadAppointments();
      onAction?.();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to complete');
    } finally {
      setActionLoading(null);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'confirmed':
        return 'bg-blue-100 text-blue-800';
      case 'checked_in':
        return 'bg-purple-100 text-purple-800';
      case 'in_progress':
        return 'bg-orange-100 text-orange-800';
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'cancelled':
        return 'bg-red-100 text-red-800';
      case 'no_show':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Today's Appointments</h2>
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Today's Appointments</h2>
        <div className="text-center py-8 text-red-600">{error}</div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold text-gray-900">Today's Appointments</h2>
          <button
            onClick={loadAppointments}
            className="text-sm text-primary-600 hover:text-primary-700"
          >
            Refresh
          </button>
        </div>
      </div>

      <div className="divide-y divide-gray-200">
        {appointments.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            No appointments scheduled for today
          </div>
        ) : (
          appointments.map((appointment) => (
            <div key={appointment.id} className="p-6 hover:bg-gray-50">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <span className="text-lg font-semibold text-gray-900">
                      {format(parseISO(appointment.scheduled_start), 'h:mm a')}
                    </span>
                    <span
                      className={`px-2 py-1 text-xs font-medium rounded ${getStatusColor(
                        appointment.status
                      )}`}
                    >
                      {appointment.status.replace('_', ' ').toUpperCase()}
                    </span>
                  </div>

                  <div className="space-y-1 text-sm text-gray-600">
                    <p>
                      <span className="font-medium">Customer:</span>{' '}
                      {appointment.owner?.first_name} {appointment.owner?.last_name}
                    </p>
                    <p>
                      <span className="font-medium">Pet:</span>{' '}
                      {appointment.pets?.map((p) => p.name).join(', ') || 'N/A'}
                    </p>
                    <p>
                      <span className="font-medium">Service:</span>{' '}
                      {appointment.service?.name}
                    </p>
                    {appointment.service && (
                      <p className="text-primary-600 font-semibold">
                        ${(appointment.service.price / 100).toFixed(2)}
                      </p>
                    )}
                  </div>
                </div>

                <div className="flex flex-col space-y-2 ml-4">
                  {appointment.status === 'PENDING' && (
                    <button
                      onClick={() => handleCheckIn(appointment.id)}
                      disabled={actionLoading === appointment.id}
                      className="px-3 py-1 text-sm bg-purple-600 text-white rounded hover:bg-purple-700 disabled:bg-gray-400"
                    >
                      Check In
                    </button>
                  )}
                  {appointment.status === 'CHECKED_IN' && (
                    <button
                      onClick={() => handleStart(appointment.id)}
                      disabled={actionLoading === appointment.id}
                      className="px-3 py-1 text-sm bg-orange-600 text-white rounded hover:bg-orange-700 disabled:bg-gray-400"
                    >
                      Start
                    </button>
                  )}
                  {appointment.status === 'IN_PROGRESS' && (
                    <button
                      onClick={() => handleComplete(appointment.id)}
                      disabled={actionLoading === appointment.id}
                      className="px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700 disabled:bg-gray-400"
                    >
                      Complete
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
