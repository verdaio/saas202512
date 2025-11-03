'use client';

import { useState, useEffect } from 'react';
import { servicesApi } from '@/lib/api';
import type { Service } from '@/lib/api';

interface Props {
  onSelect: (service: Service) => void;
}

export default function ServiceSelection({ onSelect }: Props) {
  const [services, setServices] = useState<Service[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchServices() {
      try {
        const data = await servicesApi.getServices();
        setServices(data);
      } catch (err: any) {
        setError('Failed to load services');
        console.error(err);
      } finally {
        setLoading(false);
      }
    }

    fetchServices();
  }, []);

  if (loading) {
    return <div className="text-center py-12">Loading services...</div>;
  }

  if (error) {
    return <div className="text-center py-12 text-red-600">{error}</div>;
  }

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Select a Service</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {services.map((service) => (
          <div
            key={service.id}
            onClick={() => onSelect(service)}
            className="border border-gray-200 rounded-lg p-6 hover:border-primary-500 hover:shadow-lg cursor-pointer transition-all"
          >
            <h3 className="text-xl font-semibold text-gray-900 mb-2">{service.name}</h3>
            <p className="text-gray-600 mb-4">{service.description}</p>
            <div className="flex justify-between items-center">
              <span className="text-2xl font-bold text-primary-600">
                ${(service.price / 100).toFixed(2)}
              </span>
              <span className="text-sm text-gray-500">{service.duration_minutes} min</span>
            </div>
            {service.category && (
              <div className="mt-3">
                <span className="inline-block bg-primary-100 text-primary-800 text-xs px-2 py-1 rounded">
                  {service.category}
                </span>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
