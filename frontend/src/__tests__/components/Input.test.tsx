import { render, screen, fireEvent } from '@testing-library/react';
import Input from '@/components/Input';

describe('Input', () => {
  it('renders input with label', () => {
    render(<Input id="test" label="Test Label" />);
    expect(screen.getByLabelText('Test Label')).toBeInTheDocument();
  });

  it('handles value changes', () => {
    const handleChange = jest.fn();
    render(<Input id="test" onChange={handleChange} />);

    const input = screen.getByRole('textbox');
    fireEvent.change(input, { target: { value: 'new value' } });

    expect(handleChange).toHaveBeenCalled();
  });

  it('displays error message', () => {
    render(<Input id="test" error="This field is required" />);
    expect(screen.getByText('This field is required')).toBeInTheDocument();
  });

  it('applies error styles when error is present', () => {
    render(<Input id="test" error="Error" />);
    const input = screen.getByRole('textbox');
    expect(input).toHaveClass('border-red-500');
  });

  it('applies placeholder', () => {
    render(<Input id="test" placeholder="Enter text" />);
    expect(screen.getByPlaceholderText('Enter text')).toBeInTheDocument();
  });
});
