// import { useEffect, useMemo, useState } from "react";
// import {
//   generateMetadata,
//   getMetadataDownloadUrl,
// } from "../api/client";

// const STORAGE_KEY = "metadata_state_v1";

// export default function MetadataPage({ dbConfig }) {
//   const [format, setFormat] = useState("csv");
//   const [loading, setLoading] = useState(false);
//   const [result, setResult] = useState(null);

//   /* ================= RESTORE ON LOAD ================= */
//   useEffect(() => {
//     const saved = sessionStorage.getItem(STORAGE_KEY);
//     if (saved) {
//       try {
//         const parsed = JSON.parse(saved);
//         setFormat(parsed.format || "csv");
//         setResult(parsed.result || null);
//       } catch {
//         sessionStorage.removeItem(STORAGE_KEY);
//       }
//     }
//   }, []);

//   /* ================= PERSIST ON CHANGE ================= */
//   useEffect(() => {
//     if (result) {
//       sessionStorage.setItem(
//         STORAGE_KEY,
//         JSON.stringify({ format, result })
//       );
//     }
//   }, [result, format]);

//   async function generate() {
//   if (!dbConfig) {
//     alert("Database configuration missing");
//     return;
//   }

//   const payload = {
//     db_type: dbConfig.db_type,
//     host: dbConfig.host,
//     port: Number(dbConfig.port),
//     database: dbConfig.database,
//     username: dbConfig.username,
//     password: dbConfig.password || "",
//     schema_name: dbConfig.schema_name || "public",
//     output_format: format,
//   };

//   console.log("METADATA PAYLOAD:", payload); // 👈 debug once

//   setLoading(true);
//   setResult(null);

//   const res = await generateMetadata(payload);

//   setResult(res);
//   setLoading(false);
// }


//   const dashboard = useMemo(() => {
//     const s = result?.summary || {};
//     return [
//       ["Tables", s.table_count ?? "—"],
//       ["Columns", s.column_count ?? "—"],
//       ["Relationships", s.relationship_count ?? "—"],
//       [
//         "Generated At",
//         result?.generated_at
//           ? result.generated_at.slice(0, 19).replace("T", " ")
//           : "—",
//       ],
//     ];
//   }, [result]);

//   return (
//     <div className="space-y-8">
//       {/* ================= CONTROLS ================= */}
//       <div className="bg-white border rounded-2xl p-6 shadow-sm">
//         <h2 className="text-lg font-extrabold mb-4">
//           Metadata Generator
//         </h2>

//         <div className="flex gap-6 items-end">
//           <div>
//             <label className="block text-xs font-bold mb-1">
//               Output Format
//             </label>
//             <select
//               value={format}
//               onChange={(e) => setFormat(e.target.value)}
//               className="border rounded-lg px-4 py-2"
//             >
//               {["csv", "json", "xlsx"].map((o) => (
//                 <option key={o}>{o.toUpperCase()}</option>
//               ))}
//             </select>
//           </div>

//           <button
//             onClick={generate}
//             disabled={loading}
//             className="px-6 py-2.5 rounded-lg font-bold text-white
//                        bg-indigo-600 hover:bg-indigo-700
//                        disabled:opacity-50"
//           >
//             {loading ? "Generating…" : "Generate Metadata"}
//           </button>
//         </div>
//       </div>

//       {/* ================= RESULT ================= */}
//       {result && (
//         <>
//           {/* ================= DASHBOARD ================= */}
//           <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
//             {dashboard.map(([k, v]) => (
//               <div
//                 key={k}
//                 className="bg-white border rounded-xl p-4 shadow-sm"
//               >
//                 <div className="text-xs text-slate-500">{k}</div>
//                 <div className="text-xl font-extrabold mt-1">
//                   {v}
//                 </div>
//               </div>
//             ))}
//           </div>

//           {/* ================= PREVIEW ================= */}
//           <div className="bg-white border rounded-2xl shadow-sm">
//             <div className="px-6 py-4 border-b">
//               <h3 className="text-sm font-extrabold uppercase tracking-wide">
//                 Metadata Preview
//               </h3>
//             </div>

//             <div className="h-[360px] overflow-y-auto divide-y">
//               <PreviewSection title="Tables">
//                 {result.tables_preview?.length ? (
//                   result.tables_preview.map((t, i) => (
//                     <div
//                       key={i}
//                       className="flex justify-between text-sm py-2"
//                     >
//                       <span className="font-semibold">
//                         {t.table_name}
//                       </span>
//                       <span className="text-slate-500">
//                         {t.column_count} cols • {t.row_count} rows
//                       </span>
//                     </div>
//                   ))
//                 ) : (
//                   <Empty />
//                 )}
//               </PreviewSection>

//               <PreviewSection title="Columns (sample)">
//                 {result.columns_preview?.length ? (
//                   result.columns_preview.map((c, i) => (
//                     <div
//                       key={i}
//                       className="grid grid-cols-3 text-sm py-2"
//                     >
//                       <span className="font-semibold">
//                         {c.table_name}
//                       </span>
//                       <span>{c.column_name}</span>
//                       <span className="text-slate-500">
//                         {c.data_type}
//                       </span>
//                     </div>
//                   ))
//                 ) : (
//                   <Empty />
//                 )}
//               </PreviewSection>
//             </div>
//           </div>

//           {/* ================= DOWNLOAD ================= */}
//           <div className="flex justify-end">
//             <a
//               href={getMetadataDownloadUrl(result.saved_file)}
//               className="px-6 py-2.5 rounded-lg font-bold text-white
//                          bg-emerald-600 hover:bg-emerald-700"
//             >
//               Download Metadata
//             </a>
//           </div>
//         </>
//       )}
//     </div>
//   );
// }

// /* ================= HELPERS ================= */

// function PreviewSection({ title, children }) {
//   return (
//     <div className="px-6 py-4">
//       <div className="sticky top-0 bg-white py-2 z-10">
//         <p className="text-xs font-extrabold uppercase text-slate-600">
//           {title}
//         </p>
//       </div>
//       <div className="mt-2 space-y-1">{children}</div>
//     </div>
//   );
// }

// function Empty() {
//   return (
//     <div className="text-sm text-slate-400 italic py-2">
//       No preview data available
//     </div>
//   );
// }
import { useEffect, useMemo, useState } from "react";
import {
  generateMetadata,
  getMetadataDownloadUrl,
} from "../api/client";

const STORAGE_KEY = "metadata_state_v1";

export default function MetadataPage({ dbConfig }) {
  const [format, setFormat] = useState("csv");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  /* ===== Restore ===== */
  useEffect(() => {
    const saved = sessionStorage.getItem(STORAGE_KEY);
    if (saved) {
      const parsed = JSON.parse(saved);
      setFormat(parsed.format || "csv");
      setResult(parsed.result || null);
    }
  }, []);

  /* ===== Persist ===== */
  useEffect(() => {
    if (result) {
      sessionStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({ format, result })
      );
    }
  }, [result, format]);

  async function generate() {
    if (!dbConfig) return;

    const payload = {
      db_type: dbConfig.db_type,
      host: dbConfig.host,
      port: Number(dbConfig.port),
      database: dbConfig.database,
      username: dbConfig.username,
      password: dbConfig.password || "",
      schema_name: dbConfig.schema_name || "public",
      output_format: format,
    };

    setLoading(true);
    setResult(null);

    const res = await generateMetadata(payload);

    setResult(res);
    setLoading(false);
  }

  /* ===== DASHBOARD METRICS (Generated At REMOVED) ===== */
  const dashboard = useMemo(() => {
    const s = result?.summary || {};
    return [
      ["No of Tables", s.table_count ?? "—"],
      ["No of Columns", s.column_count ?? "—"],
      ["No of Relationships", s.relationship_count ?? "—"],
    ];
  }, [result]);

  return (
    <div className="space-y-8">

      {/* ================= CONTROLS ================= */}
      <div className="bg-white border rounded-2xl p-6 shadow-sm">
        <h2 className="text-lg font-extrabold mb-4">
          Metadata Generator
        </h2>

        <div className="flex gap-6 items-end">
          <div>
            <label className="block text-xs font-bold mb-1">
              Output Format
            </label>
            <select
              value={format}
              onChange={(e) => setFormat(e.target.value)}
              className="border rounded-lg px-4 py-2"
            >
              <option value="csv">CSV</option>
              <option value="json">JSON</option>
              <option value="xlsx">XLSX</option>
            </select>
          </div>

          <button
            onClick={generate}
            disabled={loading}
            className="px-6 py-2.5 rounded-lg font-bold text-white
                       bg-indigo-600 hover:bg-indigo-700
                       disabled:opacity-50"
          >
            {loading ? "Generating…" : "Generate Metadata"}
          </button>
        </div>
      </div>

      {/* ================= RESULT ================= */}
      {result && (
        <>
          {/* ===== GENERATED AT (TOP LINE) ===== */}
          {result.generated_at && (
            <div className="text-sm font-semibold text-slate-600">
              Generated at:{" "}
              <span className="text-slate-800">
                {result.generated_at.slice(0, 19).replace("T", " ")}
              </span>
            </div>
          )}

          {/* ================= DASHBOARD ================= */}
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {dashboard.map(([k, v]) => (
              <div
                key={k}
                className="bg-white border rounded-xl p-4 shadow-sm"
              >
                <div className="text-xs text-slate-500">{k}</div>
                <div className="text-xl font-extrabold mt-1">
                  {v}
                </div>
              </div>
            ))}
          </div>

          {/* ================= PREVIEW ================= */}
          <div className="bg-white border rounded-2xl shadow-sm">
            <div className="px-6 py-4 border-b">
              <h3 className="text-sm font-extrabold uppercase tracking-wide">
                Metadata Preview
              </h3>
            </div>

            <div className="h-[360px] overflow-y-auto divide-y">
              <PreviewSection title="Tables">
                {result.tables_preview?.length ? (
                  result.tables_preview.map((t, i) => (
                    <div
                      key={i}
                      className="flex justify-between text-sm py-2"
                    >
                      <span className="font-semibold">
                        {t.table_name}
                      </span>
                      <span className="text-slate-500">
                        {t.column_count} cols • {t.row_count} rows
                      </span>
                    </div>
                  ))
                ) : (
                  <Empty />
                )}
              </PreviewSection>

              <PreviewSection title="Columns (sample)">
                {result.columns_preview?.length ? (
                  result.columns_preview.map((c, i) => (
                    <div
                      key={i}
                      className="grid grid-cols-3 text-sm py-2"
                    >
                      <span className="font-semibold">
                        {c.table_name}
                      </span>
                      <span>{c.column_name}</span>
                      <span className="text-slate-500">
                        {c.data_type}
                      </span>
                    </div>
                  ))
                ) : (
                  <Empty />
                )}
              </PreviewSection>
            </div>
          </div>

          {/* ================= DOWNLOAD ================= */}
          <div className="flex justify-end">
            <a
              href={getMetadataDownloadUrl(result.saved_file)}
              className="px-6 py-2.5 rounded-lg font-bold text-white
                         bg-emerald-600 hover:bg-emerald-700"
            >
              Download Metadata
            </a>
          </div>
        </>
      )}
    </div>
  );
}

/* ================= HELPERS ================= */

function PreviewSection({ title, children }) {
  return (
    <div className="px-6 py-4">
      <div className="sticky top-0 bg-white py-2 z-10">
        <p className="text-xs font-extrabold uppercase text-slate-600">
          {title}
        </p>
      </div>
      <div className="mt-2 space-y-1">{children}</div>
    </div>
  );
}

function Empty() {
  return (
    <div className="text-sm text-slate-400 italic py-2">
      No preview data available
    </div>
  );
}
