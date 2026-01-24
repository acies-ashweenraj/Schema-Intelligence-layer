import { useEffect, useMemo, useState } from "react";
import {
  generateMetadata,
  getMetadataDownloadUrl,
  runHybridMapping,
} from "../api/client";

export default function WorkspacePage({ dbConfig, onExit, onGoChat }) {
  // ✅ Always start at top when Workspace opens
  useEffect(() => {
    window.scrollTo({ top: 0, left: 0, behavior: "instant" });
  }, []);

  // ============================
  // METADATA STATE
  // ============================
  const [metaFormat, setMetaFormat] = useState("csv");
  const [metaLoading, setMetaLoading] = useState(false);
  const [metaError, setMetaError] = useState("");
  const [metaResult, setMetaResult] = useState(null);

  const dashboard = useMemo(() => {
    const summary = metaResult?.summary || {};
    return {
      tables: summary?.table_count ?? "—",
      columns: summary?.column_count ?? "—",
      relationships: summary?.relationship_count ?? "—",
      generatedAt: metaResult?.generated_at
        ? metaResult.generated_at.slice(0, 19).replace("T", " ")
        : "—",
    };
  }, [metaResult]);

  async function handleGenerateMetadata() {
    setMetaLoading(true);
    setMetaError("");

    try {
      const payload = {
        db_type: dbConfig?.db_type || "postgres",
        host: dbConfig?.host,
        port: Number(dbConfig?.port || 5432),
        database: dbConfig?.database,
        username: dbConfig?.username,
        password: dbConfig?.password,
        schema_name: dbConfig?.schema_name || "public",
        output_format: metaFormat,
      };

      const res = await generateMetadata(payload);
      setMetaResult(res);
    } catch (err) {
      console.log("Metadata error:", err?.response?.data || err);
      setMetaError("❌ Metadata generation failed. Check DB details / backend.");
    } finally {
      setMetaLoading(false);
    }
  }

  // ============================
  // MAPPING STATE (TYPING FIXED)
  // ============================
  const [mapFormat, setMapFormat] = useState("csv");
  const [mappingLoading, setMappingLoading] = useState(false);
  const [mappingError, setMappingError] = useState("");
  const [mappingResult, setMappingResult] = useState(null);

  const [targetCfg, setTargetCfg] = useState({
    db_type: "postgres",
    host: "localhost",
    port: "5432",
    database: "",
    username: "postgres",
    password: "",
    schema_name: "public",
  });

  function handleTargetChange(e) {
    const { name, value } = e.target;
    setTargetCfg((prev) => ({
      ...prev,
      [name]: value,
    }));
  }

  async function handleRunMapping() {
    setMappingLoading(true);
    setMappingError("");

    try {
      const payload = {
        src_cfg: {
          db_type: dbConfig?.db_type || "postgres",
          host: dbConfig?.host,
          port: Number(dbConfig?.port || 5432),
          database: dbConfig?.database,
          username: dbConfig?.username,
          password: dbConfig?.password,
          schema_name: dbConfig?.schema_name || "public",
        },
        tgt_cfg: {
          db_type: targetCfg.db_type,
          host: targetCfg.host,
          port: Number(targetCfg.port || 5432),
          database: targetCfg.database,
          username: targetCfg.username,
          password: targetCfg.password,
          schema_name: targetCfg.schema_name || "public",
        },
        qdrant_host: "localhost",
        qdrant_port: 6333,
        top_k_dense: 5,
        output_format: mapFormat,
      };

      const res = await runHybridMapping(payload);
      setMappingResult(res);
    } catch (err) {
      console.log("Mapping error:", err?.response?.data || err);
      setMappingError("❌ Mapping failed. Check target DB & backend logs.");
    } finally {
      setMappingLoading(false);
    }
  }

  // ============================
  // UI COMPONENTS
  // ============================
  function Chip({ children, tone = "gray" }) {
    const tones = {
      gray: "bg-slate-50 border-slate-200 text-slate-700",
      green: "bg-emerald-50 border-emerald-200 text-emerald-700",
      blue: "bg-sky-50 border-sky-200 text-sky-700",
      indigo: "bg-indigo-50 border-indigo-200 text-indigo-700",
      red: "bg-red-50 border-red-200 text-red-700",
      violet: "bg-violet-50 border-violet-200 text-violet-700",
    };

    return (
      <span
        className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold border ${tones[tone]}`}
      >
        {children}
      </span>
    );
  }

  function SectionCard({ title, desc, rightSlot, children }) {
    return (
      <section className="rounded-3xl border border-slate-200 bg-white shadow-sm overflow-hidden">
        <div className="px-6 py-5 border-b border-slate-200 bg-gradient-to-r from-indigo-50 via-violet-50 to-fuchsia-50">
          <div className="flex items-start justify-between gap-4 flex-wrap">
            <div>
              <h2 className="text-lg font-extrabold text-slate-900">{title}</h2>
              <p className="text-slate-600 mt-1 text-sm">{desc}</p>
            </div>
            {rightSlot}
          </div>
        </div>
        <div className="p-6">{children}</div>
      </section>
    );
  }

  function GradientButton({ children, className = "", ...props }) {
    return (
      <button
        {...props}
        className={`inline-flex items-center justify-center gap-2 rounded-2xl px-5 py-3 font-semibold text-white
          bg-gradient-to-r from-indigo-600 via-violet-600 to-fuchsia-600
          shadow-md shadow-indigo-500/20 hover:shadow-lg hover:shadow-fuchsia-500/20
          transition disabled:opacity-50 disabled:cursor-not-allowed ${className}`}
      >
        {children}
      </button>
    );
  }

  function PreviewBox({ data }) {
    return (
      <div className="rounded-2xl border border-slate-200 bg-slate-950 overflow-hidden shadow-sm">
        <div className="px-4 py-2 border-b border-white/10 bg-gradient-to-r from-indigo-600 via-violet-600 to-fuchsia-600">
          <p className="text-xs font-semibold text-white/90">Preview Output</p>
        </div>

        <pre className="text-xs p-4 text-slate-100 max-h-[340px] overflow-auto leading-relaxed">
          {data ? JSON.stringify(data, null, 2) : "Preview will appear here..."}
        </pre>
      </div>
    );
  }

  function StatCard({ title, value, sub }) {
    return (
      <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
        <p className="text-sm font-semibold text-slate-500">{title}</p>
        <p className="text-2xl font-extrabold text-slate-900 mt-1">{value}</p>
        <p className="text-xs text-slate-400 mt-1">{sub}</p>
      </div>
    );
  }

  function InputField({ label, name, value, onChange, type = "text", placeholder }) {
    return (
      <div>
        <label className="text-xs font-bold text-slate-600">{label}</label>
        <input
          name={name}
          value={value}
          onChange={onChange}
          type={type}
          placeholder={placeholder}
          autoComplete="off"
          spellCheck={false}
          className="mt-1 w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-slate-900 placeholder:text-slate-400
                     shadow-sm outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-400 transition"
        />
      </div>
    );
  }

  // ============================
  // RENDER
  // ============================
  return (
    <div className="min-h-screen bg-slate-50">
      {/* TOP BAR */}
      <header className="sticky top-0 z-20 bg-white/85 backdrop-blur border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-indigo-600 to-fuchsia-600 blur-md opacity-35" />
              <div className="relative w-11 h-11 rounded-2xl bg-gradient-to-br from-indigo-600 via-violet-600 to-fuchsia-600 text-white flex items-center justify-center font-extrabold shadow">
                SI
              </div>
            </div>

            <div>
              <h1 className="text-lg font-extrabold text-slate-900">
                Schema Intelligence Workspace
              </h1>
              <p className="text-xs text-slate-500">
                Metadata Generator • Mapping Preview • Downloads
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <Chip tone="green">Connected</Chip>

            {onGoChat && (
              <GradientButton onClick={onGoChat} className="px-4 py-2">
                💬 Open Chatbot
              </GradientButton>
            )}

            <button
              onClick={onExit}
              className="rounded-2xl px-4 py-2 bg-red-50 border border-red-200 text-red-700 font-semibold hover:bg-red-100 transition"
            >
              Exit
            </button>
          </div>
        </div>
      </header>

      {/* MAIN */}
      <main className="max-w-7xl mx-auto px-6 py-8 space-y-8">
        {/* METADATA */}
        <SectionCard
          title="Metadata Generator"
          desc="Choose output format, generate metadata, preview it and download the file."
          rightSlot={
            <GradientButton onClick={handleGenerateMetadata} disabled={metaLoading}>
              {metaLoading ? (
                <>
                  <span className="h-4 w-4 rounded-full border-2 border-white/40 border-t-white animate-spin" />
                  Generating...
                </>
              ) : (
                <>⚡ Generate Metadata</>
              )}
            </GradientButton>
          }
        >
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="rounded-3xl border border-slate-200 bg-slate-50 p-5">
              <h3 className="font-extrabold text-slate-900">Settings</h3>

              <div className="mt-4">
                <label className="text-xs font-bold text-slate-600">
                  Output Format
                </label>
                <select
                  value={metaFormat}
                  onChange={(e) => setMetaFormat(e.target.value)}
                  className="mt-1 w-full rounded-xl border border-slate-200 bg-white px-4 py-3 outline-none
                             focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-400 transition shadow-sm"
                >
                  <option value="csv">CSV</option>
                  <option value="json">JSON</option>
                  <option value="xlsx">XLSX</option>
                </select>
              </div>

              {metaError && (
                <div className="mt-4 p-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm font-semibold">
                  {metaError}
                </div>
              )}

              {metaResult?.saved_file && (
                <a
                  href={getMetadataDownloadUrl(metaResult.saved_file)}
                  className="mt-5 inline-flex justify-center w-full rounded-2xl px-4 py-3
                             bg-emerald-50 border border-emerald-200 text-emerald-700 font-extrabold
                             hover:bg-emerald-100 transition"
                >
                  ⬇ Download Metadata File
                </a>
              )}
            </div>

            <div>
              <h3 className="font-extrabold text-slate-900 mb-3">Preview</h3>
              <PreviewBox data={metaResult} />
            </div>
          </div>
        </SectionCard>

        {/* DASHBOARD */}
        <SectionCard
          title="Dashboard"
          desc="Quick summary from generated metadata output."
          rightSlot={
            <div className="flex gap-2 flex-wrap">
              <Chip tone="indigo">{dbConfig?.db_type || "postgres"}</Chip>
              <Chip tone="blue">{dbConfig?.host || "localhost"}</Chip>
              <Chip tone="gray">Port: {dbConfig?.port || 5432}</Chip>
              <Chip tone="violet">Schema: {dbConfig?.schema_name || "public"}</Chip>
            </div>
          }
        >
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard title="Tables" value={dashboard.tables} sub="Schema" />
            <StatCard title="Columns" value={dashboard.columns} sub="All tables" />
            <StatCard title="Relationships" value={dashboard.relationships} sub="Detected" />
            <StatCard title="Generated At" value={dashboard.generatedAt} sub="UTC" />
          </div>
        </SectionCard>

        {/* MAPPING */}
        <SectionCard
          title="Hybrid Mapping"
          desc="Provide target DB, choose output format, run mapping and download output."
          rightSlot={
            <GradientButton
              onClick={handleRunMapping}
              disabled={mappingLoading || !targetCfg.database}
            >
              {mappingLoading ? (
                <>
                  <span className="h-4 w-4 rounded-full border-2 border-white/40 border-t-white animate-spin" />
                  Running...
                </>
              ) : (
                <>🧩 Run Mapping</>
              )}
            </GradientButton>
          }
        >
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Target DB Config */}
            <div className="rounded-3xl border border-slate-200 bg-slate-50 p-5">
              <h3 className="font-extrabold text-slate-900">Target Database</h3>

              <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
                <InputField
                  label="Host"
                  name="host"
                  value={targetCfg.host}
                  onChange={handleTargetChange}
                  placeholder="localhost"
                />

                <InputField
                  label="Port"
                  name="port"
                  type="text"
                  value={targetCfg.port}
                  onChange={handleTargetChange}
                  placeholder="5432"
                />

                <div className="md:col-span-2">
                  <InputField
                    label="Database"
                    name="database"
                    value={targetCfg.database}
                    onChange={handleTargetChange}
                    placeholder="target_database_name"
                  />
                </div>

                <InputField
                  label="Username"
                  name="username"
                  value={targetCfg.username}
                  onChange={handleTargetChange}
                  placeholder="postgres"
                />

                <InputField
                  label="Password"
                  name="password"
                  type="password"
                  value={targetCfg.password}
                  onChange={handleTargetChange}
                  placeholder="••••••••"
                />

                <div className="md:col-span-2">
                  <InputField
                    label="Schema"
                    name="schema_name"
                    value={targetCfg.schema_name}
                    onChange={handleTargetChange}
                    placeholder="public"
                  />
                </div>

                <div className="md:col-span-2">
                  <label className="text-xs font-bold text-slate-600">
                    Output Format
                  </label>
                  <select
                    value={mapFormat}
                    onChange={(e) => setMapFormat(e.target.value)}
                    className="mt-1 w-full rounded-xl border border-slate-200 bg-white px-4 py-3 outline-none
                               focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-400 transition shadow-sm"
                  >
                    <option value="csv">CSV</option>
                    <option value="json">JSON</option>
                    <option value="xlsx">XLSX</option>
                  </select>
                </div>
              </div>

              {mappingError && (
                <div className="mt-4 p-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm font-semibold">
                  {mappingError}
                </div>
              )}

              {mappingResult?.saved_file && (
                <a
                  href={`http://localhost:8000/mapping/download?path=${encodeURIComponent(
                    mappingResult.saved_file
                  )}`}
                  className="mt-5 inline-flex justify-center w-full rounded-2xl px-4 py-3
                             bg-emerald-50 border border-emerald-200 text-emerald-700 font-extrabold
                             hover:bg-emerald-100 transition"
                >
                  ⬇ Download Mapping File
                </a>
              )}
            </div>

            {/* Preview */}
            <div>
              <h3 className="font-extrabold text-slate-900 mb-3">Preview</h3>
              <PreviewBox data={mappingResult} />
            </div>
          </div>
        </SectionCard>
      </main>
    </div>
  );
}
