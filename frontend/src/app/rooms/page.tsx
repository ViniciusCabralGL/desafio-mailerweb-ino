'use client';

import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import toast from 'react-hot-toast';
import { Plus, Users } from 'lucide-react';
import Layout from '@/components/Layout';
import { Card, CardContent, CardHeader } from '@/components/Card';
import Button from '@/components/Button';
import Input from '@/components/Input';
import Modal from '@/components/Modal';
import { roomsApi } from '@/lib/api';
import { Room } from '@/types';

const roomSchema = z.object({
  name: z.string().min(1, 'Nome é obrigatório'),
  capacity: z.number().min(1, 'Capacidade deve ser maior que 0'),
  description: z.string().optional(),
});

type RoomForm = z.infer<typeof roomSchema>;

export default function RoomsPage() {
  const [rooms, setRooms] = useState<Room[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<RoomForm>({
    resolver: zodResolver(roomSchema),
  });

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

  useEffect(() => {
    fetchRooms();
  }, []);

  const onSubmit = async (data: RoomForm) => {
    setIsSubmitting(true);
    try {
      await roomsApi.create(data);
      toast.success('Sala criada com sucesso!');
      setIsModalOpen(false);
      reset();
      fetchRooms();
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Erro ao criar sala';
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
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Salas</h1>
            <p className="text-gray-600">Gerencie as salas de reunião</p>
          </div>
          <Button onClick={() => setIsModalOpen(true)}>
            <Plus className="w-4 h-4 mr-2" />
            Nova Sala
          </Button>
        </div>

        {rooms.length === 0 ? (
          <Card>
            <CardContent className="text-center py-12">
              <Users className="w-12 h-12 mx-auto text-gray-400" />
              <p className="mt-4 text-gray-600">Nenhuma sala cadastrada</p>
              <Button className="mt-4" onClick={() => setIsModalOpen(true)}>
                Criar primeira sala
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {rooms.map((room) => (
              <Card key={room.id}>
                <CardContent>
                  <h3 className="text-lg font-semibold">{room.name}</h3>
                  <div className="mt-2 flex items-center text-gray-600">
                    <Users className="w-4 h-4 mr-1" />
                    <span>Capacidade: {room.capacity} pessoas</span>
                  </div>
                  {room.description && (
                    <p className="mt-2 text-sm text-gray-500">{room.description}</p>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Create Room Modal */}
        <Modal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          title="Nova Sala"
        >
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <Input
              id="name"
              label="Nome da Sala"
              placeholder="Ex: Sala de Reuniões A"
              error={errors.name?.message}
              {...register('name')}
            />
            <Input
              id="capacity"
              type="number"
              label="Capacidade"
              placeholder="10"
              error={errors.capacity?.message}
              {...register('capacity', { valueAsNumber: true })}
            />
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Descrição (opcional)
              </label>
              <textarea
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                rows={3}
                placeholder="Descrição da sala..."
                {...register('description')}
              />
            </div>
            <div className="flex justify-end space-x-3 pt-4">
              <Button
                type="button"
                variant="secondary"
                onClick={() => setIsModalOpen(false)}
              >
                Cancelar
              </Button>
              <Button type="submit" isLoading={isSubmitting}>
                Criar Sala
              </Button>
            </div>
          </form>
        </Modal>
      </div>
    </Layout>
  );
}
