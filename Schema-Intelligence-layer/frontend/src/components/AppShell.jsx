export default function AppShell({ title, subtitle, children, rightSlot }) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-sky-50 via-white to-indigo-50">
      <header className="sticky top-0 z-20 border-b border-gray-100 bg-white/70 backdrop-blur">
        <div className="mx-auto max-w-7xl px-5 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-11 h-11 rounded-2xl bg-indigo-600 text-white flex items-center justify-center font-bold shadow">
              SI
            </div>
            <div>
              <h1 className="text-lg font-semibold text-gray-900">{title}</h1>
              <p className="text-sm text-gray-500">{subtitle}</p>
            </div>
          </div>

          {rightSlot ? <div>{rightSlot}</div> : null}
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-5 py-8">{children}</main>

      <footer className="mx-auto max-w-7xl px-5 pb-10 text-xs text-gray-400">
        © {new Date().getFullYear()} Schema Intelligence Layer
      </footer>
    </div>
  );
}
