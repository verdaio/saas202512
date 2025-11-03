'use client';

import { useState } from 'react';
import type { Service, TimeSlot, Owner, Pet } from '@/lib/api';
import { format, parseISO } from 'date-fns';

interface Props {
  service: Service;
  slot: TimeSlot;
  date: string;
  onSubmit: (owner: Owner, pets: Pet[]) => void;
  onBack: () => void;
  loading: boolean;
}

export default function PetOwnerForm({ service, slot, date, onSubmit, onBack, loading }: Props) {
  const [owner, setOwner] = useState<Owner>({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    address_line1: '',
    city: '',
    state: '',
    zip_code: '',
  });

  const [pets, setPets] = useState<Pet[]>([
    {
      name: '',
      species: 'dog',
      breed: '',
      weight: undefined,
    },
  ]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(owner, pets);
  };

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Your Information</h2>

      {/* Booking Summary */}
      <div className="bg-gray-50 rounded-lg p-4 mb-6">
        <h3 className="font-semibold mb-2">Booking Summary</h3>
        <p className="text-sm text-gray-600">
          {service.name} on {format(parseISO(date), 'MMMM d, yyyy')} at{' '}
          {format(parseISO(slot.start_time), 'h:mm a')}
        </p>
        <p className="text-sm text-gray-600">
          Duration: {service.duration_minutes} minutes
        </p>
        <p className="text-lg font-bold text-primary-600 mt-2">
          ${(service.price / 100).toFixed(2)}
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Owner Information */}
        <div>
          <h3 className="text-lg font-semibold mb-4">Contact Information</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                First Name *
              </label>
              <input
                type="text"
                required
                value={owner.first_name}
                onChange={(e) => setOwner({ ...owner, first_name: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Last Name *</label>
              <input
                type="text"
                required
                value={owner.last_name}
                onChange={(e) => setOwner({ ...owner, last_name: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Email *</label>
              <input
                type="email"
                required
                value={owner.email}
                onChange={(e) => setOwner({ ...owner, email: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Phone *</label>
              <input
                type="tel"
                required
                value={owner.phone}
                onChange={(e) => setOwner({ ...owner, phone: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              />
            </div>
          </div>
        </div>

        {/* Pet Information */}
        <div>
          <h3 className="text-lg font-semibold mb-4">Pet Information</h3>
          {pets.map((pet, index) => (
            <div key={index} className="mb-4 p-4 border border-gray-200 rounded-lg">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Pet Name *
                  </label>
                  <input
                    type="text"
                    required
                    value={pet.name}
                    onChange={(e) => {
                      const newPets = [...pets];
                      newPets[index].name = e.target.value;
                      setPets(newPets);
                    }}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Species *
                  </label>
                  <select
                    required
                    value={pet.species}
                    onChange={(e) => {
                      const newPets = [...pets];
                      newPets[index].species = e.target.value;
                      setPets(newPets);
                    }}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                  >
                    <option value="dog">Dog</option>
                    <option value="cat">Cat</option>
                    <option value="other">Other</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Breed</label>
                  <input
                    type="text"
                    value={pet.breed || ''}
                    onChange={(e) => {
                      const newPets = [...pets];
                      newPets[index].breed = e.target.value;
                      setPets(newPets);
                    }}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Weight (lbs)
                  </label>
                  <input
                    type="number"
                    value={pet.weight || ''}
                    onChange={(e) => {
                      const newPets = [...pets];
                      newPets[index].weight = e.target.value ? parseInt(e.target.value) : undefined;
                      setPets(newPets);
                    }}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                  />
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Actions */}
        <div className="flex gap-4">
          <button
            type="button"
            onClick={onBack}
            className="px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50"
            disabled={loading}
          >
            Back
          </button>
          <button
            type="submit"
            className="flex-1 px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:bg-gray-400"
            disabled={loading}
          >
            {loading ? 'Booking...' : 'Book Appointment'}
          </button>
        </div>
      </form>
    </div>
  );
}
