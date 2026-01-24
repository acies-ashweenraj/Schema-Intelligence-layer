import { useState } from "react";
import { generateMetadata } from "../api/client";

export default function ConfigPage({ onConnected }) {
  const [form, setForm] = useState({
    db_type: "postgres",
    host: "localhost",
    port: 5432,
    database: "",
    username: "postgres",
    password: "",
    schema_name: "public",
  });

  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");

  function handleChange(e) {
    const { name, value } = e.target;
    setForm((p) => ({
      ...p,
      [name]: name === "port" ? Number(value) : value,
    }));
  }

  async function handleContinue() {
    setLoading(true);
    setErr("");

    try {
      const payload = {
        ...form,
        output_format: "json", // ✅ backend requires this
      };

      const result = await generateMetadata(payload);

      // pass db config + metadata json
      onConnected(form, result);
    } catch (error) {
      console.log("ERROR:", error?.response?.data || error);
      setErr("❌ Failed to generate metadata. Please check DB details.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen w-full bg-slate-50">
      {/* TOP BAR */}
      <div className="sticky top-0 z-30 border-b border-slate-200 bg-white/85 backdrop-blur">
        <div className="mx-auto max-w-7xl px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-indigo-600 to-fuchsia-600 blur-md opacity-40" />
              <div className="relative h-10 w-10 rounded-xl bg-gradient-to-br from-indigo-600 via-violet-600 to-fuchsia-600 text-white flex items-center justify-center font-extrabold shadow-md">
                SI
              </div>
            </div>

            <div className="leading-tight">
              <div className="text-sm font-semibold text-slate-900">
                Schema Intelligence Layer{" "}
                <span className="text-slate-500">• ACIES Global</span>
              </div>
              <div className="text-xs text-slate-500">
                Workspace • Metadata • Mapping • Chatbot
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <TopPill text="Postgres" />
            <TopPill text="ACIES Global" />
          </div>
        </div>
      </div>

      {/* BODY */}
      <div className="mx-auto max-w-7xl px-4 py-7">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* SIDEBAR */}
          <div className="lg:col-span-3">
            <div className="rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden">
              <div className="px-4 py-4 border-b border-slate-200 bg-gradient-to-r from-indigo-50 via-violet-50 to-fuchsia-50">
                <div className="text-xs text-slate-600 font-bold uppercase tracking-wide">
                  Modules
                </div>
                <div className="text-sm font-semibold text-slate-900 mt-1">
                  Workspace Tools
                </div>
              </div>

              <div className="p-3 space-y-2">
                <SideItem
                  active
                  title="Connect"
                  subtitle="Database configuration"
                  icon="🔌"
                />
                <SideItem
                  title="Metadata"
                  subtitle="Schema + table details"
                  icon="📊"
                />
                <SideItem
                  title="Mapping"
                  subtitle="Compare / map schemas"
                  icon="🧩"
                />
                <SideItem
                  title="Chatbot"
                  subtitle="Ask questions in NLP"
                  icon="✨"
                />
              </div>
              {/* QUICK SNAPSHOT */}
            <div className="mt-6 rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden">
              <div className="px-4 py-4 border-b border-slate-200 bg-white">
                <div className="text-sm font-semibold text-slate-900">
                  Connection Snapshot
                </div>
                <div className="text-xs text-slate-500 mt-1">
                  Current input values
                </div>
              </div>

              <div className="p-4 grid grid-cols-2 gap-3">
                <InfoTile label="Host" value={form.host || "-"} />
                <InfoTile label="Port" value={String(form.port || "-")} />
                <InfoTile label="Database" value={form.database || "-"} />
                <InfoTile label="Schema" value={form.schema_name || "-"} />
              </div>
            </div>
          </div>

              <div className="p-4 border-t border-slate-200 bg-slate-50">
                <div className="text-sm font-semibold text-slate-900">
                  Live Status
                </div>

                <div className="mt-3 flex flex-wrap gap-2">
                  <StatusChip
                    color={loading ? "amber" : "indigo"}
                    text={loading ? "Connecting..." : "Ready"}
                  />
                  <StatusChip
                    color={form.database ? "emerald" : "slate"}
                    text={form.database ? "DB Selected" : "DB Missing"}
                  />
                  <StatusChip color="violet" text="Secure" />
                </div>

                <div className="mt-4 text-xs text-slate-500 leading-relaxed">
                  🔒 Credentials are used only for workspace setup. Nothing is
                  stored in UI.
                </div>

                <div className="mt-3 text-[11px] font-semibold text-slate-400">
                  Powered by <span className="text-slate-600">ACIES Global</span>
                </div>
              </div>
            </div>

            

          {/* MAIN */}
          <div className="lg:col-span-9">
            {/* MAIN PANEL */}
            <div className="rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden">
              {/* Header */}
              <div className="px-6 py-5 border-b border-slate-200 bg-gradient-to-r from-indigo-50 via-violet-50 to-fuchsia-50">
                <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                  <div>
                    <h2 className="text-lg font-extrabold text-slate-900">
                      Connect Database
                    </h2>
                    <p className="text-sm text-slate-600 mt-1">
                      Connect once and use the workspace modules: Metadata,
                      Mapping and Chatbot.
                    </p>
                  </div>

                  <div className="flex items-center gap-2">
                    <StepPill active text="1. Connect" />
                    <StepPill text="2. Workspace" />
                    <StepPill text="3. Run Modules" />
                  </div>
                </div>
              </div>

              {/* Form */}
              <div className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <InputField
                    label="Host"
                    name="host"
                    value={form.host}
                    onChange={handleChange}
                    placeholder="localhost"
                  />

                  <InputField
                    label="Port"
                    name="port"
                    type="number"
                    value={form.port}
                    onChange={handleChange}
                    placeholder="5432"
                  />

                  <div className="md:col-span-2">
                    <InputField
                      label="Database Name"
                      name="database"
                      value={form.database}
                      onChange={handleChange}
                      placeholder="ehs_client"
                    />
                  </div>

                  <InputField
                    label="Username"
                    name="username"
                    value={form.username}
                    onChange={handleChange}
                    placeholder="postgres"
                  />

                  <InputField
                    label="Password"
                    name="password"
                    type="password"
                    value={form.password}
                    onChange={handleChange}
                    placeholder="••••••••"
                  />

                  <div className="md:col-span-2">
                    <InputField
                      label="Schema"
                      name="schema_name"
                      value={form.schema_name}
                      onChange={handleChange}
                      placeholder="public"
                    />
                  </div>
                </div>

                {/* ERROR */}
                {err && (
                  <div className="mt-5 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 font-semibold">
                    {err}
                  </div>
                )}

                {/* Action Bar */}
                <div className="mt-6 flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
                  <div className="flex items-center gap-2 text-xs text-slate-500">
                    <span className="h-2.5 w-2.5 rounded-full bg-emerald-500" />
                    Workspace modules will be enabled after connection.
                  </div>

                  <button
                    onClick={handleContinue}
                    disabled={loading || !form.database}
                    className="group inline-flex items-center justify-center gap-2 rounded-xl px-5 py-3 font-semibold text-white
                               bg-gradient-to-r from-indigo-600 via-violet-600 to-fuchsia-600
                               shadow-md shadow-indigo-500/20 hover:shadow-lg hover:shadow-fuchsia-500/20
                               transition disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {loading ? (
                      <>
                        <span className="h-4 w-4 rounded-full border-2 border-white/40 border-t-white animate-spin" />
                        Connecting...
                      </>
                    ) : (
                      <>
                        Enter Workspace
                        <span className="transition-transform group-hover:translate-x-1">
                          →
                        </span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>

            {/* MODULE CARDS */}
            <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
              <ToolCard
                title="Metadata"
                desc="Generate schema metadata + download output"
                tag="Module"
                color="indigo"
              />
              <ToolCard
                title="Mapping"
                desc="Compare source vs target schema mapping"
                tag="Module"
                color="violet"
              />
              <ToolCard
                title="Chatbot"
                desc="Ask questions and get smart summaries"
                tag="Module"
                color="fuchsia"
              />
            </div>

            <div className="mt-6 text-xs text-slate-400 flex items-center justify-between">
              <span>ACIES Global</span>
              <span className="font-medium text-slate-500">
                Tool Workspace • v1.0
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

/* ------------------ SMALL COMPONENTS ------------------ */

function TopPill({ text }) {
  return (
    <span className="text-xs px-2.5 py-1 rounded-full bg-slate-900/5 border border-slate-200 text-slate-700 font-semibold">
      {text}
    </span>
  );
}

function SideItem({ title, subtitle, active, icon }) {
  return (
    <div
      className={`group flex items-start gap-3 rounded-xl border px-3 py-3 transition ${
        active
          ? "border-indigo-200 bg-gradient-to-r from-indigo-50 via-violet-50 to-fuchsia-50 shadow-sm"
          : "border-slate-200 bg-white hover:bg-slate-50"
      }`}
    >
      <div
        className={`mt-0.5 h-9 w-9 rounded-xl flex items-center justify-center text-sm font-bold shadow-sm ${
          active
            ? "bg-gradient-to-br from-indigo-600 to-fuchsia-600 text-white"
            : "bg-slate-100 text-slate-700"
        }`}
      >
        {icon}
      </div>

      <div className="min-w-0">
        <div className="text-sm font-bold text-slate-900 truncate">{title}</div>
        <div className="text-xs text-slate-500 truncate mt-0.5">
          {subtitle}
        </div>
      </div>
    </div>
  );
}

function StatusChip({ text, color = "indigo" }) {
  const map = {
    indigo: "bg-indigo-600 text-white",
    emerald: "bg-emerald-600 text-white",
    violet: "bg-violet-600 text-white",
    fuchsia: "bg-fuchsia-600 text-white",
    amber: "bg-amber-500 text-white",
    slate: "bg-slate-600 text-white",
  };

  return (
    <span
      className={`text-xs px-2.5 py-1 rounded-full font-semibold shadow-sm ${
        map[color] || map.indigo
      }`}
    >
      {text}
    </span>
  );
}

function StepPill({ text, active }) {
  return (
    <span
      className={`text-xs px-3 py-1 rounded-full border font-semibold ${
        active
          ? "border-indigo-200 bg-white text-indigo-700 shadow-sm"
          : "border-white/40 bg-white/40 text-slate-700"
      }`}
    >
      {text}
    </span>
  );
}

function InfoTile({ label, value }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-3 shadow-sm">
      <div className="text-[11px] text-slate-500 font-semibold">{label}</div>
      <div className="text-sm font-extrabold text-slate-900 truncate mt-0.5">
        {value}
      </div>
    </div>
  );
}

function ToolCard({ title, desc, tag, color = "indigo" }) {
  const colorMap = {
    indigo: "from-indigo-50 to-indigo-100 bg-indigo-600",
    violet: "from-violet-50 to-violet-100 bg-violet-600",
    fuchsia: "from-fuchsia-50 to-fuchsia-100 bg-fuchsia-600",
  };

  const cfg = colorMap[color] || colorMap.indigo;

  return (
    <div className="rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden hover:shadow-md transition">
      <div
        className={`px-4 py-3 border-b border-slate-200 bg-gradient-to-r ${cfg
          .split(" ")
          .slice(0, 2)
          .join(" ")}`}
      >
        <div className="flex items-center justify-between">
          <div className="text-sm font-extrabold text-slate-900">{title}</div>
          <span
            className={`text-[11px] px-2 py-1 rounded-full text-white font-semibold ${
              cfg.split(" ").slice(-1)[0]
            }`}
          >
            {tag}
          </span>
        </div>
      </div>
      <div className="p-4 text-sm text-slate-600">{desc}</div>
    </div>
  );
}

function InputField({
  label,
  name,
  value,
  onChange,
  placeholder,
  type = "text",
}) {
  return (
    <div>
      <label className="text-sm font-bold text-slate-700">{label}</label>
      <input
        name={name}
        type={type}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        className="mt-1 w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-slate-900 placeholder:text-slate-400
                   shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-400 transition"
      />
    </div>
  );
}
