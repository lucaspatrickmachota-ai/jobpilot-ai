import { ApiStatus } from '@/components/api-status';
import { Workspace } from '@/components/workspace';

export default function HomePage() {
  return (
    <main className="min-h-screen md:flex">
      <aside className="border-b border-[var(--border)] bg-white p-5 md:min-h-screen md:w-64 md:border-b-0 md:border-r">
        <div className="mb-8 flex items-center gap-3">
          <div className="grid size-10 place-items-center rounded-xl bg-[#2457d6] font-bold text-white">J</div>
          <div><p className="font-semibold tracking-tight">JobPilot AI</p><p className="text-xs text-[var(--muted)]">Career workspace</p></div>
        </div>
        <nav aria-label="Main navigation" className="flex gap-2 overflow-x-auto md:flex-col">
          <a href="#dashboard" className="rounded-lg bg-blue-50 px-3 py-2.5 text-sm font-semibold text-blue-700">Dashboard</a>
          <a href="#applications" className="rounded-lg px-3 py-2.5 text-sm text-slate-600 hover:bg-slate-50">Applications</a>
          <a href="#system-status" className="rounded-lg px-3 py-2.5 text-sm text-slate-600 hover:bg-slate-50">System status</a>
        </nav>
        <p className="mt-8 hidden text-xs leading-5 text-slate-400 md:block">A private workspace for a more intentional job search.</p>
      </aside>
      <section id="dashboard" className="w-full p-5 sm:p-8 lg:p-10">
        <header className="mb-8 flex flex-wrap items-start justify-between gap-4">
          <div><p className="mb-2 text-sm font-medium text-blue-700">WORKSPACE</p><h1 className="text-3xl font-semibold tracking-tight">Your job search, in one place.</h1><p className="mt-2 max-w-2xl text-sm leading-6 text-[var(--muted)]">Track applications, manage their status and keep your next career move organised.</p></div>
          <span className="rounded-full border border-[var(--border)] bg-white px-3 py-2 text-sm text-slate-600">MVP · Connected workflows</span>
        </header>
        <div id="applications"><Workspace /></div>
        <section id="system-status" className="mt-6 rounded-2xl border border-[var(--border)] bg-white p-5"><h2 className="font-semibold">System status</h2><p className="mt-1 text-sm text-[var(--muted)]">Live health check against the configured API URL.</p><div className="mt-4"><ApiStatus /></div></section>
        <footer className="mt-8 text-xs text-slate-400">JobPilot AI · Built for privacy, clarity and explainable decisions.</footer>
      </section>
    </main>
  );
}
