'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import ProtectedRoute from '@/components/staff/ProtectedRoute';
import DashboardLayout from '@/components/staff/DashboardLayout';
import { appointmentsApi, Appointment } from '@/lib/staffApi';
import { format, parseISO } from 'date-fns';

export default function AppointmentDetailPage() {
  const router = useRouter();
  const params = useParams();
  const appointmentId = params.id as string;

  const [appointment, setAppointment] = useState<Appointment | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [actionLoading, setActionLoading] = useState(false);
  const [cancelReason, setCancelReason] = useState('');
  const [showCancelModal, setShowCancelModal] = useState(false);
  const [notes, setNotes] = useState('');
  const [showNotesModal, setShowNotesModal] = useState(false);
  const [showRescheduleModal, setShowRescheduleModal] = useState(false);
  const [rescheduleDate, setRescheduleDate] = useState('');
  const [availableSlots, setAvailableSlots] = useState<any[]>([]);
  const [selectedSlot, setSelectedSlot] = useState<string>('');

  useEffect(() => {
    loadAppointment();
  }, [appointmentId]);

  const loadAppointment = async () => {
    try {
      setLoading(true);
      const data = await appointmentsApi.getById(appointmentId);
      setAppointment(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load appointment');
    } finally {
      setLoading(false);
    }
  };

  const handleCheckIn = async () => {
    if (!appointment) return;
    try {
      setActionLoading(true);
      await appointmentsApi.checkIn(appointment.id);
      await loadAppointment();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to check in');
    } finally {
      setActionLoading(false);
    }
  };

  const handleStart = async () => {
    if (!appointment) return;
    try {
      setActionLoading(true);
      await appointmentsApi.start(appointment.id);
      await loadAppointment();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to start');
    } finally {
      setActionLoading(false);
    }
  };

  const handleComplete = async () => {
    setShowNotesModal(true);
  };

  const confirmComplete = async () => {
    if (!appointment) return;
    try {
      setActionLoading(true);
      await appointmentsApi.complete(appointment.id, notes);
      setShowNotesModal(false);
      await loadAppointment();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to complete');
    } finally {
      setActionLoading(false);
    }
  };

  const handleCancel = async () => {
    setShowCancelModal(true);
  };

  const confirmCancel = async () => {
    if (!appointment) return;
    try {
      setActionLoading(true);
      await appointmentsApi.cancel(appointment.id, cancelReason);
      setShowCancelModal(false);
      await loadAppointment();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to cancel');
    } finally {
      setActionLoading(false);
    }
  };

  const handleNoShow = async () => {
    if (!appointment) return;
    if (!confirm('Mark this appointment as no-show?')) return;

    try {
      setActionLoading(true);
      await appointmentsApi.markNoShow(appointment.id);
      await loadAppointment();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to mark as no-show');
    } finally {
      setActionLoading(false);
    }
  };

  const handleReschedule = () => {
    setShowRescheduleModal(true);
  };

  const loadAvailableSlots = async () => {
    if (!appointment || !rescheduleDate) return;

    try {
      const slots = await appointmentsApi.getAvailableSlots(
        appointment.service_id,
        rescheduleDate
      );
      setAvailableSlots(slots);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to load available slots');
    }
  };

  const confirmReschedule = async () => {
    if (!appointment || !selectedSlot) return;

    try {
      setActionLoading(true);
      const slot = availableSlots.find((s) => s.start === selectedSlot);
      if (!slot) return;

      await appointmentsApi.reschedule(appointment.id, {
        scheduled_start: slot.start,
        scheduled_end: slot.end,
      });

      setShowRescheduleModal(false);
      setRescheduleDate('');
      setSelectedSlot('');
      setAvailableSlots([]);
      await loadAppointment();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to reschedule');
    } finally {
      setActionLoading(false);
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
      <ProtectedRoute>
        <DashboardLayout>
          <div className="flex items-center justify-center min-h-screen">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          </div>
        </DashboardLayout>
      </ProtectedRoute>
    );
  }

  if (error || !appointment) {
    return (
      <ProtectedRoute>
        <DashboardLayout>
          <div className="text-center py-12">
            <p className="text-red-600 text-lg">{error || 'Appointment not found'}</p>
            <button
              onClick={() => router.push('/staff/appointments')}
              className="mt-4 px-4 py-2 text-primary-600 hover:text-primary-700"
            >
              ← Back to Appointments
            </button>
          </div>
        </DashboardLayout>
      </ProtectedRoute>
    );
  }

  return (
    <ProtectedRoute>
      <DashboardLayout>
        <div className="space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => router.push('/staff/appointments')}
                className="text-gray-600 hover:text-gray-900"
              >
                ← Back
              </button>
              <h1 className="text-3xl font-bold text-gray-900">
                Appointment Details
              </h1>
            </div>
            <span
              className={`px-4 py-2 text-sm font-medium rounded-lg ${getStatusColor(
                appointment.status
              )}`}
            >
              {appointment.status.replace('_', ' ').toUpperCase()}
            </span>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Main Details */}
            <div className="lg:col-span-2 space-y-6">
              {/* Appointment Info */}
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">
                  Appointment Information
                </h2>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-600">
                      Date
                    </label>
                    <p className="text-lg text-gray-900">
                      {format(parseISO(appointment.scheduled_start), 'MMMM dd, yyyy')}
                    </p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-600">
                      Time
                    </label>
                    <p className="text-lg text-gray-900">
                      {format(parseISO(appointment.scheduled_start), 'h:mm a')} -{' '}
                      {format(parseISO(appointment.scheduled_end), 'h:mm a')}
                    </p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-600">
                      Service
                    </label>
                    <p className="text-lg text-gray-900">
                      {appointment.service?.name}
                    </p>
                    {appointment.service && (
                      <p className="text-primary-600 font-semibold mt-1">
                        ${(appointment.service.price / 100).toFixed(2)}
                      </p>
                    )}
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-600">
                      Staff Member
                    </label>
                    <p className="text-lg text-gray-900">
                      {appointment.staff
                        ? `${appointment.staff.first_name} ${appointment.staff.last_name}`
                        : 'Unassigned'}
                    </p>
                  </div>
                </div>
              </div>

              {/* Customer Info */}
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">
                  Customer Information
                </h2>
                <div className="space-y-3">
                  <div>
                    <label className="block text-sm font-medium text-gray-600">
                      Name
                    </label>
                    <p className="text-lg text-gray-900">
                      {appointment.owner?.first_name} {appointment.owner?.last_name}
                    </p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-600">
                      Phone
                    </label>
                    <p className="text-lg text-gray-900">
                      {appointment.owner?.phone}
                    </p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-600">
                      Email
                    </label>
                    <p className="text-lg text-gray-900">
                      {appointment.owner?.email}
                    </p>
                  </div>
                </div>
              </div>

              {/* Pet Info */}
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">
                  Pet Information
                </h2>
                {appointment.pets && appointment.pets.length > 0 ? (
                  <div className="space-y-4">
                    {appointment.pets.map((pet) => (
                      <div key={pet.id} className="border-b border-gray-200 pb-4 last:border-0">
                        <h3 className="text-lg font-medium text-gray-900">
                          {pet.name}
                        </h3>
                        <div className="mt-2 grid grid-cols-2 gap-4 text-sm">
                          <div>
                            <span className="text-gray-600">Species:</span>{' '}
                            <span className="text-gray-900">{pet.species}</span>
                          </div>
                          {pet.breed && (
                            <div>
                              <span className="text-gray-600">Breed:</span>{' '}
                              <span className="text-gray-900">{pet.breed}</span>
                            </div>
                          )}
                          {pet.weight && (
                            <div>
                              <span className="text-gray-600">Weight:</span>{' '}
                              <span className="text-gray-900">{pet.weight} lbs</span>
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500">No pet information available</p>
                )}
              </div>
            </div>

            {/* Actions Sidebar */}
            <div className="space-y-6">
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">
                  Actions
                </h2>
                <div className="space-y-3">
                  {appointment.status === 'PENDING' && (
                    <button
                      onClick={handleCheckIn}
                      disabled={actionLoading}
                      className="w-full px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-gray-400 transition"
                    >
                      Check In
                    </button>
                  )}

                  {appointment.status === 'CHECKED_IN' && (
                    <button
                      onClick={handleStart}
                      disabled={actionLoading}
                      className="w-full px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 disabled:bg-gray-400 transition"
                    >
                      Start Service
                    </button>
                  )}

                  {appointment.status === 'IN_PROGRESS' && (
                    <button
                      onClick={handleComplete}
                      disabled={actionLoading}
                      className="w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 transition"
                    >
                      Complete Service
                    </button>
                  )}

                  {!['COMPLETED', 'CANCELLED', 'NO_SHOW'].includes(appointment.status) && (
                    <>
                      <button
                        onClick={handleReschedule}
                        disabled={actionLoading}
                        className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition"
                      >
                        Reschedule
                      </button>

                      <button
                        onClick={handleCancel}
                        disabled={actionLoading}
                        className="w-full px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:bg-gray-400 transition"
                      >
                        Cancel Appointment
                      </button>

                      <button
                        onClick={handleNoShow}
                        disabled={actionLoading}
                        className="w-full px-4 py-2 border-2 border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 disabled:bg-gray-100 transition"
                      >
                        Mark as No-Show
                      </button>
                    </>
                  )}
                </div>
              </div>

              {/* Metadata */}
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">
                  Metadata
                </h2>
                <div className="space-y-2 text-sm">
                  <div>
                    <span className="text-gray-600">Created:</span>{' '}
                    <span className="text-gray-900">
                      {format(parseISO(appointment.created_at), 'MMM dd, yyyy h:mm a')}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-600">Updated:</span>{' '}
                    <span className="text-gray-900">
                      {format(parseISO(appointment.updated_at), 'MMM dd, yyyy h:mm a')}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-600">ID:</span>{' '}
                    <span className="text-gray-900 text-xs font-mono">
                      {appointment.id}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Cancel Modal */}
        {showCancelModal && (
          <div className="fixed inset-0 z-50 overflow-y-auto">
            <div className="flex items-center justify-center min-h-screen px-4">
              <div
                className="fixed inset-0 bg-black bg-opacity-50"
                onClick={() => setShowCancelModal(false)}
              ></div>
              <div className="relative bg-white rounded-lg p-6 max-w-md w-full">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Cancel Appointment
                </h3>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Reason for cancellation
                  </label>
                  <textarea
                    value={cancelReason}
                    onChange={(e) => setCancelReason(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    rows={3}
                    placeholder="Optional reason..."
                  />
                </div>
                <div className="flex space-x-3">
                  <button
                    onClick={confirmCancel}
                    disabled={actionLoading}
                    className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:bg-gray-400"
                  >
                    Confirm Cancel
                  </button>
                  <button
                    onClick={() => setShowCancelModal(false)}
                    disabled={actionLoading}
                    className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                  >
                    Nevermind
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Notes Modal */}
        {showNotesModal && (
          <div className="fixed inset-0 z-50 overflow-y-auto">
            <div className="flex items-center justify-center min-h-screen px-4">
              <div
                className="fixed inset-0 bg-black bg-opacity-50"
                onClick={() => setShowNotesModal(false)}
              ></div>
              <div className="relative bg-white rounded-lg p-6 max-w-md w-full">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Complete Service
                </h3>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Service notes (optional)
                  </label>
                  <textarea
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    rows={4}
                    placeholder="Any notes about the service..."
                  />
                </div>
                <div className="flex space-x-3">
                  <button
                    onClick={confirmComplete}
                    disabled={actionLoading}
                    className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400"
                  >
                    Complete
                  </button>
                  <button
                    onClick={() => setShowNotesModal(false)}
                    disabled={actionLoading}
                    className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Reschedule Modal */}
        {showRescheduleModal && (
          <div className="fixed inset-0 z-50 overflow-y-auto">
            <div className="flex items-center justify-center min-h-screen px-4">
              <div
                className="fixed inset-0 bg-black bg-opacity-50"
                onClick={() => setShowRescheduleModal(false)}
              ></div>
              <div className="relative bg-white rounded-lg p-6 max-w-md w-full">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Reschedule Appointment
                </h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Select New Date
                    </label>
                    <input
                      type="date"
                      value={rescheduleDate}
                      onChange={(e) => setRescheduleDate(e.target.value)}
                      onBlur={loadAvailableSlots}
                      min={new Date().toISOString().split('T')[0]}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    />
                  </div>

                  {availableSlots.length > 0 && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Select Time Slot
                      </label>
                      <div className="max-h-48 overflow-y-auto space-y-2">
                        {availableSlots.map((slot) => (
                          <label
                            key={slot.start}
                            className="flex items-center p-3 border border-gray-300 rounded-lg hover:bg-gray-50 cursor-pointer"
                          >
                            <input
                              type="radio"
                              name="time-slot"
                              value={slot.start}
                              checked={selectedSlot === slot.start}
                              onChange={(e) => setSelectedSlot(e.target.value)}
                              className="mr-3"
                            />
                            <span className="text-sm text-gray-900">
                              {format(parseISO(slot.start), 'h:mm a')} -{' '}
                              {format(parseISO(slot.end), 'h:mm a')}
                            </span>
                          </label>
                        ))}
                      </div>
                    </div>
                  )}

                  {rescheduleDate && availableSlots.length === 0 && (
                    <p className="text-sm text-gray-500 text-center py-4">
                      No available slots for this date
                    </p>
                  )}
                </div>

                <div className="flex space-x-3 mt-6">
                  <button
                    onClick={confirmReschedule}
                    disabled={actionLoading || !selectedSlot}
                    className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
                  >
                    Confirm
                  </button>
                  <button
                    onClick={() => {
                      setShowRescheduleModal(false);
                      setRescheduleDate('');
                      setSelectedSlot('');
                      setAvailableSlots([]);
                    }}
                    disabled={actionLoading}
                    className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </DashboardLayout>
    </ProtectedRoute>
  );
}
