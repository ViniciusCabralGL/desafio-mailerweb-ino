import { render, screen, waitFor } from '@testing-library/react';

// Mock components and API
jest.mock('@/components/Layout', () => {
  return function MockLayout({ children }: { children: React.ReactNode }) {
    return <div data-testid="layout">{children}</div>;
  };
});

jest.mock('@/lib/api', () => ({
  bookingsApi: {
    listMy: jest.fn().mockResolvedValue([
      {
        id: 1,
        title: 'Test Meeting',
        room_id: 1,
        owner_id: 1,
        start_at: '2024-01-15T10:00:00Z',
        end_at: '2024-01-15T11:00:00Z',
        status: 'active',
        created_at: '2024-01-14T10:00:00Z',
      },
    ]),
  },
  roomsApi: {
    list: jest.fn().mockResolvedValue([
      { id: 1, name: 'Room A', capacity: 10 },
    ]),
  },
}));

jest.mock('react-hot-toast', () => ({
  __esModule: true,
  default: {
    success: jest.fn(),
    error: jest.fn(),
  },
}));

// Import after mocks
import BookingsPage from '@/app/bookings/page';

describe('BookingsPage', () => {
  it('renders bookings list', async () => {
    render(<BookingsPage />);

    await waitFor(() => {
      expect(screen.getByText('Test Meeting')).toBeInTheDocument();
    });
  });

  it('shows filter buttons', async () => {
    render(<BookingsPage />);

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /todas/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /ativas/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /canceladas/i })).toBeInTheDocument();
    });
  });

  it('shows new booking button', async () => {
    render(<BookingsPage />);

    await waitFor(() => {
      expect(screen.getByRole('link', { name: /nova reserva/i })).toBeInTheDocument();
    });
  });

  it('displays booking status badge', async () => {
    render(<BookingsPage />);

    await waitFor(() => {
      expect(screen.getByText('Ativa')).toBeInTheDocument();
    });
  });
});
