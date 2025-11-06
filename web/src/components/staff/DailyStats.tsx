'use client';

import { useState, useEffect } from 'react';
import { statsApi, DailyStats as DailyStatsType } from '@/lib/staffApi';

export default function DailyStats() {
  const [stats, setStats] = useState<DailyStatsType | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      setLoading(true);
      const data = await statsApi.getDailyStats();
      setStats(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load stats');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="bg-white rounded-lg shadow p-6">
            <div className="animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
              <div className="h-8 bg-gray-200 rounded w-3/4"></div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-600">{error}</p>
      </div>
    );
  }

  if (!stats) {
    return null;
  }

  const statCards = [
    {
      label: 'Total Appointments',
      value: stats.total_appointments,
      icon: '📅',
      color: 'blue',
    },
    {
      label: 'Completed',
      value: stats.completed,
      icon: '✅',
      color: 'green',
    },
    {
      label: 'Pending',
      value: stats.pending,
      icon: '⏳',
      color: 'yellow',
    },
    {
      label: 'Revenue',
      value: `$${(stats.revenue / 100).toFixed(2)}`,
      icon: '💰',
      color: 'primary',
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {statCards.map((card) => (
        <div
          key={card.label}
          className="bg-white rounded-lg shadow p-6 hover:shadow-md transition"
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-2xl">{card.icon}</span>
            <button
              onClick={loadStats}
              className="text-gray-400 hover:text-gray-600 text-sm"
            >
              ↻
            </button>
          </div>
          <p className="text-sm text-gray-600 font-medium">{card.label}</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{card.value}</p>
        </div>
      ))}

      {(stats.cancelled > 0 || stats.no_shows > 0) && (
        <div className="col-span-full bg-orange-50 border border-orange-200 rounded-lg p-4">
          <div className="flex items-center space-x-6">
            {stats.cancelled > 0 && (
              <div>
                <span className="text-sm text-orange-700 font-medium">
                  Cancelled: {stats.cancelled}
                </span>
              </div>
            )}
            {stats.no_shows > 0 && (
              <div>
                <span className="text-sm text-orange-700 font-medium">
                  No-Shows: {stats.no_shows}
                </span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
