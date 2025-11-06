'use client';

import { useState, useEffect } from 'react';
import ProtectedRoute from '@/components/staff/ProtectedRoute';
import DashboardLayout from '@/components/staff/DashboardLayout';
import { appointmentsApi, Appointment } from '@/lib/staffApi';
import { format, parseISO } from 'date-fns';

export default function AppointmentsPage() {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Filters
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState<string>('');

  // Bulk actions
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [bulkActionLoading, setBulkActionLoading] = useState(false);

  useEffect(() => {
    loadAppointments();
  }, [statusFilter, startDate, endDate]);

  const loadAppointments = async () => {
    try {
      setLoading(true);
      let data: Appointment[];

      if (startDate && endDate) {
        data = await appointmentsApi.getByDateRange(startDate, endDate);
      } else {
        data = await appointmentsApi.getToday();
      }

      // Apply filters
      let filtered = data;

      if (statusFilter) {
        filtered = filtered.filter(a => a.status === statusFilter);
      }

      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        filtered = filtered.filter(a => {
          const ownerName = `${a.owner?.first_name} ${a.owner?.last_name}`.toLowerCase();
          const ownerPhone = a.owner?.phone?.toLowerCase() || '';
          const petNames = a.pets?.map(p => p.name.toLowerCase()).join(' ') || '';

          return ownerName.includes(query) ||
                 ownerPhone.includes(query) ||
                 petNames.includes(query);
        });
      }

      setAppointments(filtered);
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

  const exportToCSV = () => {
    const headers = ['Date', 'Time', 'Customer', 'Pet', 'Service', 'Status', 'Staff'];
    const rows = appointments.map(a => [
      format(parseISO(a.scheduled_start), 'yyyy-MM-dd'),
      format(parseISO(a.scheduled_start), 'h:mm a'),
      `${a.owner?.first_name} ${a.owner?.last_name}`,
      a.pets?.map(p => p.name).join(', ') || 'N/A',
      a.service?.name || 'N/A',
      a.status,
      a.staff ? `${a.staff.first_name} ${a.staff.last_name}` : 'Unassigned'
    ]);

    const csv = [headers, ...rows].map(row => row.join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `appointments-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
  };

  const toggleSelectAll = () => {
    if (selectedIds.size === appointments.length) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(appointments.map(a => a.id)));
    }
  };

  const toggleSelect = (id: string) => {
    const newSelected = new Set(selectedIds);
    if (newSelected.has(id)) {
      newSelected.delete(id);
    } else {
      newSelected.add(id);
    }
    setSelectedIds(newSelected);
  };

  const handleBulkCheckIn = async () => {
    if (selectedIds.size === 0) return;
    if (!confirm(`Check in ${selectedIds.size} appointment(s)?`)) return;

    setBulkActionLoading(true);
    let successCount = 0;
    for (const id of Array.from(selectedIds)) {
      try {
        await appointmentsApi.checkIn(id);
        successCount++;
      } catch (err) {
        console.error(`Failed to check in ${id}`, err);
      }
    }

    alert(`Successfully checked in ${successCount} of ${selectedIds.size} appointments`);
    setSelectedIds(new Set());
    await loadAppointments();
    setBulkActionLoading(false);
  };

  const handleBulkExport = () => {
    if (selectedIds.size === 0) return;

    const selected = appointments.filter(a => selectedIds.has(a.id));
    const headers = ['Date', 'Time', 'Customer', 'Pet', 'Service', 'Status', 'Staff'];
    const rows = selected.map(a => [
      format(parseISO(a.scheduled_start), 'yyyy-MM-dd'),
      format(parseISO(a.scheduled_start), 'h:mm a'),
      `${a.owner?.first_name} ${a.owner?.last_name}`,
      a.pets?.map(p => p.name).join(', ') || 'N/A',
      a.service?.name || 'N/A',
      a.status,
      a.staff ? `${a.staff.first_name} ${a.staff.last_name}` : 'Unassigned'
    ]);

    const csv = [headers, ...rows].map(row => row.join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `selected-appointments-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
  };

  return (
    <ProtectedRoute>
      <DashboardLayout>
        <div className="space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between">
            <h1 className="text-3xl font-bold text-gray-900">Appointments</h1>
            <div className="flex items-center space-x-3">
              {selectedIds.size > 0 && (
                <>
                  <span className="text-sm text-gray-600">
                    {selectedIds.size} selected
                  </span>
                  <button
                    onClick={handleBulkCheckIn}
                    disabled={bulkActionLoading}
                    className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-gray-400 transition"
                  >
                    Bulk Check-In
                  </button>
                  <button
                    onClick={handleBulkExport}
                    disabled={bulkActionLoading}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition"
                  >
                    Export Selected
                  </button>
                </>
              )}
              <button
                onClick={exportToCSV}
                className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition"
              >
                Export All
              </button>
            </div>
          </div>

          {/* Filters */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Filters</h2>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              {/* Search */}
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Search
                </label>
                <input
                  type="text"
                  placeholder="Customer name, pet name, phone..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onBlur={loadAppointments}
                  onKeyDown={(e) => e.key === 'Enter' && loadAppointments()}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>

              {/* Status Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Status
                </label>
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                >
                  <option value="">All Statuses</option>
                  <option value="PENDING">Pending</option>
                  <option value="CONFIRMED">Confirmed</option>
                  <option value="CHECKED_IN">Checked In</option>
                  <option value="IN_PROGRESS">In Progress</option>
                  <option value="COMPLETED">Completed</option>
                  <option value="CANCELLED">Cancelled</option>
                  <option value="NO_SHOW">No Show</option>
                </select>
              </div>

              {/* Date Range */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Start Date
                </label>
                <input
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  End Date
                </label>
                <input
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>
            </div>

            <div className="mt-4 flex items-center space-x-4">
              <button
                onClick={loadAppointments}
                className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition"
              >
                Apply Filters
              </button>
              <button
                onClick={() => {
                  setStatusFilter('');
                  setStartDate('');
                  setEndDate('');
                  setSearchQuery('');
                }}
                className="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
              >
                Clear Filters
              </button>
            </div>
          </div>

          {/* Results */}
          <div className="bg-white rounded-lg shadow">
            {loading ? (
              <div className="p-8 text-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
              </div>
            ) : error ? (
              <div className="p-8 text-center text-red-600">{error}</div>
            ) : appointments.length === 0 ? (
              <div className="p-8 text-center text-gray-500">
                No appointments found
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50 border-b border-gray-200">
                    <tr>
                      <th className="px-6 py-3 text-left">
                        <input
                          type="checkbox"
                          checked={selectedIds.size === appointments.length && appointments.length > 0}
                          onChange={toggleSelectAll}
                          className="rounded border-gray-300"
                        />
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Date & Time
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Customer
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Pet
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Service
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Staff
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {appointments.map((appointment) => (
                      <tr key={appointment.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <input
                            type="checkbox"
                            checked={selectedIds.has(appointment.id)}
                            onChange={() => toggleSelect(appointment.id)}
                            className="rounded border-gray-300"
                          />
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">
                            {format(parseISO(appointment.scheduled_start), 'MMM dd, yyyy')}
                          </div>
                          <div className="text-sm text-gray-500">
                            {format(parseISO(appointment.scheduled_start), 'h:mm a')}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">
                            {appointment.owner?.first_name} {appointment.owner?.last_name}
                          </div>
                          <div className="text-sm text-gray-500">
                            {appointment.owner?.phone}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {appointment.pets?.map((p) => p.name).join(', ') || 'N/A'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {appointment.service?.name}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span
                            className={`px-2 py-1 text-xs font-medium rounded ${getStatusColor(
                              appointment.status
                            )}`}
                          >
                            {appointment.status.replace('_', ' ')}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {appointment.staff
                            ? `${appointment.staff.first_name} ${appointment.staff.last_name}`
                            : 'Unassigned'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                          <a
                            href={`/staff/appointments/${appointment.id}`}
                            className="text-primary-600 hover:text-primary-900"
                          >
                            View
                          </a>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* Results count */}
          {!loading && appointments.length > 0 && (
            <div className="text-sm text-gray-600 text-center">
              Showing {appointments.length} appointment{appointments.length !== 1 ? 's' : ''}
            </div>
          )}
        </div>
      </DashboardLayout>
    </ProtectedRoute>
  );
}
