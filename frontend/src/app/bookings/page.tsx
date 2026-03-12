'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import toast from 'react-hot-toast';
import { Plus, Calendar, Clock, MapPin } from 'lucide-react';
import Layout from '@/components/Layout';
import { Card, CardContent, CardHeader } from '@/components/Card';
import Button from '@/components/Button';
import { bookingsApi, roomsApi } from '@/lib/api';
import { Booking, Room } from '@/types';

export default function BookingsPage() {
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [rooms, setRooms] = useState<Room[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'active' | 'canceled'>('all');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [bookingsData, roomsData] = await Promise.all([
          bookingsApi.listMy(),
          roomsApi.list(),
        ]);
        setBookings(bookingsData);
        setRooms(roomsData);
      } catch (error) {
        toast.error('Erro ao carregar reservas');
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, []);

  const getRoomName = (roomId: number) => {
    const room = rooms.find((r) => r.id === roomId);
    return room?.name || 'Sala desconhecida';
  };

  const filteredBookings = bookings.filter((booking) => {
    if (filter === 'all') return true;
    return booking.status === filter;
  });

  if (isLoading) {
    return (
      <Layout>
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Minhas Reservas</h1>
            <p className="text-gray-600">Gerencie suas reservas de salas</p>
          </div>
          <Link href="/bookings/new">
            <Button>
              <Plus className="w-4 h-4 mr-2" />
              Nova Reserva
            </Button>
          </Link>
        </div>

        {/* Filter */}
        <div className="flex space-x-2">
          <Button
            variant={filter === 'all' ? 'primary' : 'secondary'}
            size="sm"
            onClick={() => setFilter('all')}
          >
            Todas
          </Button>
          <Button
            variant={filter === 'active' ? 'primary' : 'secondary'}
            size="sm"
            onClick={() => setFilter('active')}
          >
            Ativas
          </Button>
          <Button
            variant={filter === 'canceled' ? 'primary' : 'secondary'}
            size="sm"
            onClick={() => setFilter('canceled')}
          >
            Canceladas
          </Button>
        </div>

        {filteredBookings.length === 0 ? (
          <Card>
            <CardContent className="text-center py-12">
              <Calendar className="w-12 h-12 mx-auto text-gray-400" />
              <p className="mt-4 text-gray-600">Nenhuma reserva encontrada</p>
              <Link href="/bookings/new">
                <Button className="mt-4">Criar primeira reserva</Button>
              </Link>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-4">
            {filteredBookings.map((booking) => (
              <Card key={booking.id}>
                <CardContent>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2">
                        <h3 className="text-lg font-semibold">{booking.title}</h3>
                        <span
                          className={`px-2 py-0.5 text-xs rounded-full ${
                            booking.status === 'active'
                              ? 'bg-green-100 text-green-800'
                              : 'bg-red-100 text-red-800'
                          }`}
                        >
                          {booking.status === 'active' ? 'Ativa' : 'Cancelada'}
                        </span>
                      </div>
                      <div className="mt-2 space-y-1 text-sm text-gray-600">
                        <div className="flex items-center">
                          <MapPin className="w-4 h-4 mr-2" />
                          {getRoomName(booking.room_id)}
                        </div>
                        <div className="flex items-center">
                          <Calendar className="w-4 h-4 mr-2" />
                          {format(new Date(booking.start_at), "dd 'de' MMMM 'de' yyyy", {
                            locale: ptBR,
                          })}
                        </div>
                        <div className="flex items-center">
                          <Clock className="w-4 h-4 mr-2" />
                          {format(new Date(booking.start_at), 'HH:mm')} -{' '}
                          {format(new Date(booking.end_at), 'HH:mm')}
                        </div>
                      </div>
                    </div>
                    <Link href={`/bookings/${booking.id}`}>
                      <Button variant="ghost" size="sm">
                        Ver detalhes
                      </Button>
                    </Link>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </Layout>
  );
}
