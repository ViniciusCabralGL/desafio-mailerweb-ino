'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import toast from 'react-hot-toast';
import { authApi } from '@/lib/api';
import { useAuthStore } from '@/lib/store';
import Button from '@/components/Button';
import Input from '@/components/Input';
import { Card, CardContent, CardHeader } from '@/components/Card';

const loginSchema = z.object({
  email: z.string().email('Email inválido'),
  password: z.string().min(1, 'Senha é obrigatória'),
});

type LoginForm = z.infer<typeof loginSchema>;

export default function LoginPage() {
  const router = useRouter();
  const { setUser, setToken } = useAuthStore();
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginForm) => {
    setIsLoading(true);
    try {
      const response = await authApi.login(data.email, data.password);
      setToken(response.access_token);
      setUser(response.user);
      localStorage.setItem('user', JSON.stringify(response.user));
      toast.success('Login realizado com sucesso!');
      router.push('/');
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Erro ao fazer login';
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
            MailerWeb Booking
          </h1>
          <p className="mt-2 text-center text-sm text-gray-600">
            Entre na sua conta para continuar
          </p>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
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
            <Button type="submit" className="w-full" isLoading={isLoading}>
              Entrar
            </Button>
          </form>
          <p className="mt-4 text-center text-sm text-gray-600">
            Não tem uma conta?{' '}
            <Link href="/register" className="text-primary-600 hover:underline">
              Registre-se
            </Link>
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
