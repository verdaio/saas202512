/**
 * Staff API Client
 * Authenticated API calls for staff dashboard
 */

import axios, { AxiosInstance } from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8012';
const API_VERSION = process.env.NEXT_PUBLIC_API_VERSION || 'v1';

// Create authenticated axios instance
const createAuthClient = (): AxiosInstance => {
  const client = axios.create({
    baseURL: `${API_URL}/api/${API_VERSION}`,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  // Add auth token to requests
  client.interceptors.request.use((config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  });

  // Handle 401 responses
  client.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.response?.status === 401) {
        // Token expired or invalid
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/staff/login';
      }
      return Promise.reject(error);
    }
  );

  return client;
};

const authApi = createAuthClient();

// Types
export interface Appointment {
  id: string;
  owner_id: string;
  pet_ids: string[];
  service_id: string;
  staff_id?: string;
  scheduled_start: string;
  scheduled_end: string;
  status: string;
  created_at: string;
  updated_at: string;
  owner?: Owner;
  pets?: Pet[];
  service?: Service;
  staff?: Staff;
}

export interface Owner {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
}

export interface Pet {
  id: string;
  name: string;
  species: string;
  breed?: string;
  weight?: number;
}

export interface Service {
  id: string;
  name: string;
  description?: string;
  category: string;
  price: number;
  duration_minutes: number;
}

export interface Staff {
  id: string;
  first_name: string;
  last_name: string;
  title?: string;
}

export interface DailyStats {
  total_appointments: number;
  completed: number;
  pending: number;
  cancelled: number;
  no_shows: number;
  revenue: number;
}

// Appointments API
export const appointmentsApi = {
  async getToday(): Promise<Appointment[]> {
    const today = new Date().toISOString().split('T')[0];
    const response = await authApi.get<Appointment[]>('/appointments', {
      params: { date: today },
    });
    return response.data;
  },

  async getByDateRange(startDate: string, endDate: string): Promise<Appointment[]> {
    const response = await authApi.get<Appointment[]>('/appointments', {
      params: { start_date: startDate, end_date: endDate },
    });
    return response.data;
  },

  async getById(id: string): Promise<Appointment> {
    const response = await authApi.get<Appointment>(`/appointments/${id}`);
    return response.data;
  },

  async checkIn(id: string): Promise<Appointment> {
    const response = await authApi.patch<Appointment>(`/appointments/${id}/check-in`);
    return response.data;
  },

  async start(id: string): Promise<Appointment> {
    const response = await authApi.patch<Appointment>(`/appointments/${id}/start`);
    return response.data;
  },

  async complete(id: string, notes?: string): Promise<Appointment> {
    const response = await authApi.patch<Appointment>(`/appointments/${id}/complete`, {
      notes,
    });
    return response.data;
  },

  async cancel(id: string, reason: string): Promise<Appointment> {
    const response = await authApi.patch<Appointment>(`/appointments/${id}/cancel`, {
      reason,
    });
    return response.data;
  },

  async markNoShow(id: string): Promise<Appointment> {
    const response = await authApi.patch<Appointment>(`/appointments/${id}/no-show`);
    return response.data;
  },

  async reschedule(
    id: string,
    data: { scheduled_start: string; scheduled_end: string; staff_id?: string }
  ): Promise<Appointment> {
    const response = await authApi.patch<Appointment>(`/appointments/${id}/reschedule`, data);
    return response.data;
  },

  async getAvailableSlots(serviceId: string, date: string): Promise<any[]> {
    const response = await authApi.get(`/appointments/availability/slots`, {
      params: { service_id: serviceId, date },
    });
    return response.data;
  },
};

// Stats API
export const statsApi = {
  async getDailyStats(date?: string): Promise<DailyStats> {
    const targetDate = date || new Date().toISOString().split('T')[0];
    const response = await authApi.get<DailyStats>('/stats/daily', {
      params: { date: targetDate },
    });
    return response.data;
  },
};

// Auth helpers
export const authHelpers = {
  isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token');
  },

  getUserName(): string {
    return localStorage.getItem('user_name') || 'User';
  },

  getUserRole(): string {
    return localStorage.getItem('user_role') || '';
  },

  logout(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_name');
    localStorage.removeItem('user_role');
    window.location.href = '/staff/login';
  },
};
