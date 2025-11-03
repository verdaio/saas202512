'use client';

import { useState, useEffect } from 'react';
import { servicesApi, appointmentsApi, ownersApi, petsApi } from '@/lib/api';
import type { Service, TimeSlot, Owner, Pet } from '@/lib/api';
import { format, parseISO } from 'date-fns';

// Step components
import ServiceSelection from './booking/ServiceSelection';
import DateTimeSelection from './booking/DateTimeSelection';
import PetOwnerForm from './booking/PetOwnerForm';
import ConfirmationStep from './booking/ConfirmationStep';

type BookingStep = 'service' | 'datetime' | 'details' | 'confirmation';

export default function BookingWidget() {
  const [currentStep, setCurrentStep] = useState<BookingStep>('service');
  const [selectedService, setSelectedService] = useState<Service | null>(null);
  const [selectedSlot, setSelectedSlot] = useState<TimeSlot | null>(null);
  const [selectedDate, setSelectedDate] = useState<string>('');
  const [ownerData, setOwnerData] = useState<Owner | null>(null);
  const [petData, setPetData] = useState<Pet[]>([]);
  const [appointmentId, setAppointmentId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleServiceSelect = (service: Service) => {
    setSelectedService(service);
    setCurrentStep('datetime');
  };

  const handleDateTimeSelect = (date: string, slot: TimeSlot) => {
    setSelectedDate(date);
    setSelectedSlot(slot);
    setCurrentStep('details');
  };

  const handleDetailsSubmit = async (owner: Owner, pets: Pet[]) => {
    setLoading(true);
    setError(null);

    try {
      // Create or get owner
      let ownerId: string;
      const existingOwners = await ownersApi.searchOwners(owner.email);

      if (existingOwners.length > 0) {
        ownerId = existingOwners[0].id;
      } else {
        const newOwner = await ownersApi.createOwner(owner);
        ownerId = newOwner.id;
      }

      // Create pets
      const petIds: string[] = [];
      for (const pet of pets) {
        const newPet = await petsApi.createPet(ownerId, pet);
        petIds.push(newPet.id);
      }

      // Create appointment
      if (!selectedService || !selectedSlot) {
        throw new Error('Missing service or time slot');
      }

      const appointment = await appointmentsApi.createAppointment({
        owner_id: ownerId,
        pet_ids: petIds,
        service_id: selectedService.id,
        scheduled_start: selectedSlot.start_time,
        scheduled_end: selectedSlot.end_time,
        customer_notes: '',
      });

      setAppointmentId(appointment.id);
      setOwnerData(owner);
      setPetData(pets);
      setCurrentStep('confirmation');
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to create appointment');
      console.error('Booking error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleBack = () => {
    if (currentStep === 'datetime') {
      setCurrentStep('service');
    } else if (currentStep === 'details') {
      setCurrentStep('datetime');
    }
  };

  const handleStartOver = () => {
    setCurrentStep('service');
    setSelectedService(null);
    setSelectedSlot(null);
    setSelectedDate('');
    setOwnerData(null);
    setPetData([]);
    setAppointmentId(null);
    setError(null);
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white rounded-lg shadow-2xl overflow-hidden">
        {/* Progress Bar */}
        <div className="bg-primary-600 p-6">
          <div className="flex justify-between items-center text-white">
            <Step
              number={1}
              title="Service"
              active={currentStep === 'service'}
              completed={currentStep !== 'service'}
            />
            <div className="flex-1 h-1 bg-primary-400 mx-4"></div>
            <Step
              number={2}
              title="Date & Time"
              active={currentStep === 'datetime'}
              completed={currentStep === 'details' || currentStep === 'confirmation'}
            />
            <div className="flex-1 h-1 bg-primary-400 mx-4"></div>
            <Step
              number={3}
              title="Your Info"
              active={currentStep === 'details'}
              completed={currentStep === 'confirmation'}
            />
            <div className="flex-1 h-1 bg-primary-400 mx-4"></div>
            <Step number={4} title="Confirm" active={currentStep === 'confirmation'} />
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border-l-4 border-red-400 p-4 mx-6 mt-6">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg
                  className="h-5 w-5 text-red-400"
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                    clipRule="evenodd"
                  />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-red-700">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Content */}
        <div className="p-6">
          {currentStep === 'service' && <ServiceSelection onSelect={handleServiceSelect} />}

          {currentStep === 'datetime' && selectedService && (
            <DateTimeSelection
              service={selectedService}
              onSelect={handleDateTimeSelect}
              onBack={handleBack}
            />
          )}

          {currentStep === 'details' && selectedService && selectedSlot && (
            <PetOwnerForm
              service={selectedService}
              slot={selectedSlot}
              date={selectedDate}
              onSubmit={handleDetailsSubmit}
              onBack={handleBack}
              loading={loading}
            />
          )}

          {currentStep === 'confirmation' && selectedService && ownerData && (
            <ConfirmationStep
              appointmentId={appointmentId!}
              service={selectedService}
              date={selectedDate}
              slot={selectedSlot!}
              owner={ownerData}
              pets={petData}
              onStartOver={handleStartOver}
            />
          )}
        </div>
      </div>
    </div>
  );
}

// Progress Step Component
function Step({
  number,
  title,
  active,
  completed,
}: {
  number: number;
  title: string;
  active?: boolean;
  completed?: boolean;
}) {
  return (
    <div className="flex flex-col items-center">
      <div
        className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold ${
          active
            ? 'bg-white text-primary-600'
            : completed
            ? 'bg-primary-300 text-white'
            : 'bg-primary-500 text-white'
        }`}
      >
        {completed ? '✓' : number}
      </div>
      <span className="text-xs mt-1">{title}</span>
    </div>
  );
}
