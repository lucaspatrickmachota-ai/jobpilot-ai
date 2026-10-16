'use client';

import { useEffect, useState } from 'react';
import { getApiHealth, type HealthResponse } from '@/lib/api';

type Status = { kind: 'loading' } | { kind: 'success'; data: HealthResponse } | { kind: 'error'; message: string };

export function ApiStatus() {
  const [status, setStatus] = useState<Status>({ kind: 'loading' });

  useEffect(() => {
    let active = true;
    getApiHealth().then((data) => {
      if (active) setStatus({ kind: 'success', data });
    }).catch((error: unknown) => {
      if (active) setStatus({ kind: 'error', message: error instanceof Error ? error.message : 'Unknown API error' });
    });
    return () => { active = false; };
  }, []);

  if (status.kind === 'loading') return <p role="status" className="text-sm text-slate-500">Checking API…</p>;
  if (status.kind === 'error') return <div role="alert" className="rounded-lg bg-rose-50 p-3 text-sm text-rose-700">API unavailable: {status.message}</div>;
  return <div role="status" className="rounded-lg bg-emerald-50 p-3 text-sm text-emerald-800"><span className="mr-2 inline-block size-2 rounded-full bg-emerald-500" />{status.data.service}: {status.data.status}</div>;
}
