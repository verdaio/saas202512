/**
 * API client for Pet Care booking system
 */
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5410';
const API_VERSION = process.env.NEXT_PUBLIC_API_VERSION || 'v1';

const api = axios.create({
  baseURL: `${API_URL}/api/${API_VERSION}`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types
export interface Service {
  id: string;
  name: string;
  description: string;
  category: string;
  price: number;
  duration_minutes: number;
  setup_buffer_minutes: number;
  cleanup_buffer_minutes: number;
  requires_vaccination: boolean;
}

export interface TimeSlot {
  start_time: string;
  end_time: string;
  staff_ids: string[];
  duration_minutes: number;
}

export interface Owner {
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  address_line1?: string;
  city?: string;
  state?: string;
  zip_code?: string;
}

export interface Pet {
  name: string;
  species: string;
  breed?: string;
  weight?: number;
  temperament?: string;
}

export interface Appointment {
  owner_id: string;
  pet_ids: string[];
  service_id: string;
  staff_id?: string;
  scheduled_start: string;
  scheduled_end: string;
  customer_notes?: string;
}

// API Methods
export const servicesApi = {
  /**
   * Get all available services
   */
  async getServices(): Promise<Service[]> {
    const response = await api.get<Service[]>('/services', {
      params: {
        is_active: true,
        is_bookable_online: true,
      },
    });
    return response.data;
  },

  /**
   * Get a specific service by ID
   */
  async getService(serviceId: string): Promise<Service> {
    const response = await api.get<Service>(`/services/${serviceId}`);
    return response.data;
  },
};

export const appointmentsApi = {
  /**
   * Get available time slots for a service on a date
   */
  async getAvailableSlots(
    serviceId: string,
    date: string,
    staffId?: string
  ): Promise<TimeSlot[]> {
    const response = await api.get<TimeSlot[]>('/appointments/availability/slots', {
      params: {
        service_id: serviceId,
        date,
        staff_id: staffId,
      },
    });
    return response.data;
  },

  /**
   * Find next available slot for a service
   */
  async getNextAvailableSlot(
    serviceId: string,
    startDate: string,
    staffId?: string
  ): Promise<TimeSlot> {
    const response = await api.get<TimeSlot>('/appointments/availability/next', {
      params: {
        service_id: serviceId,
        start_date: startDate,
        staff_id: staffId,
      },
    });
    return response.data;
  },

  /**
   * Create a new appointment
   */
  async createAppointment(appointment: Appointment): Promise<any> {
    const response = await api.post('/appointments', appointment);
    return response.data;
  },
};

export const ownersApi = {
  /**
   * Create a new owner
   */
  async createOwner(owner: Owner): Promise<any> {
    const response = await api.post('/owners', owner);
    return response.data;
  },

  /**
   * Search for owner by email
   */
  async searchOwners(email: string): Promise<any[]> {
    const response = await api.get('/owners', {
      params: {
        search: email,
        limit: 1,
      },
    });
    return response.data;
  },
};

export const petsApi = {
  /**
   * Create a new pet
   */
  async createPet(ownerId: string, pet: Pet): Promise<any> {
    const response = await api.post('/pets', {
      owner_id: ownerId,
      ...pet,
    });
    return response.data;
  },

  /**
   * Get pets by owner
   */
  async getPetsByOwner(ownerId: string): Promise<any[]> {
    const response = await api.get('/pets', {
      params: {
        owner_id: ownerId,
      },
    });
    return response.data;
  },
};

export default api;
