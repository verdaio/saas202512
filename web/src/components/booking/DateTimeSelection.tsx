'use client';

import { useState, useEffect } from 'react';
import { appointmentsApi } from '@/lib/api';
import type { Service, TimeSlot } from '@/lib/api';
import { format, addDays, parseISO } from 'date-fns';

interface Props {
  service: Service;
  onSelect: (date: string, slot: TimeSlot) => void;
  onBack: () => void;
}

export default function DateTimeSelection({ service, onSelect, onBack }: Props) {
  const [selectedDate, setSelectedDate] = useState<string>('');
  const [availableSlots, setAvailableSlots] = useState<TimeSlot[]>([]);
  const [loading, setLoading] = useState(false);
  const [dates, setDates] = useState<string[]>([]);

  useEffect(() => {
    // Generate next 14 days
    const nextDates = [];
    for (let i = 0; i < 14; i++) {
      const date = addDays(new Date(), i);
      nextDates.push(format(date, 'yyyy-MM-dd'));
    }
    setDates(nextDates);
    setSelectedDate(nextDates[0]);
  }, []);

  useEffect(() => {
    if (selectedDate) {
      fetchSlots(selectedDate);
    }
  }, [selectedDate]);

  async function fetchSlots(date: string) {
    setLoading(true);
    try {
      const slots = await appointmentsApi.getAvailableSlots(service.id, date);
      setAvailableSlots(slots);
    } catch (err) {
      console.error('Failed to fetch slots:', err);
      setAvailableSlots([]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Select Date & Time</h2>

      {/* Date Selection */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">Date</label>
        <div className="grid grid-cols-7 gap-2">
          {dates.map((date) => (
            <button
              key={date}
              onClick={() => setSelectedDate(date)}
              className={`p-2 text-center rounded-lg border ${
                selectedDate === date
                  ? 'bg-primary-600 text-white border-primary-600'
                  : 'bg-white text-gray-700 border-gray-300 hover:border-primary-400'
              }`}
            >
              <div className="text-xs">{format(parseISO(date), 'EEE')}</div>
              <div className="text-lg font-semibold">{format(parseISO(date), 'd')}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Time Slots */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">Available Times</label>
        {loading ? (
          <div className="text-center py-8">Loading available times...</div>
        ) : availableSlots.length === 0 ? (
          <div className="text-center py-8 text-gray-500">No available times for this date</div>
        ) : (
          <div className="grid grid-cols-3 gap-3">
            {availableSlots.map((slot, index) => (
              <button
                key={index}
                onClick={() => onSelect(selectedDate, slot)}
                className="p-3 text-center rounded-lg border border-gray-300 hover:border-primary-500 hover:bg-primary-50 transition-colors"
              >
                {format(parseISO(slot.start_time), 'h:mm a')}
              </button>
            ))}
          </div>
        )}
      </div>

      <button
        onClick={onBack}
        className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
      >
        Back
      </button>
    </div>
  );
}
