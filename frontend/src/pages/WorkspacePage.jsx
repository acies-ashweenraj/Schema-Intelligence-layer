// // import { useEffect, useMemo, useRef, useState } from "react";
// // import { v4 as uuidv4 } from "uuid";
// // import logo from "../assets/logo.png";

// // import {
// //   generateMetadata,
// //   getMetadataDownloadUrl,
// //   runHybridMapping,
// //   getMappingDownloadUrl,
// //   loadKG,
// //   initRAG,
// //   askQuestion,
// // } from "../api/client";

// // /* ======================================================
// //    WORKSPACE – FINAL ENTERPRISE FLOW
// // ====================================================== */

// // export default function WorkspacePage({ dbConfig, onExit }) {
// //   const [activeTab, setActiveTab] = useState("metadata");

// //   /* ================= METADATA ================= */
// //   const [metaFormat, setMetaFormat] = useState("csv");
// //   const [metaLoading, setMetaLoading] = useState(false);
// //   const [metaResult, setMetaResult] = useState(null);

// //   const metaDashboard = useMemo(() => {
// //     const s = metaResult?.summary || {};
// //     return [
// //       ["Tables", s.table_count ?? "—"],
// //       ["Columns", s.column_count ?? "—"],
// //       ["Relationships", s.relationship_count ?? "—"],
// //       [
// //         "Generated",
// //         metaResult?.generated_at
// //           ? metaResult.generated_at.slice(0, 19).replace("T", " ")
// //           : "—",
// //       ],
// //     ];
// //   }, [metaResult]);

// //   async function generateMeta() {
// //     setMetaLoading(true);
// //     setMetaResult(null);

// //     const res = await generateMetadata({
// //       ...dbConfig,
// //       port: Number(dbConfig.port),
// //       schema_name: dbConfig.schema_name || "public",
// //       output_format: metaFormat,
// //     });

// //     setMetaResult(res);
// //     setMetaLoading(false);
// //   }

// //   /* ================= MAPPING ================= */
// //   const [mapFormat, setMapFormat] = useState("csv");
// //   const [mappingLoading, setMappingLoading] = useState(false);
// //   const [mappingResult, setMappingResult] = useState(null);
// //   const [mappingRows, setMappingRows] = useState([]);

// //   const [targetCfg, setTargetCfg] = useState({
// //     db_type: "postgres",
// //     host: "",
// //     port: "5432",
// //     database: "",
// //     username: "",
// //     password: "",
// //     schema_name: "public",
// //   });

// //   const mappingDashboard = useMemo(() => {
// //     const d = mappingResult?.details?.dashboard;
// //     if (!d) return [];
// //     return [
// //       ["Source Tables", d.source_tables_used],
// //       ["Target Tables", d.target_tables_used],
// //       ["Matched Tables", d.matched_table_pairs],
// //       ["Matched Columns", d.matched_columns],
// //       [
// //         "Avg Confidence",
// //         typeof d.avg_confidence_score === "number"
// //           ? d.avg_confidence_score.toFixed(3)
// //           : "—",
// //       ],
// //     ];
// //   }, [mappingResult]);

// //   async function generateMapping() {
// //     setMappingLoading(true);
// //     setMappingResult(null);
// //     setMappingRows([]);

// //     const res = await runHybridMapping({
// //       src_cfg: { ...dbConfig, port: Number(dbConfig.port) },
// //       tgt_cfg: { ...targetCfg, port: Number(targetCfg.port) },
// //       qdrant_host: "localhost",
// //       qdrant_port: 6333,
// //       top_k_dense: 5,
// //       output_format: mapFormat,
// //     });

// //     setMappingResult(res);
// //     setMappingRows(res.mappings || []);
// //     setMappingLoading(false);
// //   }

// //   function updateMappingRow(i, key, value) {
// //     setMappingRows((rows) =>
// //       rows.map((r, idx) => (idx === i ? { ...r, [key]: value } : r))
// //     );
// //   }

// //   /* ================= CHATBOT ================= */
// //   const sessionId = useMemo(() => uuidv4(), []);
// //   const [neo4j, setNeo4j] = useState({ uri: "", user: "", password: "" });
// //   const [ragReady, setRagReady] = useState(false);
// //   const [chatLoading, setChatLoading] = useState(false);
// //   const [messages, setMessages] = useState([]);
// //   const [question, setQuestion] = useState("");
// //   const bottomRef = useRef(null);

// //   useEffect(() => {
// //     bottomRef.current?.scrollIntoView({ behavior: "smooth" });
// //   }, [messages]);

// //   async function initChat() {
// //     setChatLoading(true);

// //     await loadKG({ pg: dbConfig, neo4j });
// //     await initRAG({
// //       session_id: sessionId,
// //       neo4j_uri: neo4j.uri,
// //       neo4j_user: neo4j.user,
// //       neo4j_password: neo4j.password,
// //       neo4j_database: "neo4j",
// //     });

// //     setMessages([{ role: "bot", text: "Chat initialized." }]);
// //     setRagReady(true);
// //     setChatLoading(false);
// //   }

// //   async function sendQuestion() {
// //     if (!question.trim()) return;
// //     const q = question;
// //     setQuestion("");
// //     setMessages((m) => [...m, { role: "user", text: q }]);
// //     const res = await askQuestion({ session_id: sessionId, question: q });
// //     setMessages((m) => [...m, { role: "bot", text: res.result }]);
// //   }

// //   function newChat() {
// //     setMessages([{ role: "bot", text: "New chat started." }]);
// //   }

// //   /* ======================================================
// //      RENDER
// //   ====================================================== */

// //   return (
// //     <div className="h-screen flex flex-col bg-slate-100">
// //       {/* TOP BAR */}
// //       <header className="h-14 bg-black flex items-center justify-between px-6">
// //         <div className="flex items-center gap-3">
// //           <img src={logo} className="h-6" />
// //           <span className="text-white font-semibold">
// //             Schema Intelligence
// //           </span>
// //         </div>
// //         <button
// //           onClick={onExit}
// //           className="bg-red-600 text-white px-4 py-1.5 rounded"
// //         >
// //           Exit
// //         </button>
// //       </header>

// //       <div className="flex flex-1 overflow-hidden">
// //         {/* LEFT PANEL */}
// //         <aside className="w-64 bg-slate-200 border-r p-4 space-y-2">
// //           {["metadata", "mapping", "chatbot"].map((t) => (
// //             <button
// //               key={t}
// //               onClick={() => setActiveTab(t)}
// //               className={`w-full px-4 py-3 rounded-lg font-semibold text-left ${
// //                 activeTab === t
// //                   ? "bg-white shadow text-indigo-700"
// //                   : "hover:bg-slate-300"
// //               }`}
// //             >
// //               {t.toUpperCase()}
// //             </button>
// //           ))}
// //         </aside>

// //         {/* MAIN */}
// //         <main className="flex-1 overflow-y-auto p-8 max-w-6xl mx-auto">
// //           {/* ================= METADATA ================= */}
// //           {activeTab === "metadata" && (
// //             <Section title="Metadata Generator">
// //               <FormRow>
// //                 <Select
// //                   label="Output Format"
// //                   value={metaFormat}
// //                   onChange={setMetaFormat}
// //                   options={["csv", "json", "xlsx"]}
// //                 />
// //                 <PrimaryButton onClick={generateMeta}>
// //                   {metaLoading ? "Generating…" : "Generate Metadata"}
// //                 </PrimaryButton>
// //               </FormRow>

// //               {metaResult && (
// //                 <>
// //                   <Dashboard items={metaDashboard} />
// //                   <DownloadButton
// //                     href={getMetadataDownloadUrl(metaResult.saved_file)}
// //                   />
// //                 </>
// //               )}
// //             </Section>
// //           )}

// //           {/* ================= MAPPING ================= */}
// //           {activeTab === "mapping" && (
// //             <>
// //               <Section title="Target Database Configuration">
// //                 <FormGrid>
// //                   {Object.keys(targetCfg).map((k) => (
// //                     <Input
// //                       key={k}
// //                       label={k}
// //                       type={k === "password" ? "password" : "text"}
// //                       value={targetCfg[k]}
// //                       onChange={(v) =>
// //                         setTargetCfg({ ...targetCfg, [k]: v })
// //                       }
// //                     />
// //                   ))}
// //                 </FormGrid>

// //                 <FormRow>
// //                   <Select
// //                     label="Output Format"
// //                     value={mapFormat}
// //                     onChange={setMapFormat}
// //                     options={["csv", "json", "xlsx"]}
// //                   />
// //                   <PrimaryButton onClick={generateMapping}>
// //                     {mappingLoading ? "Generating…" : "Generate Mapping"}
// //                   </PrimaryButton>
// //                 </FormRow>
// //               </Section>

// //               {mappingResult && (
// //                 <>
// //                   <Dashboard items={mappingDashboard} />

// //                   <Section title="Editable Mapping">
// //                     <div className="overflow-x-auto border rounded-lg bg-white">
// //                       <table className="min-w-full text-sm">
// //                         <thead className="bg-slate-100">
// //                           <tr>
// //                             {[
// //                               "Source Table",
// //                               "Source Column",
// //                               "Target Table",
// //                               "Target Column",
// //                               "Confidence",
// //                             ].map((h) => (
// //                               <th key={h} className="px-3 py-2 text-left">
// //                                 {h}
// //                               </th>
// //                             ))}
// //                           </tr>
// //                         </thead>
// //                         <tbody>
// //                           {mappingRows.map((r, i) => (
// //                             <tr key={i} className="border-t">
// //                               {[
// //                                 "source_table",
// //                                 "source_column",
// //                                 "target_table",
// //                                 "target_column",
// //                                 "confidence",
// //                               ].map((k) => (
// //                                 <td key={k} className="px-3 py-2">
// //                                   <input
// //                                     value={r[k]}
// //                                     onChange={(e) =>
// //                                       updateMappingRow(i, k, e.target.value)
// //                                     }
// //                                     className="w-full border rounded px-2 py-1"
// //                                   />
// //                                 </td>
// //                               ))}
// //                             </tr>
// //                           ))}
// //                         </tbody>
// //                       </table>
// //                     </div>

// //                     <DownloadButton
// //                       href={getMappingDownloadUrl(mappingResult.saved_file)}
// //                     />
// //                   </Section>
// //                 </>
// //               )}
// //             </>
// //           )}

// //           {/* ================= CHATBOT ================= */}
// //           {activeTab === "chatbot" && (
// //             <Section title="Chatbot">
// //               {!ragReady && (
// //                 <>
// //                   {["uri", "user", "password"].map((f) => (
// //                     <Input
// //                       key={f}
// //                       label={f}
// //                       type={f === "password" ? "password" : "text"}
// //                       onChange={(v) =>
// //                         setNeo4j({ ...neo4j, [f]: v })
// //                       }
// //                     />
// //                   ))}
// //                   <PrimaryButton onClick={initChat}>
// //                     {chatLoading ? "Initializing…" : "Initialize Chat"}
// //                   </PrimaryButton>
// //                 </>
// //               )}

// //               {ragReady && (
// //                 <>
// //                   <div className="flex justify-end mb-2">
// //                     <button
// //                       onClick={newChat}
// //                       className="text-sm text-indigo-700 font-semibold"
// //                     >
// //                       + New Chat
// //                     </button>
// //                   </div>

// //                   <div className="h-96 border rounded p-4 bg-white overflow-y-auto space-y-2">
// //                     {messages.map((m, i) => (
// //                       <div
// //                         key={i}
// //                         className={`p-3 rounded max-w-[80%] ${
// //                           m.role === "user"
// //                             ? "bg-indigo-600 text-white ml-auto"
// //                             : "bg-slate-100"
// //                         }`}
// //                       >
// //                         {m.text}
// //                       </div>
// //                     ))}
// //                     <div ref={bottomRef} />
// //                   </div>

// //                   <div className="flex gap-3 mt-3">
// //                     <input
// //                       value={question}
// //                       onChange={(e) => setQuestion(e.target.value)}
// //                       onKeyDown={(e) => e.key === "Enter" && sendQuestion()}
// //                       className="flex-1 border px-3 py-2 rounded"
// //                       placeholder="Ask a question…"
// //                     />
// //                     <PrimaryButton onClick={sendQuestion}>
// //                       Send
// //                     </PrimaryButton>
// //                   </div>
// //                 </>
// //               )}
// //             </Section>
// //           )}
// //         </main>
// //       </div>
// //     </div>
// //   );
// // }

// // /* ================= UI HELPERS ================= */

// // function Section({ title, children }) {
// //   return (
// //     <div className="bg-white border rounded-xl p-6 mb-6 shadow-sm space-y-4">
// //       <h2 className="text-lg font-bold">{title}</h2>
// //       {children}
// //     </div>
// //   );
// // }

// // function Dashboard({ items }) {
// //   return (
// //     <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
// //       {items.map(([k, v]) => (
// //         <div key={k} className="bg-white border rounded-xl p-4 shadow-sm">
// //           <div className="text-xs text-slate-500">{k}</div>
// //           <div className="text-xl font-bold">{v}</div>
// //         </div>
// //       ))}
// //     </div>
// //   );
// // }

// // function FormRow({ children }) {
// //   return <div className="flex gap-6 items-end flex-wrap">{children}</div>;
// // }

// // function FormGrid({ children }) {
// //   return <div className="grid grid-cols-2 gap-6">{children}</div>;
// // }

// // function Input({ label, type = "text", value, onChange }) {
// //   return (
// //     <div>
// //       <label className="block text-xs font-bold mb-1 capitalize">
// //         {label}
// //       </label>
// //       <input
// //         type={type}
// //         value={value}
// //         onChange={(e) => onChange(e.target.value)}
// //         className="w-full border rounded px-3 py-2"
// //       />
// //     </div>
// //   );
// // }

// // function Select({ label, value, onChange, options }) {
// //   return (
// //     <div>
// //       <label className="block text-xs font-bold mb-1">{label}</label>
// //       <select
// //         value={value}
// //         onChange={(e) => onChange(e.target.value)}
// //         className="border rounded px-3 py-2"
// //       >
// //         {options.map((o) => (
// //           <option key={o} value={o}>
// //             {o.toUpperCase()}
// //           </option>
// //         ))}
// //       </select>
// //     </div>
// //   );
// // }

// // function PrimaryButton({ children, onClick }) {
// //   return (
// //     <button
// //       onClick={onClick}
// //       className="bg-indigo-600 text-white px-5 py-2 rounded font-semibold"
// //     >
// //       {children}
// //     </button>
// //   );
// // }

// // function DownloadButton({ href }) {
// //   return (
// //     <a
// //       href={href}
// //       className="inline-block bg-emerald-600 text-white px-5 py-2 rounded font-semibold"
// //     >
// //       Download
// //     </a>
// //   );
// // }
// import { NavLink, Outlet } from "react-router-dom";
// import logo from "../assets/logo.png";

// export default function WorkspacePage({ onExit }) {
//   return (
//     <div className="h-screen flex flex-col bg-slate-100">
//       {/* HEADER */}
//       <header className="h-14 bg-black flex items-center justify-between px-6">
//         <div className="flex items-center gap-3">
//           <img src={logo} className="h-6" />
//           <span className="text-white font-semibold">
//             Schema Intelligence
//           </span>
//         </div>
//         <button
//           onClick={onExit}
//           className="bg-red-600 text-white px-4 py-1.5 rounded"
//         >
//           Exit
//         </button>
//       </header>

//       <div className="flex flex-1 overflow-hidden">
//         {/* SIDEBAR */}
//         <aside className="w-64 bg-slate-200 border-r p-4 space-y-2">
//           {[
//             { path: "metadata", label: "METADATA" },
//             { path: "mapping", label: "MAPPING" },
//             { path: "chatbot", label: "CHATBOT" },
//           ].map((t) => (
//             <NavLink
//               key={t.path}
//               to={t.path}
//               className={({ isActive }) =>
//                 `block px-4 py-3 rounded-lg font-semibold ${
//                   isActive
//                     ? "bg-white shadow text-indigo-700"
//                     : "hover:bg-slate-300"
//                 }`
//               }
//             >
//               {t.label}
//             </NavLink>
//           ))}
//         </aside>

//         {/* PAGE CONTENT */}
//         <main className="flex-1 overflow-y-auto p-8 max-w-6xl mx-auto">
//           <Outlet />
//         </main>
//       </div>
//     </div>
//   );
// }
import { useState } from "react";
import logo from "../assets/logo.png";

import MetadataPage from "./MetadataPage";
import MappingPage from "./MappingPage";
import ChatbotPage from "./ChatbotPage";

export default function WorkspacePage({
  dbConfig,
  metadata,
  onExit,
}) {
  const [activePage, setActivePage] = useState("metadata");

  return (
    <div className="h-screen flex flex-col bg-slate-100">
      {/* TOP BAR */}
      <header className="h-14 bg-black flex items-center justify-between px-6">
        <div className="flex items-center gap-3">
          <img src={logo} className="h-6" />
          <span className="text-white font-semibold">
            Schema Intelligence
          </span>
        </div>
        <button
          onClick={onExit}
          className="bg-red-600 text-white px-4 py-1.5 rounded"
        >
          Exit
        </button>
      </header>

      <div className="flex flex-1 overflow-hidden">
        {/* SIDEBAR */}
        <aside className="w-64 bg-slate-200 border-r p-4 space-y-2">
          {[
            ["metadata", "METADATA"],
            ["mapping", "MAPPING"],
            ["chatbot", "CHATBOT"],
          ].map(([key, label]) => (
            <button
              key={key}
              onClick={() => setActivePage(key)}
              className={`w-full px-4 py-3 rounded-lg font-semibold text-left ${
                activePage === key
                  ? "bg-white shadow text-indigo-700"
                  : "hover:bg-slate-300"
              }`}
            >
              {label}
            </button>
          ))}
        </aside>

        {/* CONTENT */}
        <main className="flex-1 overflow-y-auto p-8 max-w-6xl mx-auto">
          {activePage === "metadata" && (
            <MetadataPage
              dbConfig={dbConfig}
              metadata={metadata}
            />
          )}

          {activePage === "mapping" && (
            <MappingPage dbConfig={dbConfig} />
          )}

          {activePage === "chatbot" && (
            <ChatbotPage dbConfig={dbConfig} />
          )}
        </main>
      </div>
    </div>
  );
}
