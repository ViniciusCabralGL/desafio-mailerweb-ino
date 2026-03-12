'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import toast from 'react-hot-toast';
import { authApi } from '@/lib/api';
import Button from '@/components/Button';
import Input from '@/components/Input';
import { Card, CardContent, CardHeader } from '@/components/Card';

const registerSchema = z.object({
  name: z.string().min(2, 'Nome deve ter pelo menos 2 caracteres'),
  email: z.string().email('Email inválido'),
  password: z.string().min(6, 'Senha deve ter pelo menos 6 caracteres'),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: 'Senhas não conferem',
  path: ['confirmPassword'],
});

type RegisterForm = z.infer<typeof registerSchema>;

export default function RegisterPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterForm>({
    resolver: zodResolver(registerSchema),
  });

  const onSubmit = async (data: RegisterForm) => {
    setIsLoading(true);
    try {
      await authApi.register(data.email, data.name, data.password);
      toast.success('Conta criada com sucesso! Faça login para continuar.');
      router.push('/login');
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Erro ao criar conta';
      toast.error(message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <Card className="w-full max-w-md">
        <CardHeader>
          <h1 className="text-2xl font-bold text-center text-gray-900">
            Criar Conta
          </h1>
          <p className="mt-2 text-center text-sm text-gray-600">
            Preencha os dados abaixo para se registrar
          </p>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <Input
              id="name"
              type="text"
              label="Nome"
              placeholder="Seu nome"
              error={errors.name?.message}
              {...register('name')}
            />
            <Input
              id="email"
              type="email"
              label="Email"
              placeholder="seu@email.com"
              error={errors.email?.message}
              {...register('email')}
            />
            <Input
              id="password"
              type="password"
              label="Senha"
              placeholder="********"
              error={errors.password?.message}
              {...register('password')}
            />
            <Input
              id="confirmPassword"
              type="password"
              label="Confirmar Senha"
              placeholder="********"
              error={errors.confirmPassword?.message}
              {...register('confirmPassword')}
            />
            <Button type="submit" className="w-full" isLoading={isLoading}>
              Criar Conta
            </Button>
          </form>
          <p className="mt-4 text-center text-sm text-gray-600">
            Já tem uma conta?{' '}
            <Link href="/login" className="text-primary-600 hover:underline">
              Faça login
            </Link>
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
