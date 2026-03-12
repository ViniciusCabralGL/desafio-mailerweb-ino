'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuthStore } from '@/lib/store';
import { LogOut, Calendar, Home, Users } from 'lucide-react';

interface LayoutProps {
  children: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const router = useRouter();
  const { user, isAuthenticated, isLoading, initialize, logout } = useAuthStore();

  useEffect(() => {
    initialize();
  }, [initialize]);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isLoading, isAuthenticated, router]);

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-8">
              <Link href="/" className="text-xl font-bold text-primary-600">
                MailerWeb Booking
              </Link>
              <nav className="hidden md:flex space-x-4">
                <Link
                  href="/"
                  className="flex items-center px-3 py-2 text-sm font-medium text-gray-700 hover:text-primary-600"
                >
                  <Home className="w-4 h-4 mr-1" />
                  Início
                </Link>
                <Link
                  href="/rooms"
                  className="flex items-center px-3 py-2 text-sm font-medium text-gray-700 hover:text-primary-600"
                >
                  <Users className="w-4 h-4 mr-1" />
                  Salas
                </Link>
                <Link
                  href="/bookings"
                  className="flex items-center px-3 py-2 text-sm font-medium text-gray-700 hover:text-primary-600"
                >
                  <Calendar className="w-4 h-4 mr-1" />
                  Reservas
                </Link>
              </nav>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">
                Olá, <span className="font-medium">{user?.name}</span>
              </span>
              <button
                onClick={handleLogout}
                className="flex items-center px-3 py-2 text-sm font-medium text-gray-700 hover:text-red-600"
              >
                <LogOut className="w-4 h-4 mr-1" />
                Sair
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
    </div>
  );
}
