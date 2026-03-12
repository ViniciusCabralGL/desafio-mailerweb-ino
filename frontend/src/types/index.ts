export interface User {
  id: number;
  email: string;
  name: string;
  is_active: boolean;
  created_at: string;
}

export interface Room {
  id: number;
  name: string;
  capacity: number;
  description: string | null;
  created_at: string;
  updated_at: string;
}

export interface Participant {
  id: number;
  email: string;
  user_id: number | null;
}

export type BookingStatus = 'active' | 'canceled';

export interface Booking {
  id: number;
  title: string;
  room_id: number;
  owner_id: number;
  start_at: string;
  end_at: string;
  status: BookingStatus;
  participants: Participant[];
  created_at: string;
  updated_at: string;
}

export interface BookingCreate {
  title: string;
  room_id: number;
  start_at: string;
  end_at: string;
  participants: { email: string }[];
}

export interface BookingUpdate {
  title?: string;
  room_id?: number;
  start_at?: string;
  end_at?: string;
  participants?: { email: string }[];
}

export interface AuthToken {
  access_token: string;
  token_type: string;
  user: User;
}

export interface ApiError {
  detail: string;
}
