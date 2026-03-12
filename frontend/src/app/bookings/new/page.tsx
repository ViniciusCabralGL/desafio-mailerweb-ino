'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useForm, useFieldArray } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import toast from 'react-hot-toast';
import { Plus, Trash2 } from 'lucide-react';
import Layout from '@/components/Layout';
import { Card, CardContent, CardHeader } from '@/components/Card';
import Button from '@/components/Button';
import Input from '@/components/Input';
import { bookingsApi, roomsApi } from '@/lib/api';
import { Room } from '@/types';

const bookingSchema = z.object({
  title: z.string().min(1, 'Título é obrigatório'),
  room_id: z.number().min(1, 'Selecione uma sala'),
  date: z.string().min(1, 'Data é obrigatória'),
  start_time: z.string().min(1, 'Horário de início é obrigatório'),
  end_time: z.string().min(1, 'Horário de término é obrigatório'),
  participants: z.array(z.object({ email: z.string().email('Email inválido') })),
});

type BookingForm = z.infer<typeof bookingSchema>;

export default function NewBookingPage() {
  const router = useRouter();
  const [rooms, setRooms] = useState<Room[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    control,
    formState: { errors },
  } = useForm<BookingForm>({
    resolver: zodResolver(bookingSchema),
    defaultValues: {
      participants: [],
    },
  });

  const { fields, append, remove } = useFieldArray({
    control,
    name: 'participants',
  });

  useEffect(() => {
    const fetchRooms = async () => {
      try {
        const data = await roomsApi.list();
        setRooms(data);
      } catch (error) {
        toast.error('Erro ao carregar salas');
      } finally {
        setIsLoading(false);
      }
    };

    fetchRooms();
  }, []);

  const onSubmit = async (data: BookingForm) => {
    // Combine date and times
    const start_at = new Date(`${data.date}T${data.start_time}`).toISOString();
    const end_at = new Date(`${data.date}T${data.end_time}`).toISOString();

    // Validate times
    if (new Date(start_at) >= new Date(end_at)) {
      toast.error('Horário de início deve ser anterior ao de término');
      return;
    }

    const duration = (new Date(end_at).getTime() - new Date(start_at).getTime()) / 60000;
    if (duration < 15) {
      toast.error('Duração mínima é de 15 minutos');
      return;
    }
    if (duration > 480) {
      toast.error('Duração máxima é de 8 horas');
      return;
    }

    setIsSubmitting(true);
    try {
      await bookingsApi.create({
        title: data.title,
        room_id: data.room_id,
        start_at,
        end_at,
        participants: data.participants,
      });
      toast.success('Reserva criada com sucesso!');
      router.push('/bookings');
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Erro ao criar reserva';
      toast.error(message);
    } finally {
      setIsSubmitting(false);
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

  return (
    <Layout>
      <div className="max-w-2xl mx-auto">
        <Card>
          <CardHeader>
            <h1 className="text-xl font-bold">Nova Reserva</h1>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
              <Input
                id="title"
                label="Título da Reunião"
                placeholder="Ex: Reunião de Planejamento"
                error={errors.title?.message}
                {...register('title')}
              />

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Sala
                </label>
                <select
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  {...register('room_id', { valueAsNumber: true })}
                >
                  <option value="">Selecione uma sala</option>
                  {rooms.map((room) => (
                    <option key={room.id} value={room.id}>
                      {room.name} (Capacidade: {room.capacity})
                    </option>
                  ))}
                </select>
                {errors.room_id && (
                  <p className="mt-1 text-sm text-red-600">{errors.room_id.message}</p>
                )}
              </div>

              <Input
                id="date"
                type="date"
                label="Data"
                error={errors.date?.message}
                {...register('date')}
              />

              <div className="grid grid-cols-2 gap-4">
                <Input
                  id="start_time"
                  type="time"
                  label="Início"
                  error={errors.start_time?.message}
                  {...register('start_time')}
                />
                <Input
                  id="end_time"
                  type="time"
                  label="Término"
                  error={errors.end_time?.message}
                  {...register('end_time')}
                />
              </div>

              {/* Participants */}
              <div>
                <div className="flex justify-between items-center mb-2">
                  <label className="block text-sm font-medium text-gray-700">
                    Participantes (opcional)
                  </label>
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={() => append({ email: '' })}
                  >
                    <Plus className="w-4 h-4 mr-1" />
                    Adicionar
                  </Button>
                </div>
                {fields.map((field, index) => (
                  <div key={field.id} className="flex items-center space-x-2 mb-2">
                    <Input
                      type="email"
                      placeholder="email@exemplo.com"
                      error={errors.participants?.[index]?.email?.message}
                      {...register(`participants.${index}.email`)}
                    />
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => remove(index)}
                    >
                      <Trash2 className="w-4 h-4 text-red-500" />
                    </Button>
                  </div>
                ))}
              </div>

              <div className="flex justify-end space-x-3 pt-4">
                <Button
                  type="button"
                  variant="secondary"
                  onClick={() => router.back()}
                >
                  Cancelar
                </Button>
                <Button type="submit" isLoading={isSubmitting}>
                  Criar Reserva
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </Layout>
  );
}
