const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

export type HealthResponse = {
  status: string;
  service: string;
};

export async function getApiHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE_URL}/health`, { cache: 'no-store' });
  if (!response.ok) {
    throw new Error(`API health check failed with status ${response.status}`);
  }
  return (await response.json()) as HealthResponse;
}
