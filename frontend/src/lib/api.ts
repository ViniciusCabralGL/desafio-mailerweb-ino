import axios, { AxiosError } from 'axios';
import { AuthToken, Room, Booking, BookingCreate, BookingUpdate, User, ApiError } from '@/types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiError>) => {
    if (error.response?.status === 401) {
      if (typeof window !== 'undefined') {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// Auth
export const authApi = {
  login: async (email: string, password: string): Promise<AuthToken> => {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const response = await api.post<AuthToken>('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    return response.data;
  },

  register: async (email: string, name: string, password: string): Promise<User> => {
    const response = await api.post<User>('/auth/register', { email, name, password });
    return response.data;
  },

  me: async (): Promise<User> => {
    const response = await api.get<User>('/auth/me');
    return response.data;
  },
};

// Rooms
export const roomsApi = {
  list: async (): Promise<Room[]> => {
    const response = await api.get<Room[]>('/rooms/');
    return response.data;
  },

  get: async (id: number): Promise<Room> => {
    const response = await api.get<Room>(`/rooms/${id}`);
    return response.data;
  },

  create: async (data: { name: string; capacity: number; description?: string }): Promise<Room> => {
    const response = await api.post<Room>('/rooms/', data);
    return response.data;
  },
};

// Bookings
export const bookingsApi = {
  list: async (roomId?: number, status?: string): Promise<Booking[]> => {
    const params = new URLSearchParams();
    if (roomId) params.append('room_id', roomId.toString());
    if (status) params.append('status', status);

    const response = await api.get<Booking[]>(`/bookings/?${params.toString()}`);
    return response.data;
  },

  listMy: async (status?: string): Promise<Booking[]> => {
    const params = new URLSearchParams();
    if (status) params.append('status', status);

    const response = await api.get<Booking[]>(`/bookings/my?${params.toString()}`);
    return response.data;
  },

  get: async (id: number): Promise<Booking> => {
    const response = await api.get<Booking>(`/bookings/${id}`);
    return response.data;
  },

  create: async (data: BookingCreate): Promise<Booking> => {
    const response = await api.post<Booking>('/bookings/', data);
    return response.data;
  },

  update: async (id: number, data: BookingUpdate): Promise<Booking> => {
    const response = await api.put<Booking>(`/bookings/${id}`, data);
    return response.data;
  },

  cancel: async (id: number): Promise<Booking> => {
    const response = await api.post<Booking>(`/bookings/${id}/cancel`);
    return response.data;
  },
};

export default api;
