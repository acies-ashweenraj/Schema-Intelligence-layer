import { useMemo, useState } from "react";
import logo from "../assets/logo.png";
import {
  generateMetadata,
  getMetadataDownloadUrl,
  runHybridMapping,
  getMappingDownloadUrl,
} from "../api/client";

export default function WorkspacePage({ dbConfig, onExit, onGoChat }) {
  // ============================
  // SIDEBAR TABS
  // ============================
  const [activeTab, setActiveTab] = useState("metadata"); // metadata | mapping | chatbot

  const steps = [
    { key: "metadata", label: "Metadata" },
    { key: "mapping", label: "Mapping" },
    { key: "chatbot", label: "Chatbot" },
  ];

  const activeIndex = steps.findIndex((s) => s.key === activeTab);
  const progressPercent =
    activeIndex >= 0 ? Math.round(((activeIndex + 1) / steps.length) * 100) : 33;

  // ============================
  // METADATA STATE
  // ============================
  const [metaFormat, setMetaFormat] = useState("csv");
  const [metaLoading, setMetaLoading] = useState(false);
  const [metaError, setMetaError] = useState("");
  const [metaResult, setMetaResult] = useState(null);

  const metaDashboard = useMemo(() => {
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
    setMetaResult(null);

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
      setMetaError("❌ Metadata generation failed. Check DB / backend.");
    } finally {
      setMetaLoading(false);
    }
  }

  // ============================
  // MAPPING STATE
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
    setMappingResult(null);

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
  // ✅ MAPPING DASHBOARD (FIXED)
  // ============================
  const mappingDashboard = useMemo(() => {
    // backend returns:
    // mappingResult.table_match_count
    // mappingResult.column_match_count
    // mappingResult.details.preview_rows (if you added it in backend)
    const rows = mappingResult?.details?.preview_rows || [];

    const srcTables = new Set();
    const tgtTables = new Set();
    let confSum = 0;
    let confCount = 0;

    rows.forEach((r) => {
      if (r.source_table) srcTables.add(r.source_table);
      if (r.target_table) tgtTables.add(r.target_table);

      // take column_confidence if present
      if (typeof r.column_confidence === "number") {
        confSum += r.column_confidence;
        confCount += 1;
      }
    });

    const avgConfidence =
      confCount > 0 ? (confSum / confCount).toFixed(3) : "—";

    return {
      mappings: mappingResult?.table_match_count ?? "—",
      rows: mappingResult?.column_match_count ?? "—",
      sourceTables: srcTables.size > 0 ? srcTables.size : "—",
      targetTables: tgtTables.size > 0 ? tgtTables.size : "—",
      avgConfidence,
      generatedAt: mappingResult?.generated_at
        ? mappingResult.generated_at.slice(0, 19).replace("T", " ")
        : "—",
    };
  }, [mappingResult]);

  // ============================
  // RENDER
  // ============================
  return (
    <div className="min-h-screen w-full bg-slate-50">
      {/* TOP BAR */}
      <header className="sticky top-0 z-30 border-b border-slate-200 bg-white/80 backdrop-blur">
        <div className="mx-auto max-w-7xl px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="rounded-xl bg-slate-900 px-3 py-2 shadow-sm">
              <img src={logo} alt="ACIES Global" className="h-7 w-auto object-contain" />
            </div>

            <div className="leading-tight">
              <div className="text-sm font-extrabold text-slate-900">
                Schema Intelligence
              </div>
              <div className="text-xs text-slate-500">
                Workspace • Metadata • Mapping • Chatbot
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {onGoChat && (
              <button
                onClick={onGoChat}
                className="hidden sm:inline-flex items-center justify-center gap-2 rounded-xl px-4 py-2 font-semibold text-white
                           bg-gradient-to-r from-indigo-600 via-violet-600 to-fuchsia-600
                           shadow-md shadow-indigo-500/20 hover:shadow-lg hover:shadow-fuchsia-500/20 transition"
              >
                💬 Chatbot
              </button>
            )}

            <button
              onClick={onExit}
              className="rounded-xl px-4 py-2 bg-red-50 border border-red-200 text-red-700 font-semibold hover:bg-red-100 transition"
            >
              Exit
            </button>
          </div>
        </div>
      </header>

      {/* BODY */}
      <div className="mx-auto max-w-7xl px-4 py-7">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* SIDEBAR */}
          <aside className="lg:col-span-3 space-y-6">
            {/* MODULES */}
            <div className="rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden">
              <div className="px-4 py-4 border-b border-slate-200 bg-gradient-to-r from-indigo-50 via-violet-50 to-fuchsia-50">
                <div className="text-xs text-slate-600 font-bold uppercase tracking-wide">
                  Modules
                </div>
                <div className="text-sm font-extrabold text-slate-900 mt-1">
                  Workspace Tools
                </div>
              </div>

              <div className="p-3 space-y-2">
                <SideTab
                  active={activeTab === "metadata"}
                  title="Metadata"
                  subtitle="Generate schema output"
                  icon="📄"
                  onClick={() => setActiveTab("metadata")}
                />

                <SideTab
                  active={activeTab === "mapping"}
                  title="Mapping"
                  subtitle="Compare schemas"
                  icon="🧩"
                  onClick={() => setActiveTab("mapping")}
                />

                <SideTab
                  active={activeTab === "chatbot"}
                  title="Chatbot"
                  subtitle="Quick insights summary"
                  icon="✨"
                  onClick={() => setActiveTab("chatbot")}
                />
              </div>
            </div>

            {/* STATUS + PROGRESS */}
            <div className="rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden">
              <div className="px-4 py-4 border-b border-slate-200">
                <div className="text-sm font-extrabold text-slate-900">
                  Status
                </div>
                <div className="text-xs text-slate-500 mt-1">
                  Step {activeIndex + 1} of {steps.length} • {progressPercent}%
                </div>

                <div className="mt-3 h-2 rounded-full bg-slate-100 overflow-hidden">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-indigo-600 via-violet-600 to-fuchsia-600 transition-all"
                    style={{ width: `${progressPercent}%` }}
                  />
                </div>
              </div>

              <div className="p-4 space-y-3">
                <div className="flex flex-wrap gap-2">
                  <StatusChip color="emerald" text="Connected" />
                </div>

                <div className="rounded-xl border border-slate-200 bg-slate-50 p-3">
                  <div className="text-xs font-bold text-slate-600">
                    Source DB
                  </div>
                  <div className="mt-2 space-y-2">
                    <RowItem label="Host" value={dbConfig?.host || "—"} />
                    <RowItem label="Port" value={String(dbConfig?.port || "—")} />
                    <RowItem label="Database" value={dbConfig?.database || "—"} />
                    <RowItem label="Schema" value={dbConfig?.schema_name || "—"} />
                  </div>
                </div>
              </div>
            </div>
          </aside>

          {/* MAIN */}
          <main className="lg:col-span-9 space-y-6">
            {/* METADATA TAB */}
            {activeTab === "metadata" && (
              <>
                {/* DASHBOARD */}
                <div className="rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden">
                  <div className="px-6 py-5 border-b border-slate-200 bg-gradient-to-r from-indigo-50 via-violet-50 to-fuchsia-50">
                    <h2 className="text-lg font-extrabold text-slate-900">
                      Dashboard
                    </h2>
                    <p className="text-sm text-slate-600 mt-1">
                      Summary from generated metadata.
                    </p>
                  </div>

                  <div className="p-6 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                    <StatCard title="No. of Tables" value={metaDashboard.tables} sub="Detected" />
                    <StatCard title="No. of Columns" value={metaDashboard.columns} sub="All tables" />
                    <StatCard title="Relationships" value={metaDashboard.relationships} sub="Detected" />
                    <StatCard title="Generated At" value={metaDashboard.generatedAt} sub="UTC" />
                  </div>
                </div>

                {/* GENERATOR */}
                <div className="rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden">
                  <div className="px-6 py-5 border-b border-slate-200 bg-gradient-to-r from-indigo-50 via-violet-50 to-fuchsia-50">
                    <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                      <div>
                        <h2 className="text-lg font-extrabold text-slate-900">
                          Metadata Generator
                        </h2>
                        <p className="text-sm text-slate-600 mt-1">
                          Generate schema metadata and download output.
                        </p>
                      </div>

                      <button
                        onClick={handleGenerateMetadata}
                        disabled={metaLoading}
                        className="inline-flex items-center justify-center gap-2 rounded-xl px-5 py-3 font-semibold text-white
                                   bg-gradient-to-r from-indigo-600 via-violet-600 to-fuchsia-600
                                   shadow-md shadow-indigo-500/20 hover:shadow-lg hover:shadow-fuchsia-500/20
                                   transition disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {metaLoading ? (
                          <>
                            <span className="h-4 w-4 rounded-full border-2 border-white/40 border-t-white animate-spin" />
                            Generating...
                          </>
                        ) : (
                          <>⚡ Generate</>
                        )}
                      </button>
                    </div>
                  </div>

                  <div className="p-6 grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
                      <div className="text-sm font-extrabold text-slate-900">
                        Settings
                      </div>

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
                          className="mt-5 inline-flex justify-center w-full rounded-xl px-4 py-3
                                     bg-emerald-50 border border-emerald-200 text-emerald-700 font-extrabold
                                     hover:bg-emerald-100 transition"
                        >
                          ⬇ Download Metadata
                        </a>
                      )}
                    </div>

                    <PreviewBox data={metaResult} />
                  </div>
                </div>
              </>
            )}

            {/* MAPPING TAB */}
            {activeTab === "mapping" && (
              <>
                {/* DASHBOARD */}
                <div className="rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden">
                  <div className="px-6 py-5 border-b border-slate-200 bg-gradient-to-r from-indigo-50 via-violet-50 to-fuchsia-50">
                    <h2 className="text-lg font-extrabold text-slate-900">
                      Dashboard
                    </h2>
                    <p className="text-sm text-slate-600 mt-1">
                      Summary from generated mapping output.
                    </p>
                  </div>

                  <div className="p-6 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
                    <StatCard title="No. of Mappings" value={mappingDashboard.mappings} sub="Unique table pairs" />
                    <StatCard title="Rows" value={mappingDashboard.rows} sub="Column matches" />
                    <StatCard title="No. of Source Tables" value={mappingDashboard.sourceTables} sub="Unique" />
                    <StatCard title="No. of Target Tables" value={mappingDashboard.targetTables} sub="Unique" />
                    <StatCard title="Avg Confidence" value={mappingDashboard.avgConfidence} sub="Score" />
                  </div>
                </div>

                {/* MAPPING TOOL */}
                <div className="rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden">
                  <div className="px-6 py-5 border-b border-slate-200 bg-gradient-to-r from-indigo-50 via-violet-50 to-fuchsia-50">
                    <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                      <div>
                        <h2 className="text-lg font-extrabold text-slate-900">
                          Hybrid Mapping
                        </h2>
                        <p className="text-sm text-slate-600 mt-1">
                          Map source schema to target schema and export output.
                        </p>
                      </div>

                      <button
                        onClick={handleRunMapping}
                        disabled={mappingLoading || !targetCfg.database}
                        className="inline-flex items-center justify-center gap-2 rounded-xl px-5 py-3 font-semibold text-white
                                 bg-gradient-to-r from-indigo-600 via-violet-600 to-fuchsia-600
                                 shadow-md shadow-indigo-500/20 hover:shadow-lg hover:shadow-fuchsia-500/20
                                 transition disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {mappingLoading ? (
                          <>
                            <span className="h-4 w-4 rounded-full border-2 border-white/40 border-t-white animate-spin" />
                            Running...
                          </>
                        ) : (
                          <>🧩 Run Mapping</>
                        )}
                      </button>
                    </div>
                  </div>

                  <div className="p-6 grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Target Config */}
                    <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
                      <div className="text-sm font-extrabold text-slate-900">
                        Target Database
                      </div>

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
                          href={getMappingDownloadUrl(mappingResult.saved_file)}
                          className="mt-5 inline-flex justify-center w-full rounded-xl px-4 py-3
                                   bg-emerald-50 border border-emerald-200 text-emerald-700 font-extrabold
                                   hover:bg-emerald-100 transition"
                        >
                          ⬇ Download Mapping
                        </a>
                      )}
                    </div>

                    <PreviewBox data={mappingResult} />
                  </div>
                </div>
              </>
            )}

            {/* CHATBOT TAB */}
            {activeTab === "chatbot" && (
              <div className="rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden">
                <div className="px-6 py-5 border-b border-slate-200 bg-gradient-to-r from-indigo-50 via-violet-50 to-fuchsia-50">
                  <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                    <div>
                      <h2 className="text-lg font-extrabold text-slate-900">
                        Chatbot
                      </h2>
                      <p className="text-sm text-slate-600 mt-1">
                        Get quick insights through summary of your data.
                      </p>
                    </div>

                    {onGoChat ? (
                      <button
                        onClick={onGoChat}
                        className="inline-flex items-center justify-center gap-2 rounded-xl px-5 py-3 font-semibold text-white
                                   bg-gradient-to-r from-indigo-600 via-violet-600 to-fuchsia-600
                                   shadow-md shadow-indigo-500/20 hover:shadow-lg hover:shadow-fuchsia-500/20 transition"
                      >
                        💬 Open Chatbot
                      </button>
                    ) : (
                      <StatusChip color="slate" text="Not Available" />
                    )}
                  </div>
                </div>

                <div className="p-6">
                  <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
                    <div className="text-sm font-extrabold text-slate-900">
                      Chat Assistant Ready
                    </div>
                    <div className="text-xs text-slate-500 mt-1">
                      Get instant insights from your data with smart summaries.
                    </div>

                    <div className="mt-4 flex flex-wrap gap-2">
                      <StatusChip color="emerald" text="Connected DB" />
                      <StatusChip color="violet" text="AI Enabled" />
                      <StatusChip color="indigo" text="Schema Context" />
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* FOOTER */}
            <div className="text-xs text-slate-400 flex items-center justify-between">
              <span className="inline-flex items-center gap-2">
                <img src={logo} alt="ACIES Global" className="h-4 w-auto" />
                ACIES Global
              </span>
              <span className="font-medium text-slate-500">
                Tool Workspace • v1.0
              </span>
            </div>
          </main>
        </div>
      </div>
    </div>
  );
}

/* ------------------ SMALL COMPONENTS ------------------ */

function SideTab({ title, subtitle, active, icon, onClick }) {
  return (
    <button
      onClick={onClick}
      type="button"
      className={`w-full text-left group flex items-start gap-3 rounded-xl border px-3 py-3 transition ${
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

      <div className="min-w-0 flex-1">
        <div className="flex items-center justify-between gap-2">
          <div className="text-sm font-extrabold text-slate-900 truncate">
            {title}
          </div>

          {active && (
            <span className="text-[10px] px-2 py-1 rounded-full bg-indigo-600 text-white font-bold">
              ACTIVE
            </span>
          )}
        </div>

        <div className="text-xs text-slate-500 truncate mt-0.5">{subtitle}</div>
      </div>
    </button>
  );
}

function StatusChip({ text, color = "indigo" }) {
  const map = {
    indigo: "bg-indigo-600 text-white",
    emerald: "bg-emerald-600 text-white",
    violet: "bg-violet-600 text-white",
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

function RowItem({ label, value }) {
  return (
    <div className="flex items-center justify-between gap-3">
      <span className="text-xs font-semibold text-slate-500">{label}</span>
      <span className="text-xs font-extrabold text-slate-900 truncate max-w-[140px] text-right">
        {value}
      </span>
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
        autoComplete="off"
        spellCheck={false}
        className="mt-1 w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-slate-900 placeholder:text-slate-400
                   shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-400 transition"
      />
    </div>
  );
}

/**
 * ✅ PreviewBox without black background
 */
function PreviewBox({ data }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white overflow-hidden shadow-sm">
      <div className="px-4 py-3 border-b border-slate-200 bg-slate-50">
        <p className="text-xs font-bold text-slate-700">Preview Output</p>
      </div>

      <pre className="text-xs p-4 text-slate-800 max-h-[420px] overflow-auto leading-relaxed bg-white">
        {data ? JSON.stringify(data, null, 2) : "Preview will appear here..."}
      </pre>
    </div>
  );
}

function StatCard({ title, value, sub }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <p className="text-sm font-semibold text-slate-500">{title}</p>
      <p className="text-2xl font-extrabold text-slate-900 mt-1">{value}</p>
      <p className="text-xs text-slate-400 mt-1">{sub}</p>
    </div>
  );
}
