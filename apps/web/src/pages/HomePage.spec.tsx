import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { HomePage } from './HomePage';

const renderWithRouter = (component: React.ReactElement) => {
  return render(<BrowserRouter>{component}</BrowserRouter>);
};

describe('HomePage', () => {
  test('renders welcome message', () => {
    renderWithRouter(<HomePage />);

    expect(screen.getByText('Welcome to DocGraph')).toBeInTheDocument();
    expect(screen.getByText(/AI-powered document insight engine/)).toBeInTheDocument();
  });

  test('renders action buttons', () => {
    renderWithRouter(<HomePage />);

    expect(screen.getByRole('button', { name: /get started/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /learn more/i })).toBeInTheDocument();
  });

  test('renders feature sections', () => {
    renderWithRouter(<HomePage />);

    expect(screen.getByText('Document Processing')).toBeInTheDocument();
    expect(screen.getByText('AI-Powered Insights')).toBeInTheDocument();
    expect(screen.getByText('Knowledge Graphs')).toBeInTheDocument();
  });
});