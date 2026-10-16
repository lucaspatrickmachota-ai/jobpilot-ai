'use client';

import { FormEvent, useCallback, useEffect, useState } from 'react';

type Status = 'SAVED' | 'APPLIED' | 'INTERVIEW' | 'OFFER' | 'REJECTED';
type Application = { id: string; company: string; position: string; job_url: string | null; description: string | null; status: Status; created_at: string; updated_at: string };
type Stats = { total: number; saved: number; applied: number; interviews: number; offers: number; rejected: number; interview_conversion_percent: number };
type Analysis = { id: string; application_id: string; match_score: number; matched_skills: string[]; missing_skills: string[]; breakdown: Record<string, number>; analysis: string; created_at: string };
type UserProfile = { id: string; email: string };
type ResumeAnswer = { answer: string; evidence: { chunk_id: string; content: string }[]; grounded: boolean };
const API = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';
const statuses: Status[] = ['SAVED', 'APPLIED', 'INTERVIEW', 'OFFER', 'REJECTED'];

async function request<T>(path: string, token: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  if (token) headers.set('Authorization', `Bearer ${token}`);
  if (!(init.body instanceof FormData) && init.body !== undefined) headers.set('Content-Type', 'application/json');
  const response = await fetch(`${API}${path}`, { ...init, headers });
  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    try { const body: { detail?: string } = await response.json(); message = body.detail ?? message; } catch { /* keep HTTP fallback */ }
    throw new Error(message);
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export function Workspace() {
  const [token, setToken] = useState('');
  const [authMode, setAuthMode] = useState<'login' | 'register'>('register');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [applications, setApplications] = useState<Application[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [company, setCompany] = useState('');
  const [position, setPosition] = useState('');
  const [description, setDescription] = useState('');
  const [jobUrl, setJobUrl] = useState('');
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [busy, setBusy] = useState(false);
  const [resumeName, setResumeName] = useState('');
  const [analysisById, setAnalysisById] = useState<Record<string, Analysis>>({});
  const [resumeQuestion, setResumeQuestion] = useState('');
  const [resumeAnswer, setResumeAnswer] = useState<ResumeAnswer | null>(null);

  const refresh = useCallback(async (accessToken: string) => {
    const [items, metrics] = await Promise.all([
      request<Application[]>('/applications', accessToken),
      request<Stats>('/dashboard/stats', accessToken),
    ]);
    setApplications(items);
    setStats(metrics);
  }, []);

  useEffect(() => {
    const saved = window.sessionStorage.getItem('jobpilot_access_token');
    if (saved) {
      setToken(saved);
      void Promise.all([request<UserProfile>('/auth/me', saved), refresh(saved)])
        .then(([profile]) => setEmail(profile.email))
        .catch(() => { window.sessionStorage.removeItem('jobpilot_access_token'); setToken(''); });
      void request<{ filename: string }>('/resume', saved).then(resume => setResumeName(resume.filename)).catch(() => undefined);
    }
  }, [refresh]);

  async function submitAuth(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setBusy(true); setError('');
    try {
      if (authMode === 'register') await request('/auth/register', '', { method: 'POST', body: JSON.stringify({ email, password }) });
      const response = await fetch(`${API}/auth/login`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email, password }) });
      const data = await response.json() as { access_token?: string; detail?: string };
      if (!response.ok || !data.access_token) throw new Error(data.detail ?? 'Could not sign in');
      window.sessionStorage.setItem('jobpilot_access_token', data.access_token);
      setToken(data.access_token); setPassword(''); await refresh(data.access_token); setNotice('Signed in successfully.');
    } catch (err) { setError(err instanceof Error ? err.message : 'Unexpected error'); }
    finally { setBusy(false); }
  }

  async function createApplication(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); if (!token) return; setBusy(true); setError(''); setNotice('');
    try {
      await request<Application>('/applications', token, { method: 'POST', body: JSON.stringify({ company, position, description: description || null, job_url: jobUrl || null }) });
      setCompany(''); setPosition(''); setDescription(''); setJobUrl(''); await refresh(token); setNotice('Application saved.');
    } catch (err) { setError(err instanceof Error ? err.message : 'Could not save application'); }
    finally { setBusy(false); }
  }

  async function uploadResume(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); const form = event.currentTarget; const fileInput = form.elements.namedItem('resume-file');
    if (!(fileInput instanceof HTMLInputElement) || !fileInput.files?.[0]) return;
    const file = fileInput.files[0]; const data = new FormData(); data.append('file', file); setError(''); setNotice(''); setBusy(true);
    try { const resume = await request<{ filename: string }>('/resume', token, { method: 'POST', body: data }); setResumeName(resume.filename); setNotice('Resume uploaded and text extracted.'); form.reset(); }
    catch (err) { setError(err instanceof Error ? err.message : 'Could not upload resume'); } finally { setBusy(false); }
  }

  async function askResume(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setError(''); setNotice(''); setResumeAnswer(null);
    try { const answer = await request<ResumeAnswer>('/resume/ask', token, { method: 'POST', body: JSON.stringify({ question: resumeQuestion }) }); setResumeAnswer(answer); }
    catch (err) { setError(err instanceof Error ? err.message : 'Could not answer from your CV'); }
  }

  async function deleteResume() {
    try { await request<void>('/resume', token, { method: 'DELETE' }); setResumeName(''); setResumeAnswer(null); setNotice('Resume deleted.'); }
    catch (err) { setError(err instanceof Error ? err.message : 'Could not delete resume'); }
  }

  async function analyze(item: Application) {
    setError(''); setNotice('');
    try { const result = await request<Analysis>(`/applications/${item.id}/analyze`, token, { method: 'POST' }); setAnalysisById(previous => ({ ...previous, [item.id]: result })); setNotice(`Analysis complete for ${item.company}.`); }
    catch (err) { setError(err instanceof Error ? err.message : 'Could not analyze application'); }
  }

  async function changeStatus(item: Application, status: Status) {
    setError('');
    try { await request(`/applications/${item.id}`, token, { method: 'PATCH', body: JSON.stringify({ status }) }); await refresh(token); setNotice('Application status updated.'); }
    catch (err) { setError(err instanceof Error ? err.message : 'Could not update status'); }
  }

  async function removeApplication(item: Application) {
    if (!window.confirm(`Delete the application for ${item.company}?`)) return;
    try { await request(`/applications/${item.id}`, token, { method: 'DELETE' }); await refresh(token); setNotice('Application deleted.'); }
    catch (err) { setError(err instanceof Error ? err.message : 'Could not delete application'); }
  }

  function signOut() { window.sessionStorage.removeItem('jobpilot_access_token'); setToken(''); setApplications([]); setStats(null); setNotice(''); setError(''); }

  if (!token) return <section className="mx-auto max-w-md rounded-2xl border border-[var(--border)] bg-white p-6 shadow-sm sm:p-8">
    <h2 className="text-xl font-semibold">{authMode === 'register' ? 'Create your account' : 'Welcome back'}</h2>
    <p className="mt-2 text-sm text-[var(--muted)]">Your applications are private to your account.</p>
    {error && <p role="alert" className="mt-4 rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</p>}
    <form onSubmit={submitAuth} className="mt-5 space-y-4">
      <label className="block text-sm font-medium">Email<input required type="email" autoComplete="email" value={email} onChange={e => setEmail(e.target.value)} className="mt-1 block w-full rounded-lg border border-[var(--border)] px-3 py-2.5 font-normal" /></label>
      <label className="block text-sm font-medium">Password<input required minLength={authMode === 'register' ? 12 : 1} maxLength={128} type="password" autoComplete={authMode === 'register' ? 'new-password' : 'current-password'} value={password} onChange={e => setPassword(e.target.value)} className="mt-1 block w-full rounded-lg border border-[var(--border)] px-3 py-2.5 font-normal" /><span className="mt-1 block text-xs text-[var(--muted)]">Registration requires at least 12 characters.</span></label>
      <button disabled={busy} className="w-full rounded-lg bg-blue-700 px-4 py-3 text-sm font-semibold text-white hover:bg-blue-800 disabled:opacity-60">{busy ? 'Please wait…' : authMode === 'register' ? 'Create account' : 'Sign in'}</button>
    </form>
    <button onClick={() => { setAuthMode(authMode === 'register' ? 'login' : 'register'); setError(''); }} className="mt-4 w-full text-sm font-medium text-blue-700">{authMode === 'register' ? 'Already have an account? Sign in' : 'New to JobPilot AI? Create an account'}</button>
  </section>;

  return <div className="space-y-6">
    <div className="flex flex-wrap items-center justify-between gap-3"><p className="text-sm text-[var(--muted)]">Signed in as <strong className="text-slate-800">{email}</strong></p><button onClick={signOut} className="rounded-lg border border-[var(--border)] px-3 py-2 text-sm hover:bg-slate-50">Sign out</button></div>
    {error && <p role="alert" className="rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</p>}{notice && <p role="status" className="rounded-lg bg-emerald-50 p-3 text-sm text-emerald-800">{notice}</p>}
    <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">{[{ label: 'Applications', value: stats?.total }, { label: 'Saved', value: stats?.saved }, { label: 'Applied', value: stats?.applied }, { label: 'Interviews', value: stats?.interviews }, { label: 'Offers', value: stats?.offers }, { label: 'Rejected', value: stats?.rejected }, { label: 'Interview conversion', value: `${stats?.interview_conversion_percent ?? 0}%` }].map(card => <article key={card.label} className="rounded-xl border border-[var(--border)] bg-white p-5"><p className="text-sm text-[var(--muted)]">{card.label}</p><p className="mt-2 text-2xl font-semibold">{card.value ?? '—'}</p></article>)}</div>
    <div className="grid items-start gap-6 xl:grid-cols-[minmax(280px,0.8fr)_minmax(0,1.5fr)]">
      <div className="space-y-6"><section className="rounded-2xl border border-[var(--border)] bg-white p-5"><h2 className="text-lg font-semibold">Resume</h2><p className="mt-1 text-sm text-[var(--muted)]">Upload a PDF to enable job matching.</p>{resumeName && <div className="mt-2 flex items-center justify-between gap-2"><p className="text-sm font-medium text-emerald-700">Current CV: {resumeName}</p><button onClick={() => void deleteResume()} className="text-xs text-red-700 underline">Delete</button></div>}<form onSubmit={uploadResume} className="mt-4 space-y-3"><label className="block text-sm font-medium">PDF file<input required name="resume-file" type="file" accept="application/pdf,.pdf" className="mt-1 block w-full text-sm file:mr-3 file:rounded-lg file:border-0 file:bg-slate-100 file:px-3 file:py-2" /></label><button disabled={busy} className="w-full rounded-lg border border-[var(--border)] px-4 py-2.5 text-sm font-semibold hover:bg-slate-50 disabled:opacity-60">Upload CV</button></form><div className="mt-5 border-t border-[var(--border)] pt-4"><h3 className="font-semibold">Ask about your experience</h3><p className="mt-1 text-xs leading-5 text-[var(--muted)]">Answers require an AI provider and indexed CV evidence.</p><form onSubmit={askResume} className="mt-3 space-y-2"><label htmlFor="resume-question" className="sr-only">Question about your CV</label><textarea id="resume-question" required minLength={3} maxLength={2000} rows={3} value={resumeQuestion} onChange={e => setResumeQuestion(e.target.value)} placeholder="What experience do I have with REST APIs?" className="block w-full rounded-lg border border-[var(--border)] px-3 py-2 text-sm" /><button className="w-full rounded-lg bg-slate-900 px-4 py-2.5 text-sm font-semibold text-white">Ask using CV evidence</button></form>{resumeAnswer && <div className="mt-3 rounded-xl bg-slate-50 p-3"><p className="whitespace-pre-wrap text-sm">{resumeAnswer.answer}</p><p className="mt-3 text-xs font-semibold uppercase tracking-wide text-[var(--muted)]">Evidence ({resumeAnswer.evidence.length})</p>{resumeAnswer.evidence.map(item => <blockquote key={item.chunk_id} className="mt-2 border-l-2 border-blue-500 pl-3 text-xs leading-5 text-slate-600">{item.content}</blockquote>)}</div>}</div></section>
      <section className="rounded-2xl border border-[var(--border)] bg-white p-5"><h2 className="text-lg font-semibold">Add an application</h2><form onSubmit={createApplication} className="mt-4 space-y-3">
        <label className="block text-sm font-medium">Company<input required maxLength={200} value={company} onChange={e => setCompany(e.target.value)} className="mt-1 block w-full rounded-lg border border-[var(--border)] px-3 py-2 font-normal" /></label>
        <label className="block text-sm font-medium">Position<input required maxLength={200} value={position} onChange={e => setPosition(e.target.value)} className="mt-1 block w-full rounded-lg border border-[var(--border)] px-3 py-2 font-normal" /></label>
        <label className="block text-sm font-medium">Job URL (optional)<input type="url" value={jobUrl} onChange={e => setJobUrl(e.target.value)} className="mt-1 block w-full rounded-lg border border-[var(--border)] px-3 py-2 font-normal" /></label>
        <label className="block text-sm font-medium">Job description (optional)<textarea rows={4} maxLength={30000} value={description} onChange={e => setDescription(e.target.value)} className="mt-1 block w-full rounded-lg border border-[var(--border)] px-3 py-2 font-normal" /></label>
        <button disabled={busy} className="w-full rounded-lg bg-blue-700 px-4 py-2.5 text-sm font-semibold text-white disabled:opacity-60">Save application</button>
      </form></section></div>
      <section className="rounded-2xl border border-[var(--border)] bg-white p-5"><div className="flex items-center justify-between gap-3"><h2 className="text-lg font-semibold">Your applications</h2><span className="text-sm text-[var(--muted)]">{applications.length} total</span></div>
        {applications.length === 0 ? <div className="mt-5 rounded-xl border border-dashed border-[var(--border)] p-8 text-center"><p className="font-medium">No applications yet</p><p className="mt-1 text-sm text-[var(--muted)]">Add your first role to start tracking your search.</p></div> : <ul className="mt-4 divide-y divide-[var(--border)]">{applications.map(item => <li key={item.id} className="py-4 first:pt-1"><div className="flex flex-wrap items-start justify-between gap-3"><div><p className="font-semibold">{item.position}</p><p className="mt-1 text-sm text-[var(--muted)]">{item.company}</p>{item.job_url && <a href={item.job_url} target="_blank" rel="noreferrer" className="mt-1 inline-block text-xs text-blue-700 underline">View job posting</a>}</div><button onClick={() => void removeApplication(item)} className="text-xs text-red-700 underline">Delete</button></div><div className="mt-3 flex flex-wrap items-center gap-2"><label htmlFor={`status-${item.id}`} className="text-xs text-[var(--muted)]">Status</label><select id={`status-${item.id}`} value={item.status} onChange={e => void changeStatus(item, e.target.value as Status)} className="rounded-lg border border-[var(--border)] bg-white px-2 py-1.5 text-sm">{statuses.map(status => <option key={status} value={status}>{status}</option>)}</select><span className="text-xs text-[var(--muted)]">Added {new Date(item.created_at).toLocaleDateString()}</span><button onClick={() => void analyze(item)} className="rounded-lg bg-blue-50 px-2.5 py-1.5 text-xs font-semibold text-blue-700 hover:bg-blue-100">Analyze vs CV</button></div>{analysisById[item.id] && <div className="mt-3 rounded-xl bg-slate-50 p-3"><div className="flex items-center justify-between"><p className="text-sm font-semibold">Match score</p><p className="text-lg font-semibold">{analysisById[item.id].match_score}%</p></div><p className="mt-2 text-xs text-[var(--muted)]">Matched: {analysisById[item.id].matched_skills.join(', ') || 'None detected'}</p><p className="mt-1 text-xs text-[var(--muted)]">Missing: {analysisById[item.id].missing_skills.join(', ') || 'None detected'}</p><p className="mt-2 text-xs leading-5">{analysisById[item.id].analysis}</p></div>}</li>)}</ul>}
      </section>
    </div>
  </div>;
}
