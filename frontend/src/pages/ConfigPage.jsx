// import { useState } from "react";
// import { generateMetadata } from "../api/client";
// import logo from "../assets/logo.png";

// export default function ConfigPage({ onConnected }) {
//   const [form, setForm] = useState({
//     db_type: "postgres",
//     host: "localhost",
//     port: 5432,
//     database: "",
//     username: "postgres",
//     password: "",
//     schema_name: "public",
//   });

//   const [loading, setLoading] = useState(false);
//   const [err, setErr] = useState("");

//   // Tabs
//   const [activeTab, setActiveTab] = useState("connect"); // connect | metadata | mapping | chatbot

//   function handleChange(e) {
//     const { name, value } = e.target;
//     setForm((p) => ({
//       ...p,
//       [name]: name === "port" ? Number(value) : value,
//     }));
//   }

//   async function handleContinue() {
//     setLoading(true);
//     setErr("");

//     try {
//       const payload = {
//         ...form,
//         output_format: "json",
//       };

//       const result = await generateMetadata(payload);
//       onConnected(form, result);
//     } catch (error) {
//       console.log("ERROR:", error?.response?.data || error);
//       setErr("❌ Failed to generate metadata. Please check DB details.");
//     } finally {
//       setLoading(false);
//     }
//   }

//   const steps = [
//     { key: "connect", label: "Connect" },
//     { key: "metadata", label: "Metadata" },
//     { key: "mapping", label: "Mapping" },
//     { key: "chatbot", label: "Chatbot" },
//   ];

//   const activeIndex = steps.findIndex((s) => s.key === activeTab);
//   const progressPercent =
//     activeIndex >= 0 ? Math.round(((activeIndex + 1) / steps.length) * 100) : 25;

//   const isConnectedReady = !!form.database && !loading;

//   return (
//     <div className="min-h-screen w-full bg-slate-50">
//       {/* TOP BAR */}
//       <header className="sticky top-0 z-30 border-b border-slate-200 bg-white/80 backdrop-blur">
//         <div className="mx-auto max-w-7xl px-4 py-3 flex items-center justify-between">
//           {/* Left */}
//           <div className="flex items-center gap-3">
//             <div className="rounded-xl bg-slate-900 px-3 py-2 shadow-sm">
//               <img
//                 src={logo}
//                 alt="ACIES Global"
//                 className="h-7 w-auto object-contain"
//               />
//             </div>

//             <div className="leading-tight">
//               <div className="text-sm font-extrabold text-slate-900">
//                 Schema Intelligence{" "}
//                 <span className="text-slate-500 font-semibold">• ACIES Global</span>
//               </div>
//               <div className="text-xs text-slate-500">
//                 Connect once • Use Metadata • Mapping • Chatbot
//               </div>
//             </div>
//           </div>

//           {/* Right */}
//           <div className="hidden sm:flex items-center gap-2">
//             <TopPill text="Postgres" />
//           </div>
//         </div>
//       </header>

//       {/* BODY */}
//       <div className="mx-auto max-w-7xl px-4 py-7">
//         <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
//           {/* LEFT SIDEBAR */}
//           <aside className="lg:col-span-3 space-y-6">
//             {/* MODULES */}
//             <div className="rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden">
//               <div className="px-4 py-4 border-b border-slate-200">
//                 <div className="text-xs text-slate-500 font-bold uppercase tracking-wide">
//                   Navigation
//                 </div>
//                 <div className="text-sm font-extrabold text-slate-900 mt-1">
//                   Workspace Modules
//                 </div>
//               </div>

//               <div className="p-2 space-y-1">
//                 <SideTab
//                   active={activeTab === "connect"}
//                   title="Connect"
//                   subtitle="Source database setup"
//                   icon="🔌"
//                   onClick={() => setActiveTab("connect")}
//                 />
//                 <SideTab
//                   active={activeTab === "metadata"}
//                   title="Metadata"
//                   subtitle="Generate schema metadata"
//                   icon="📄"
//                   onClick={() => setActiveTab("metadata")}
//                 />
//                 <SideTab
//                   active={activeTab === "mapping"}
//                   title="Mapping"
//                   subtitle="Map source → target"
//                   icon="🧩"
//                   onClick={() => setActiveTab("mapping")}
//                 />
//                 <SideTab
//                   active={activeTab === "chatbot"}
//                   title="Chatbot"
//                   subtitle="Quick insights & summary"
//                   icon="✨"
//                   onClick={() => setActiveTab("chatbot")}
//                 />
//               </div>
//             </div>

//             {/* STATUS */}
//             <div className="rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden">
//               <div className="px-4 py-4 border-b border-slate-200">
//                 <div className="flex items-center justify-between">
//                   <div>
//                     <div className="text-sm font-extrabold text-slate-900">
//                       Workspace Status
//                     </div>
//                     <div className="text-xs text-slate-500 mt-1">
//                       Step {activeIndex + 1} / {steps.length}
//                     </div>
//                   </div>

//                   <span className="text-xs font-bold text-slate-700">
//                     {progressPercent}%
//                   </span>
//                 </div>

//                 {/* Progress bar */}
//                 <div className="mt-3 h-2 rounded-full bg-slate-100 overflow-hidden">
//                   <div
//                     className="h-full rounded-full bg-gradient-to-r from-indigo-600 via-violet-600 to-fuchsia-600 transition-all"
//                     style={{ width: `${progressPercent}%` }}
//                   />
//                 </div>
//               </div>

//               <div className="p-4 space-y-4">
//                 <div className="flex flex-wrap gap-2">
//                   <StatusChip
//                     color={loading ? "amber" : "indigo"}
//                     text={loading ? "Connecting..." : "Ready"}
//                   />
//                   <StatusChip
//                     color={form.database ? "emerald" : "slate"}
//                     text={form.database ? "DB Selected" : "DB Missing"}
//                   />
                
//                 </div>

//                 <div className="rounded-xl border border-slate-200 bg-slate-50 p-3">
//                   <div className="text-xs font-bold text-slate-600">
//                     Connection Summary
//                   </div>

//                   <div className="mt-2 space-y-2">
//                     <RowItem label="Host" value={form.host || "—"} />
//                     <RowItem label="Port" value={String(form.port || "—")} />
//                     <RowItem label="Database" value={form.database || "—"} />
//                     <RowItem label="Schema" value={form.schema_name || "—"} />
//                   </div>
//                 </div>

//                 <div className="text-[11px] text-slate-500 leading-relaxed">
//                   🔒 Credentials are used only for workspace setup. Nothing is stored in UI.
//                 </div>
//               </div>
//             </div>
//           </aside>

//           {/* MAIN CONTENT */}
//           <main className="lg:col-span-9 space-y-6">
//             {/* MAIN PANEL */}
//             <div className="rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden">
//               {/* Header */}
//               <div className="px-6 py-5 border-b border-slate-200 bg-gradient-to-r from-indigo-50 via-violet-50 to-fuchsia-50">
//                 <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
//                   <div>
//                     <h2 className="text-lg font-extrabold text-slate-900">
//                       {activeTab === "connect" && "Database Configuration"}
//                       {activeTab === "metadata" && "Metadata Module"}
//                       {activeTab === "mapping" && "Mapping Module"}
//                       {activeTab === "chatbot" && "Chatbot Module"}
//                     </h2>

//                     <p className="text-sm text-slate-600 mt-1">
//                       {activeTab === "connect" &&
//                         "Configure your source database to unlock the workspace tools."}
//                       {activeTab === "metadata" &&
//                         "Generate schema metadata and download structured output."}
//                       {activeTab === "mapping" &&
//                         "Compare schemas and generate mapping output between databases."}
//                       {activeTab === "chatbot" &&
//                         "Get quick insights through summary of your data using natural language queries."}
//                     </p>
//                   </div>

//                   <div className="flex items-center gap-2 flex-wrap">
//                     <StepPill active={activeTab === "connect"} text="Connect" />
//                     <StepPill active={activeTab === "metadata"} text="Metadata" />
//                     <StepPill active={activeTab === "mapping"} text="Mapping" />
//                     <StepPill active={activeTab === "chatbot"} text="Chatbot" />
//                   </div>
//                 </div>
//               </div>

//               {/* BODY */}
//               <div className="p-6">
//                 {/* CONNECT TAB */}
//                 {activeTab === "connect" && (
//                   <>
//                     <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
//                       <InputField
//                         label="Host"
//                         name="host"
//                         value={form.host}
//                         onChange={handleChange}
//                         placeholder="localhost"
//                       />

//                       <InputField
//                         label="Port"
//                         name="port"
//                         type="number"
//                         value={form.port}
//                         onChange={handleChange}
//                         placeholder="5432"
//                       />

//                       <div className="md:col-span-2">
//                         <InputField
//                           label="Database Name"
//                           name="database"
//                           value={form.database}
//                           onChange={handleChange}
//                           placeholder="ehs_client"
//                         />
//                       </div>

//                       <InputField
//                         label="Username"
//                         name="username"
//                         value={form.username}
//                         onChange={handleChange}
//                         placeholder="postgres"
//                       />

//                       <InputField
//                         label="Password"
//                         name="password"
//                         type="password"
//                         value={form.password}
//                         onChange={handleChange}
//                         placeholder="••••••••"
//                       />

//                       <div className="md:col-span-2">
//                         <InputField
//                           label="Schema"
//                           name="schema_name"
//                           value={form.schema_name}
//                           onChange={handleChange}
//                           placeholder="public"
//                         />
//                       </div>
//                     </div>

//                     {/* ERROR */}
//                     {err && (
//                       <div className="mt-5 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 font-semibold">
//                         {err}
//                       </div>
//                     )}

//                     {/* ACTION */}
//                     <div className="mt-6 flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
//                       <div className="flex items-center gap-2 text-xs text-slate-500">
//                         <span className="h-2.5 w-2.5 rounded-full bg-emerald-500" />
//                         Enter workspace after successful connection.
//                       </div>

//                       <button
//                         onClick={handleContinue}
//                         disabled={loading || !form.database}
//                         className="group inline-flex items-center justify-center gap-2 rounded-xl px-5 py-3 font-semibold text-white
//                                    bg-gradient-to-r from-indigo-600 via-violet-600 to-fuchsia-600
//                                    shadow-md shadow-indigo-500/20 hover:shadow-lg hover:shadow-fuchsia-500/20
//                                    transition disabled:opacity-50 disabled:cursor-not-allowed"
//                       >
//                         {loading ? (
//                           <>
//                             <span className="h-4 w-4 rounded-full border-2 border-white/40 border-t-white animate-spin" />
//                             Connecting...
//                           </>
//                         ) : (
//                           <>
//                             Enter Workspace
//                             <span className="transition-transform group-hover:translate-x-1">
//                               →
//                             </span>
//                           </>
//                         )}
//                       </button>
//                     </div>
//                   </>
//                 )}

//                 {/* LOCKED MODULES */}
//                 {activeTab !== "connect" && (
//                   <ModuleLockedPanel
//                     title={
//                       activeTab === "metadata"
//                         ? "Metadata Generator"
//                         : activeTab === "mapping"
//                         ? "Schema Mapping"
//                         : "Chatbot"
//                     }
//                     desc={
//                       activeTab === "metadata"
//                         ? "Generate schema metadata, preview output and download the file."
//                         : activeTab === "mapping"
//                         ? "Generate mapping output between source and target schemas."
//                         : "Get quick insights through summary of your data."
//                     }
//                     ready={isConnectedReady}
//                     tip="Connect your database first. Then this module will be available inside the Workspace."
//                   />
//                 )}
//               </div>
//             </div>

//             {/* FOOTER */}
//             <div className="text-xs text-slate-400 flex items-center justify-between">
//               <span className="inline-flex items-center gap-2">
//                 <img src={logo} alt="ACIES Global" className="h-4 w-auto" />
//                 ACIES Global
//               </span>
//               <span className="font-medium text-slate-500">
//                 Tool Workspace • v1.0
//               </span>
//             </div>
//           </main>
//         </div>
//       </div>
//     </div>
//   );
// }

// /* ------------------ SMALL COMPONENTS ------------------ */

// function TopPill({ text }) {
//   return (
//     <span className="text-xs px-2.5 py-1 rounded-full bg-slate-900/5 border border-slate-200 text-slate-700 font-semibold">
//       {text}
//     </span>
//   );
// }

// function SideTab({ title, subtitle, active, icon, onClick }) {
//   return (
//     <button
//       onClick={onClick}
//       type="button"
//       className={`w-full text-left group flex items-start gap-3 rounded-xl border px-3 py-3 transition ${
//         active
//           ? "border-indigo-200 bg-gradient-to-r from-indigo-50 via-violet-50 to-fuchsia-50 shadow-sm"
//           : "border-slate-200 bg-white hover:bg-slate-50"
//       }`}
//     >
//       <div
//         className={`mt-0.5 h-9 w-9 rounded-xl flex items-center justify-center text-sm font-bold shadow-sm ${
//           active
//             ? "bg-gradient-to-br from-indigo-600 to-fuchsia-600 text-white"
//             : "bg-slate-100 text-slate-700"
//         }`}
//       >
//         {icon}
//       </div>

//       <div className="min-w-0 flex-1">
//         <div className="flex items-center justify-between gap-2">
//           <div className="text-sm font-extrabold text-slate-900 truncate">
//             {title}
//           </div>

//           {active && (
//             <span className="text-[10px] px-2 py-1 rounded-full bg-indigo-600 text-white font-bold">
//               ACTIVE
//             </span>
//           )}
//         </div>

//         <div className="text-xs text-slate-500 truncate mt-0.5">{subtitle}</div>
//       </div>
//     </button>
//   );
// }

// function StatusChip({ text, color = "indigo" }) {
//   const map = {
//     indigo: "bg-indigo-600 text-white",
//     emerald: "bg-emerald-600 text-white",
//     violet: "bg-violet-600 text-white",
//     amber: "bg-amber-500 text-white",
//     slate: "bg-slate-600 text-white",
//   };

//   return (
//     <span
//       className={`text-xs px-2.5 py-1 rounded-full font-semibold shadow-sm ${
//         map[color] || map.indigo
//       }`}
//     >
//       {text}
//     </span>
//   );
// }

// function StepPill({ text, active }) {
//   return (
//     <span
//       className={`text-xs px-3 py-1 rounded-full border font-semibold transition ${
//         active
//           ? "border-indigo-200 bg-white text-indigo-700 shadow-sm"
//           : "border-white/40 bg-white/40 text-slate-700"
//       }`}
//     >
//       {text}
//     </span>
//   );
// }

// function RowItem({ label, value }) {
//   return (
//     <div className="flex items-center justify-between gap-3">
//       <span className="text-xs font-semibold text-slate-500">{label}</span>
//       <span className="text-xs font-extrabold text-slate-900 truncate max-w-[140px] text-right">
//         {value}
//       </span>
//     </div>
//   );
// }

// function InputField({
//   label,
//   name,
//   value,
//   onChange,
//   placeholder,
//   type = "text",
// }) {
//   return (
//     <div>
//       <label className="text-sm font-bold text-slate-700">{label}</label>
//       <input
//         name={name}
//         type={type}
//         value={value}
//         onChange={onChange}
//         placeholder={placeholder}
//         autoComplete="off"
//         spellCheck={false}
//         className="mt-1 w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-slate-900 placeholder:text-slate-400
//                    shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-400 transition"
//       />
//     </div>
//   );
// }

// function ModuleLockedPanel({ title, desc, tip, ready }) {
//   return (
//     <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
//       <div className="flex items-start justify-between gap-4 flex-wrap">
//         <div>
//           <div className="text-sm font-extrabold text-slate-900">{title}</div>
//           <div className="text-xs text-slate-500 mt-1">{desc}</div>
//         </div>

//         <span
//           className={`text-xs px-3 py-1 rounded-full font-bold ${
//             ready ? "bg-emerald-600 text-white" : "bg-slate-600 text-white"
//           }`}
//         >
//           {ready ? "READY" : "LOCKED"}
//         </span>
//       </div>

//       <div className="mt-4 rounded-xl border border-slate-200 bg-white p-4">
//         <div className="text-xs font-semibold text-slate-700">
//           {ready ? "Connection verified ✅" : "Connection required 🔒"}
//         </div>
//         <div className="text-xs text-slate-500 mt-1">{tip}</div>
//       </div>
//     </div>
//   );
// }
// import { useState } from "react";
// import { generateMetadata } from "../api/client";
// import logo from "../assets/logo.png";

// export default function ConfigPage({ onConnected, onExit }) {
//   const [form, setForm] = useState({
//     db_type: "postgres",
//     host: "localhost",
//     port: 5432,
//     database: "",
//     username: "postgres",
//     password: "",
//     schema_name: "public",
//   });

//   const [loading, setLoading] = useState(false);
//   const [err, setErr] = useState("");
//   const [activeTab, setActiveTab] = useState("connect");

//   function handleChange(e) {
//     const { name, value } = e.target;
//     setForm((p) => ({
//       ...p,
//       [name]: name === "port" ? Number(value) : value,
//     }));
//   }

//   async function handleContinue() {
//     setLoading(true);
//     setErr("");

//     try {
//       const payload = { ...form, output_format: "json" };
//       const result = await generateMetadata(payload);
//       onConnected(form, result);
//     } catch (error) {
//       console.error(error);
//       setErr("❌ Failed to generate metadata. Please check DB details.");
//     } finally {
//       setLoading(false);
//     }
//   }

//   const steps = ["connect", "metadata", "mapping", "chatbot"];
//   const activeIndex = steps.indexOf(activeTab);
//   const progressPercent = Math.round(((activeIndex + 1) / steps.length) * 100);
//   const isConnectedReady = !!form.database && !loading;

//   return (
//     <div className="min-h-screen bg-slate-50">
//       {/* ================= HEADER ================= */}
//       <header className="sticky top-0 z-30 border-b bg-white/80 backdrop-blur">
//         <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
//           <div className="flex items-center gap-3">
//             <div className="bg-slate-900 rounded-xl px-3 py-2">
//               <img src={logo} alt="Logo" className="h-7" />
//             </div>
//             <div>
//               <p className="text-sm font-extrabold">
//                 Schema Intelligence
//                 <span className="text-slate-500 font-semibold"> • ACIES Global</span>
//               </p>
//               <p className="text-xs text-slate-500">
//                 Connect • Metadata • Mapping • Chatbot
//               </p>
//             </div>
//           </div>

//           <div className="flex items-center gap-3">
//             <TopPill text="Postgres" />
//             <button
//               onClick={onExit}
//               className="rounded-xl px-4 py-2 bg-red-50 border border-red-200
//                          text-red-700 font-semibold hover:bg-red-100 transition"
//             >
//               Exit
//             </button>
//           </div>
//         </div>
//       </header>

//       {/* ================= BODY ================= */}
//       <div className="max-w-7xl mx-auto px-4 py-7 grid grid-cols-1 lg:grid-cols-12 gap-6">
//         {/* ================= SIDEBAR ================= */}
//         <aside className="lg:col-span-3 space-y-6">
//           <Card title="Navigation" subtitle="Workspace Modules">
//             <SideTab icon="🔌" title="Connect" subtitle="Source database setup" active={activeTab === "connect"} onClick={() => setActiveTab("connect")} />
//             <SideTab icon="📄" title="Metadata" subtitle="Generate schema metadata" active={activeTab === "metadata"} onClick={() => setActiveTab("metadata")} />
//             <SideTab icon="🧩" title="Mapping" subtitle="Map source → target" active={activeTab === "mapping"} onClick={() => setActiveTab("mapping")} />
//             <SideTab icon="✨" title="Chatbot" subtitle="Insights & Q&A" active={activeTab === "chatbot"} onClick={() => setActiveTab("chatbot")} />
//           </Card>

//           <Card title="Workspace Status">
//             <div className="flex justify-between text-xs font-bold">
//               <span>Step {activeIndex + 1} / {steps.length}</span>
//               <span>{progressPercent}%</span>
//             </div>

//             <div className="mt-3 h-2 bg-slate-100 rounded-full overflow-hidden">
//               <div
//                 className="h-full bg-gradient-to-r from-indigo-600 to-fuchsia-600"
//                 style={{ width: `${progressPercent}%` }}
//               />
//             </div>

//             <div className="mt-4 flex flex-wrap gap-2">
//               <StatusChip text={loading ? "Connecting..." : "Ready"} color={loading ? "amber" : "indigo"} />
//               <StatusChip text={form.database ? "DB Selected" : "DB Missing"} color={form.database ? "emerald" : "slate"} />
//             </div>

//             <div className="mt-4 bg-slate-50 border rounded-xl p-3 text-xs">
//               <RowItem label="Host" value={form.host || "—"} />
//               <RowItem label="Port" value={form.port || "—"} />
//               <RowItem label="Database" value={form.database || "—"} />
//               <RowItem label="Schema" value={form.schema_name || "—"} />
//             </div>
//           </Card>
//         </aside>

//         {/* ================= MAIN ================= */}
//         <main className="lg:col-span-9">
//           <Card
//             title={
//               activeTab === "connect"
//                 ? "Database Configuration"
//                 : activeTab === "metadata"
//                 ? "Metadata Module"
//                 : activeTab === "mapping"
//                 ? "Mapping Module"
//                 : "Chatbot Module"
//             }
//             subtitle={
//               activeTab === "connect"
//                 ? "Configure your source database to unlock workspace tools."
//                 : activeTab === "metadata"
//                 ? "Generate schema metadata and export structured output."
//                 : activeTab === "mapping"
//                 ? "Create mappings between schemas."
//                 : "Ask questions and get insights from your data."
//             }
//             headerGradient
//           >
//             {activeTab === "connect" ? (
//               <>
//                 <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
//                   <InputField label="Host" name="host" value={form.host} onChange={handleChange} />
//                   <InputField label="Port" name="port" type="number" value={form.port} onChange={handleChange} />
//                   <InputField label="Database" name="database" value={form.database} onChange={handleChange} />
//                   <InputField label="Username" name="username" value={form.username} onChange={handleChange} />
//                   <InputField label="Password" name="password" type="password" value={form.password} onChange={handleChange} />
//                   <InputField label="Schema" name="schema_name" value={form.schema_name} onChange={handleChange} />
//                 </div>

//                 {err && (
//                   <div className="mt-4 bg-red-50 border border-red-200 p-3 rounded-xl text-red-700 font-semibold">
//                     {err}
//                   </div>
//                 )}

//                 <div className="mt-6 flex justify-end">
//                   <button
//                     onClick={handleContinue}
//                     disabled={!form.database || loading}
//                     className="rounded-xl px-6 py-3 font-semibold text-white
//                                bg-gradient-to-r from-indigo-600 to-fuchsia-600
//                                disabled:opacity-50"
//                   >
//                     {loading ? "Connecting..." : "Enter Workspace →"}
//                   </button>
//                 </div>
//               </>
//             ) : (
//               <ModuleLockedPanel
//                 ready={isConnectedReady}
//                 title="Module Locked"
//                 desc="Connect your database first to unlock this module."
//               />
//             )}
//           </Card>
//         </main>
//       </div>
//     </div>
//   );
// }

// /* ================= COMPONENTS ================= */

// function Card({ title, subtitle, children, headerGradient }) {
//   return (
//     <div className="rounded-2xl border bg-white shadow-sm overflow-hidden">
//       <div
//         className={`px-6 py-5 border-b ${
//           headerGradient
//             ? "bg-gradient-to-r from-indigo-50 to-fuchsia-50"
//             : ""
//         }`}
//       >
//         <p className="text-lg font-extrabold">{title}</p>
//         {subtitle && <p className="text-sm text-slate-600 mt-1">{subtitle}</p>}
//       </div>
//       <div className="p-6 space-y-4">{children}</div>
//     </div>
//   );
// }

// function TopPill({ text }) {
//   return (
//     <span className="text-xs px-3 py-1 rounded-full border bg-slate-100 font-semibold">
//       {text}
//     </span>
//   );
// }

// function SideTab({ icon, title, subtitle, active, onClick }) {
//   return (
//     <button
//       onClick={onClick}
//       className={`w-full flex gap-3 p-3 rounded-xl border transition ${
//         active
//           ? "bg-indigo-50 border-indigo-200"
//           : "bg-white border-slate-200 hover:bg-slate-50"
//       }`}
//     >
//       <span className="text-lg">{icon}</span>
//       <div className="text-left">
//         <p className="font-bold text-sm">{title}</p>
//         <p className="text-xs text-slate-500">{subtitle}</p>
//       </div>
//     </button>
//   );
// }

// function StatusChip({ text, color }) {
//   const map = {
//     indigo: "bg-indigo-600",
//     emerald: "bg-emerald-600",
//     amber: "bg-amber-500",
//     slate: "bg-slate-600",
//   };
//   return (
//     <span className={`text-xs px-3 py-1 rounded-full text-white font-bold ${map[color]}`}>
//       {text}
//     </span>
//   );
// }

// function RowItem({ label, value }) {
//   return (
//     <div className="flex justify-between">
//       <span className="text-xs text-slate-500">{label}</span>
//       <span className="text-xs font-bold">{value}</span>
//     </div>
//   );
// }

// function InputField({ label, name, value, onChange, type = "text" }) {
//   return (
//     <div>
//       <label className="text-sm font-bold">{label}</label>
//       <input
//         name={name}
//         value={value}
//         type={type}
//         onChange={onChange}
//         className="mt-1 w-full rounded-xl border px-4 py-3 focus:ring-2 focus:ring-indigo-500/20"
//       />
//     </div>
//   );
// }

// function ModuleLockedPanel({ title, desc, ready }) {
//   return (
//     <div className="rounded-xl border bg-slate-50 p-5">
//       <div className="flex justify-between items-center">
//         <div>
//           <p className="font-bold">{title}</p>
//           <p className="text-xs text-slate-500 mt-1">{desc}</p>
//         </div>
//         <span
//           className={`text-xs px-3 py-1 rounded-full font-bold ${
//             ready ? "bg-emerald-600 text-white" : "bg-slate-600 text-white"
//           }`}
//         >
//           {ready ? "READY" : "LOCKED"}
//         </span>
//       </div>
//     </div>
//   );
// }
// import { useState } from "react";
// import { generateMetadata } from "../api/client";
// import logo from "../assets/logo.png";

// export default function ConfigPage({ onConnected, onExit }) {
//   const [form, setForm] = useState({
//     db_type: "postgres",
//     host: "localhost",
//     port: 5432,
//     database: "",
//     username: "postgres",
//     password: "",
//     schema_name: "public",
//   });

//   const [loading, setLoading] = useState(false);
//   const [error, setError] = useState("");

//   function handleChange(e) {
//     const { name, value } = e.target;
//     setForm((p) => ({
//       ...p,
//       [name]: name === "port" ? Number(value) : value,
//     }));
//   }

//   async function handleConnect() {
//     setLoading(true);
//     setError("");

//     try {
//       const payload = { ...form, output_format: "json" };
//       const metadata = await generateMetadata(payload);
//       onConnected(form, metadata);
//     } catch (err) {
//       console.error(err);
//       setError("Unable to connect. Please verify database credentials.");
//     } finally {
//       setLoading(false);
//     }
//   }

//   const canConnect = !!form.database && !loading;

//   return (
//     <div className="min-h-screen bg-slate-100">
//       {/* ================= NAVBAR ================= */}
//       <header className="sticky top-0 z-40 bg-black border-b border-slate-800">
//         <div className="max-w-7xl mx-auto px-6 h-14 flex items-center justify-between">
//           <div className="flex items-center gap-3">
//             <img src={logo} className="h-7" />
//             <div className="leading-tight">
//               <p className="text-sm font-bold text-white">
//                 Schema Intelligence
//               </p>
//               <p className="text-[11px] text-slate-400">
//                 Secure database onboarding
//               </p>
//             </div>
//           </div>

//           <button
//             onClick={onExit}
//             className="px-4 py-2 rounded-lg bg-red-600 text-white
//                        text-sm font-semibold hover:bg-red-700 transition"
//           >
//             Exit
//           </button>
//         </div>
//       </header>

//       {/* ================= PAGE ================= */}
//       <main className="max-w-5xl mx-auto px-6 py-16">
//         <div className="relative">
//           {/* SOFT BACKDROP */}
//           <div className="absolute -inset-2 rounded-3xl bg-gradient-to-r from-indigo-200/40 to-fuchsia-200/40 blur-2xl" />

//           <div className="relative bg-white border border-slate-200 rounded-3xl shadow-2xl overflow-hidden">
//             {/* HEADER */}
//             <div className="px-12 py-10 border-b bg-gradient-to-r from-slate-50 to-white">
//               <h1 className="text-2xl font-extrabold text-slate-900">
//                 Connect Database
//               </h1>
//               <p className="mt-2 text-sm text-slate-600 max-w-2xl">
//                 Configure your source database to enable schema analysis,
//                 metadata extraction, intelligent mapping, and AI-powered
//                 exploration.
//               </p>
//             </div>

//             {/* BODY */}
//             <div className="px-12 py-10 space-y-12">
//               {/* ENGINE */}
//               <Section title="Database Engine">
//                 <div className="flex items-center gap-3">
//                   <EngineBadge />
//                   <span className="text-xs text-slate-500">
//                     Currently supported engine
//                   </span>
//                 </div>
//               </Section>

//               {/* CONNECTION */}
//               <Section title="Connection Details">
//                 <Panel>
//                   <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
//                     <Field
//                       label="Host"
//                       name="host"
//                       value={form.host}
//                       onChange={handleChange}
//                       hint="Hostname or IP address"
//                     />
//                     <Field
//                       label="Port"
//                       name="port"
//                       type="number"
//                       value={form.port}
//                       onChange={handleChange}
//                     />
//                     <Field
//                       label="Database Name"
//                       name="database"
//                       value={form.database}
//                       onChange={handleChange}
//                       required
//                     />
//                     <Field
//                       label="Schema"
//                       name="schema_name"
//                       value={form.schema_name}
//                       onChange={handleChange}
//                     />
//                   </div>
//                 </Panel>
//               </Section>

//               {/* AUTH */}
//               <Section title="Authentication">
//                 <Panel>
//                   <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
//                     <Field
//                       label="Username"
//                       name="username"
//                       value={form.username}
//                       onChange={handleChange}
//                     />
//                     <Field
//                       label="Password"
//                       name="password"
//                       type="password"
//                       value={form.password}
//                       onChange={handleChange}
//                     />
//                   </div>
//                 </Panel>
//               </Section>

//               {/* ERROR */}
//               {error && (
//                 <div className="rounded-xl border border-red-200 bg-red-50 px-5 py-4 text-sm text-red-700 font-semibold">
//                   {error}
//                 </div>
//               )}
//             </div>

//             {/* FOOTER */}
//             <div className="px-12 py-6 border-t bg-slate-50 flex justify-between items-center">
//               <div className="flex items-center gap-2 text-xs text-slate-500">
//                 <span>🔒</span>
//                 <span>Credentials are never stored</span>
//               </div>

//               <button
//                 onClick={handleConnect}
//                 disabled={!canConnect}
//                 className="px-12 py-3 rounded-xl font-bold text-white
//                            bg-gradient-to-r from-indigo-600 to-fuchsia-600
//                            hover:from-indigo-700 hover:to-fuchsia-700
//                            shadow-lg shadow-indigo-600/30
//                            disabled:opacity-50 disabled:cursor-not-allowed
//                            transition-all"
//               >
//                 {loading ? "Connecting…" : "Connect & Enter Workspace"}
//               </button>
//             </div>
//           </div>
//         </div>
//       </main>
//     </div>
//   );
// }

// /* ================= UI ================= */

// function Section({ title, children }) {
//   return (
//     <div>
//       <h2 className="text-xs font-extrabold tracking-widest text-slate-700 mb-4 uppercase">
//         {title}
//       </h2>
//       {children}
//     </div>
//   );
// }

// function Panel({ children }) {
//   return (
//     <div className="rounded-2xl border border-slate-200 bg-slate-50 p-6 shadow-inner">
//       {children}
//     </div>
//   );
// }

// function Field({
//   label,
//   name,
//   value,
//   onChange,
//   type = "text",
//   required,
//   hint,
// }) {
//   return (
//     <div className="group">
//       <label className="block text-sm font-bold text-slate-700 mb-1">
//         {label}
//         {required && <span className="text-red-500"> *</span>}
//       </label>

//       <input
//         name={name}
//         value={value}
//         type={type}
//         onChange={onChange}
//         className="w-full rounded-xl border border-slate-300 bg-white
//                    px-4 py-3 text-sm
//                    focus:outline-none focus:ring-2 focus:ring-indigo-500/30
//                    focus:border-indigo-500
//                    group-hover:border-slate-400
//                    transition"
//       />

//       {hint && (
//         <p className="mt-1 text-xs text-slate-500">{hint}</p>
//       )}
//     </div>
//   );
// }

// function EngineBadge() {
//   return (
//     <span className="inline-flex items-center gap-2 px-5 py-2 rounded-xl
//                      bg-slate-900 text-white font-bold text-sm shadow">
//        PostgreSQL
//     </span>
//   );
// }
import { useState } from "react";
import { v4 as uuidv4 } from "uuid";
import {
  generateMetadata,
  loadKG,
  initRAG,
} from "../api/client";
import logo from "../assets/logo.png";

/* ================= SESSION KEYS ================= */
const SESSION_KEY = "rag_session_id";
const KG_READY_KEY = "kg_initialized";
const NEO4J_CFG_KEY = "neo4j_cfg";

export default function ConfigPage({ onConnected, onExit }) {
  /* ================= POSTGRES ================= */
  const [pg, setPg] = useState({
    db_type: "postgres",
    host: "localhost",
    port: 5432,
    database: "",
    username: "postgres",
    password: "",
    schema_name: "public",
  });

  /* ================= NEO4J ================= */
  const [neo4j, setNeo4j] = useState({
    uri: "bolt://localhost:7687",
    user: "neo4j",
    password: "",
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  /* ================= HELPERS ================= */
  function handlePgChange(e) {
    const { name, value } = e.target;
    setPg(p => ({ ...p, [name]: name === "port" ? Number(value) : value }));
  }

  function handleNeo4jChange(e) {
    const { name, value } = e.target;
    setNeo4j(n => ({ ...n, [name]: value }));
  }

  /* ================= CONNECT ================= */
  async function handleConnect() {
    setLoading(true);
    setError("");

    try {
      /* 1️⃣ Validate Postgres */
      await generateMetadata({
        ...pg,
        output_format: "json",
      });

      /* 2️⃣ Create / reuse session */
      let sessionId = sessionStorage.getItem(SESSION_KEY);
      if (!sessionId) {
        sessionId = uuidv4();
        sessionStorage.setItem(SESSION_KEY, sessionId);
      }

      /* 3️⃣ Load Knowledge Graph */
      await loadKG({
        pg,
        neo4j,
      });

      /* 4️⃣ Initialize RAG */
      await initRAG({
        session_id: sessionId,
        neo4j_uri: neo4j.uri,
        neo4j_user: neo4j.user,
        neo4j_password: neo4j.password,
        neo4j_database: "neo4j",
      });

      /* 5️⃣ Persist SAFE session info */
      sessionStorage.setItem(KG_READY_KEY, "true");
      sessionStorage.setItem(
        NEO4J_CFG_KEY,
        JSON.stringify({
          uri: neo4j.uri,
          user: neo4j.user,
        })
      );

      /* 6️⃣ Enter workspace */
      onConnected(pg);
    } catch (err) {
      console.error(err);
      setError("Unable to connect. Please verify credentials.");
    } finally {
      setLoading(false);
    }
  }

  const canConnect =
    pg.database &&
    neo4j.uri &&
    neo4j.user &&
    neo4j.password &&
    !loading;

  /* ================= UI ================= */
  return (
    <div className="min-h-screen bg-slate-100">
      {/* ================= NAVBAR ================= */}
      <header className="sticky top-0 bg-black border-b border-slate-800">
        <div className="max-w-7xl mx-auto px-6 h-14 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <img src={logo} className="h-7" />
            <div>
              <p className="text-sm font-bold text-white">
                Schema Intelligence
              </p>
              <p className="text-xs text-slate-400">
                Secure onboarding
              </p>
            </div>
          </div>

          <button
            onClick={() => {
              sessionStorage.clear();
              onExit();
            }}
            className="px-4 py-2 rounded-lg bg-red-600 text-white text-sm font-semibold"
          >
            Exit
          </button>
        </div>
      </header>

      {/* ================= BODY ================= */}
      <main className="max-w-5xl mx-auto px-6 py-16">
        <div className="bg-white rounded-3xl shadow-2xl border overflow-hidden">

          {/* HEADER */}
          <div className="px-12 py-10 border-b">
            <h1 className="text-2xl font-extrabold">
              Connect & Initialize Knowledge Graph
            </h1>
            <p className="mt-2 text-sm text-slate-600">
              Provide PostgreSQL and Neo4j credentials to build the graph and enable AI chat.
            </p>
          </div>

          {/* CONTENT */}
          <div className="px-12 py-10 space-y-10">

            {/* POSTGRES */}
            <Section title="PostgreSQL">
              <Grid>
                <Field label="Host" name="host" value={pg.host} onChange={handlePgChange} />
                <Field label="Port" name="port" value={pg.port} onChange={handlePgChange} />
                <Field label="Database" name="database" value={pg.database} onChange={handlePgChange} required />
                <Field label="Schema" name="schema_name" value={pg.schema_name} onChange={handlePgChange} />
                <Field label="Username" name="username" value={pg.username} onChange={handlePgChange} />
                <Field label="Password" name="password" type="password" value={pg.password} onChange={handlePgChange} />
              </Grid>
            </Section>

            {/* NEO4J */}
            <Section title="Neo4j">
              <Grid>
                <Field label="URI" name="uri" value={neo4j.uri} onChange={handleNeo4jChange} />
                <Field label="Username" name="user" value={neo4j.user} onChange={handleNeo4jChange} />
                <Field label="Password" name="password" type="password" value={neo4j.password} onChange={handleNeo4jChange} />
              </Grid>
            </Section>

            {error && (
              <div className="bg-red-50 border border-red-200 px-5 py-4 rounded-xl text-sm text-red-700 font-semibold">
                {error}
              </div>
            )}
          </div>

          {/* FOOTER */}
          <div className="px-12 py-6 border-t bg-slate-50 flex justify-end">
            <button
              onClick={handleConnect}
              disabled={!canConnect}
              className="px-10 py-3 rounded-xl font-bold text-white
                         bg-indigo-600 hover:bg-indigo-700
                         disabled:opacity-50"
            >
              {loading ? "Initializing…" : "Enter Workspace"}
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}

/* ================= UI HELPERS ================= */

function Section({ title, children }) {
  return (
    <div>
      <h2 className="text-xs font-extrabold uppercase tracking-widest mb-4">
        {title}
      </h2>
      {children}
    </div>
  );
}

function Grid({ children }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {children}
    </div>
  );
}

function Field({ label, name, value, onChange, type = "text", required }) {
  return (
    <div>
      <label className="block text-sm font-bold mb-1">
        {label}
        {required && <span className="text-red-500"> *</span>}
      </label>
      <input
        name={name}
        type={type}
        value={value}
        onChange={onChange}
        className="w-full rounded-xl border px-4 py-3 text-sm"
      />
    </div>
  );
}
