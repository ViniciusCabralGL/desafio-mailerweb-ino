'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import toast from 'react-hot-toast';
import { Calendar, Clock, MapPin, Users, Edit, X } from 'lucide-react';
import Layout from '@/components/Layout';
import { Card, CardContent, CardHeader, CardFooter } from '@/components/Card';
import Button from '@/components/Button';
import Modal from '@/components/Modal';
import { bookingsApi, roomsApi } from '@/lib/api';
import { Booking, Room } from '@/types';

export default function BookingDetailPage() {
  const router = useRouter();
  const params = useParams();
  const bookingId = Number(params.id);

  const [booking, setBooking] = useState<Booking | null>(null);
  const [room, setRoom] = useState<Room | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isCanceling, setIsCanceling] = useState(false);
  const [showCancelModal, setShowCancelModal] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const bookingData = await bookingsApi.get(bookingId);
        setBooking(bookingData);

        const roomData = await roomsApi.get(bookingData.room_id);
        setRoom(roomData);
      } catch (error) {
        toast.error('Erro ao carregar reserva');
        router.push('/bookings');
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [bookingId, router]);

  const handleCancel = async () => {
    setIsCanceling(true);
    try {
      await bookingsApi.cancel(bookingId);
      toast.success('Reserva cancelada com sucesso!');
      setShowCancelModal(false);
      // Refresh booking data
      const updatedBooking = await bookingsApi.get(bookingId);
      setBooking(updatedBooking);
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Erro ao cancelar reserva';
      toast.error(message);
    } finally {
      setIsCanceling(false);
    }
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

  if (!booking || !room) {
    return null;
  }

  return (
    <Layout>
      <div className="max-w-2xl mx-auto">
        <Card>
          <CardHeader>
            <div className="flex items-start justify-between">
              <div>
                <h1 className="text-xl font-bold">{booking.title}</h1>
                <span
                  className={`mt-2 inline-block px-3 py-1 text-sm rounded-full ${
                    booking.status === 'active'
                      ? 'bg-green-100 text-green-800'
                      : 'bg-red-100 text-red-800'
                  }`}
                >
                  {booking.status === 'active' ? 'Reserva Ativa' : 'Reserva Cancelada'}
                </span>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="flex items-start space-x-3">
                <MapPin className="w-5 h-5 text-gray-400 mt-0.5" />
                <div>
                  <p className="text-sm text-gray-500">Sala</p>
                  <p className="font-medium">{room.name}</p>
                  <p className="text-sm text-gray-500">
                    Capacidade: {room.capacity} pessoas
                  </p>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <Calendar className="w-5 h-5 text-gray-400 mt-0.5" />
                <div>
                  <p className="text-sm text-gray-500">Data</p>
                  <p className="font-medium">
                    {format(new Date(booking.start_at), "dd 'de' MMMM 'de' yyyy", {
                      locale: ptBR,
                    })}
                  </p>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <Clock className="w-5 h-5 text-gray-400 mt-0.5" />
                <div>
                  <p className="text-sm text-gray-500">Horário</p>
                  <p className="font-medium">
                    {format(new Date(booking.start_at), 'HH:mm')} -{' '}
                    {format(new Date(booking.end_at), 'HH:mm')}
                  </p>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <Users className="w-5 h-5 text-gray-400 mt-0.5" />
                <div>
                  <p className="text-sm text-gray-500">Participantes</p>
                  {booking.participants.length === 0 ? (
                    <p className="text-gray-400">Nenhum participante</p>
                  ) : (
                    <ul className="space-y-1">
                      {booking.participants.map((p) => (
                        <li key={p.id} className="text-sm">
                          {p.email}
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              </div>
            </div>
          </CardContent>
          <CardFooter>
            <div className="flex justify-between w-full">
              <Button variant="ghost" onClick={() => router.back()}>
                Voltar
              </Button>
              {booking.status === 'active' && (
                <div className="flex space-x-2">
                  <Button
                    variant="secondary"
                    onClick={() => router.push(`/bookings/${booking.id}/edit`)}
                  >
                    <Edit className="w-4 h-4 mr-2" />
                    Editar
                  </Button>
                  <Button variant="danger" onClick={() => setShowCancelModal(true)}>
                    <X className="w-4 h-4 mr-2" />
                    Cancelar
                  </Button>
                </div>
              )}
            </div>
          </CardFooter>
        </Card>

        {/* Cancel Confirmation Modal */}
        <Modal
          isOpen={showCancelModal}
          onClose={() => setShowCancelModal(false)}
          title="Cancelar Reserva"
        >
          <p className="text-gray-600">
            Tem certeza que deseja cancelar esta reserva? Esta ação não pode ser
            desfeita e todos os participantes serão notificados.
          </p>
          <div className="flex justify-end space-x-3 mt-6">
            <Button variant="secondary" onClick={() => setShowCancelModal(false)}>
              Não, manter
            </Button>
            <Button variant="danger" onClick={handleCancel} isLoading={isCanceling}>
              Sim, cancelar
            </Button>
          </div>
        </Modal>
      </div>
    </Layout>
  );
}
