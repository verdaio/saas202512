'use client';

import { useState } from 'react';
import ProtectedRoute from '@/components/staff/ProtectedRoute';
import DashboardLayout from '@/components/staff/DashboardLayout';
import DailyStats from '@/components/staff/DailyStats';
import TodayAppointments from '@/components/staff/TodayAppointments';
import UpcomingAppointments from '@/components/staff/UpcomingAppointments';

export default function StaffDashboardPage() {
  const [refreshKey, setRefreshKey] = useState(0);

  const handleRefresh = () => {
    setRefreshKey((prev) => prev + 1);
  };

  return (
    <ProtectedRoute>
      <DashboardLayout>
        <div className="space-y-6">
          {/* Page Header */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
              <p className="text-gray-600 mt-1">
                Welcome back! Here's what's happening today.
              </p>
            </div>
            <button
              onClick={handleRefresh}
              className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition"
            >
              Refresh All
            </button>
          </div>

          {/* Daily Stats */}
          <DailyStats key={`stats-${refreshKey}`} />

          {/* Today's Appointments */}
          <TodayAppointments
            key={`appointments-${refreshKey}`}
            onAction={handleRefresh}
          />

          {/* Upcoming Appointments */}
          <UpcomingAppointments key={`upcoming-${refreshKey}`} />

          {/* Quick Links */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Quick Actions
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <a
                href="/staff/appointments"
                className="flex items-center p-4 border-2 border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition"
              >
                <span className="text-3xl mr-4">📅</span>
                <div>
                  <h3 className="font-semibold text-gray-900">
                    View All Appointments
                  </h3>
                  <p className="text-sm text-gray-600">
                    See complete appointment list
                  </p>
                </div>
              </a>

              <a
                href="/staff/calendar"
                className="flex items-center p-4 border-2 border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition"
              >
                <span className="text-3xl mr-4">🗓️</span>
                <div>
                  <h3 className="font-semibold text-gray-900">Open Calendar</h3>
                  <p className="text-sm text-gray-600">
                    Day, week, and month views
                  </p>
                </div>
              </a>

              <a
                href="/staff/customers"
                className="flex items-center p-4 border-2 border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition"
              >
                <span className="text-3xl mr-4">👥</span>
                <div>
                  <h3 className="font-semibold text-gray-900">
                    Manage Customers
                  </h3>
                  <p className="text-sm text-gray-600">
                    View and edit customer info
                  </p>
                </div>
              </a>
            </div>
          </div>
        </div>
      </DashboardLayout>
    </ProtectedRoute>
  );
}
