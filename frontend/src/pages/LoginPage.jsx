import { useState } from "react";
import { signInWithEmailAndPassword } from "firebase/auth";
import { auth } from "../firebase";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleLogin(e) {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      await signInWithEmailAndPassword(auth, email, password);
    } catch {
      setError("Invalid email or password");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen w-full relative overflow-hidden bg-slate-50 flex items-center justify-center px-4">
      {/* BACKGROUND DECOR */}
      <div className="absolute inset-0 -z-10">
        <div className="absolute top-[-140px] left-[-140px] h-[420px] w-[420px] rounded-full bg-indigo-200/40 blur-3xl" />
        <div className="absolute bottom-[-140px] right-[-140px] h-[420px] w-[420px] rounded-full bg-violet-200/40 blur-3xl" />
      </div>

      {/* LOGIN CARD */}
      <div className="w-full max-w-md rounded-2xl bg-white border border-slate-200 shadow-2xl overflow-hidden">
        {/* HEADER */}
        <div className="px-8 py-10 bg-gradient-to-r from-indigo-600 via-violet-600 to-fuchsia-600 text-center">
          <h1 className="text-2xl font-extrabold text-white tracking-wide">
            Schema Intelligence 
          </h1>
          <p className="mt-2 text-sm text-white/80">
            Platform Access
          </p>
        </div>

        {/* FORM */}
        <form onSubmit={handleLogin} className="px-8 py-8 space-y-6">
          {/* EMAIL */}
          <div>
            <label className="block text-xs font-bold text-slate-600 mb-1">
              Email
            </label>
            <input
              type="email"
              placeholder="your@email.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full rounded-xl border border-slate-300 px-4 py-3 text-sm
                         text-slate-900 placeholder:text-slate-400
                         focus:outline-none focus:ring-2 focus:ring-indigo-500/20
                         focus:border-indigo-500 transition"
            />
          </div>

          {/* PASSWORD */}
          <div>
            <label className="block text-xs font-bold text-slate-600 mb-1">
              Password
            </label>
            <input
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full rounded-xl border border-slate-300 px-4 py-3 text-sm
                         text-slate-900 placeholder:text-slate-400
                         focus:outline-none focus:ring-2 focus:ring-indigo-500/20
                         focus:border-indigo-500 transition"
            />
          </div>

          {/* ERROR */}
          {error && (
            <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-semibold text-red-700">
              {error}
            </div>
          )}

          {/* ACTION */}
          <button
            type="submit"
            disabled={loading}
            className="group w-full rounded-xl px-4 py-3 font-semibold text-white
                       bg-gradient-to-r from-indigo-600 via-violet-600 to-fuchsia-600
                       shadow-md shadow-indigo-500/30
                       hover:shadow-lg hover:shadow-fuchsia-500/30
                       transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <span className="inline-flex items-center justify-center gap-2">
                <span className="h-4 w-4 rounded-full border-2 border-white/40 border-t-white animate-spin" />
                Signing in…
              </span>
            ) : (
              <span className="inline-flex items-center gap-2">
                Access Platform
                <span className="transition-transform group-hover:translate-x-1">
                  →
                </span>
              </span>
            )}
          </button>
        </form>

        {/* FOOTER */}
        <div className="px-8 py-4 border-t bg-slate-50 text-center">
          <p className="text-xs text-slate-500">
            Schema Intelligence Platform • Acies Global
          </p>
        </div>
      </div>
    </div>
  );
}
