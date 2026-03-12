'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import { Calendar, Users, Clock, Plus } from 'lucide-react';
import toast from 'react-hot-toast';
import Layout from '@/components/Layout';
import { Card, CardContent, CardHeader } from '@/components/Card';
import Button from '@/components/Button';
import { bookingsApi, roomsApi } from '@/lib/api';
import { Booking, Room } from '@/types';

export default function HomePage() {
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [rooms, setRooms] = useState<Room[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [bookingsData, roomsData] = await Promise.all([
          bookingsApi.listMy('active'),
          roomsApi.list(),
        ]);
        setBookings(bookingsData.slice(0, 5));
        setRooms(roomsData);
      } catch (error) {
        toast.error('Erro ao carregar dados');
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
        {/* Welcome */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
            <p className="text-gray-600">Gerencie suas reservas de salas</p>
          </div>
          <Link href="/bookings/new">
            <Button>
              <Plus className="w-4 h-4 mr-2" />
              Nova Reserva
            </Button>
          </Link>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card>
            <CardContent className="flex items-center space-x-4">
              <div className="p-3 bg-primary-100 rounded-lg">
                <Calendar className="w-6 h-6 text-primary-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Minhas Reservas</p>
                <p className="text-2xl font-bold">{bookings.length}</p>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="flex items-center space-x-4">
              <div className="p-3 bg-green-100 rounded-lg">
                <Users className="w-6 h-6 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Salas Disponíveis</p>
                <p className="text-2xl font-bold">{rooms.length}</p>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="flex items-center space-x-4">
              <div className="p-3 bg-purple-100 rounded-lg">
                <Clock className="w-6 h-6 text-purple-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Reservas Ativas</p>
                <p className="text-2xl font-bold">
                  {bookings.filter((b) => b.status === 'active').length}
                </p>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Recent Bookings */}
        <Card>
          <CardHeader>
            <div className="flex justify-between items-center">
              <h2 className="text-lg font-semibold">Próximas Reservas</h2>
              <Link href="/bookings" className="text-sm text-primary-600 hover:underline">
                Ver todas
              </Link>
            </div>
          </CardHeader>
          <CardContent>
            {bookings.length === 0 ? (
              <p className="text-gray-500 text-center py-4">
                Você não tem reservas ativas.
              </p>
            ) : (
              <div className="space-y-3">
                {bookings.map((booking) => (
                  <div
                    key={booking.id}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                  >
                    <div>
                      <p className="font-medium">{booking.title}</p>
                      <p className="text-sm text-gray-600">
                        {getRoomName(booking.room_id)} -{' '}
                        {format(new Date(booking.start_at), "dd/MM 'às' HH:mm", {
                          locale: ptBR,
                        })}
                      </p>
                    </div>
                    <Link href={`/bookings/${booking.id}`}>
                      <Button variant="ghost" size="sm">
                        Ver
                      </Button>
                    </Link>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Rooms */}
        <Card>
          <CardHeader>
            <div className="flex justify-between items-center">
              <h2 className="text-lg font-semibold">Salas Disponíveis</h2>
              <Link href="/rooms" className="text-sm text-primary-600 hover:underline">
                Ver todas
              </Link>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {rooms.slice(0, 6).map((room) => (
                <div
                  key={room.id}
                  className="p-4 border rounded-lg hover:border-primary-300 transition-colors"
                >
                  <h3 className="font-medium">{room.name}</h3>
                  <p className="text-sm text-gray-600">
                    Capacidade: {room.capacity} pessoas
                  </p>
                  {room.description && (
                    <p className="text-sm text-gray-500 mt-1">{room.description}</p>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </Layout>
  );
}
