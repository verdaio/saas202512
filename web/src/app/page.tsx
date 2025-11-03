'use client';

import BookingWidget from '@/components/BookingWidget';

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-12">
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            Pet Care Booking
          </h1>
          <p className="text-xl text-gray-600">
            Book grooming and training appointments for your pets
          </p>
        </div>

        <BookingWidget />
      </div>
    </main>
  );
}
