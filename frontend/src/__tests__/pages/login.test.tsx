import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import LoginPage from '@/app/login/page';

// Mock the API
jest.mock('@/lib/api', () => ({
  authApi: {
    login: jest.fn(),
  },
}));

// Mock react-hot-toast
jest.mock('react-hot-toast', () => ({
  __esModule: true,
  default: {
    success: jest.fn(),
    error: jest.fn(),
  },
}));

// Mock zustand store
jest.mock('@/lib/store', () => ({
  useAuthStore: () => ({
    setUser: jest.fn(),
    setToken: jest.fn(),
  }),
}));

describe('LoginPage', () => {
  it('renders login form', () => {
    render(<LoginPage />);

    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/senha/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /entrar/i })).toBeInTheDocument();
  });

  it('shows validation errors for empty fields', async () => {
    render(<LoginPage />);

    const submitButton = screen.getByRole('button', { name: /entrar/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/email inválido/i)).toBeInTheDocument();
    });
  });

  it('shows validation error for invalid email', async () => {
    render(<LoginPage />);

    const emailInput = screen.getByLabelText(/email/i);
    fireEvent.change(emailInput, { target: { value: 'invalid-email' } });

    const submitButton = screen.getByRole('button', { name: /entrar/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/email inválido/i)).toBeInTheDocument();
    });
  });

  it('has link to register page', () => {
    render(<LoginPage />);

    const registerLink = screen.getByRole('link', { name: /registre-se/i });
    expect(registerLink).toHaveAttribute('href', '/register');
  });
});
