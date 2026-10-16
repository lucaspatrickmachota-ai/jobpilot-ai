import { render, screen } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { ApiStatus } from '../components/api-status';

vi.mock('../lib/api', () => ({
  getApiHealth: vi.fn().mockResolvedValue({ status: 'ok', service: 'jobpilot-api' }),
}));

afterEach(() => vi.clearAllMocks());

describe('ApiStatus', () => {
  it('shows the API health response', async () => {
    render(<ApiStatus />);
    expect(await screen.findByText('jobpilot-api: ok')).toBeInTheDocument();
  });
});
