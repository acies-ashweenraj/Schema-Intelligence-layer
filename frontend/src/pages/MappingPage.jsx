// import { useEffect, useMemo, useState } from "react";
// import * as XLSX from "xlsx";
// import { runHybridMapping } from "../api/client";

// const STORAGE_KEY = "mapping_state_v3";

// export default function MappingPage({ dbConfig }) {
//   const [format, setFormat] = useState("csv");
//   const [minConfidence, setMinConfidence] = useState(0.5);
//   const [showLegend, setShowLegend] = useState(false);
//   const [loading, setLoading] = useState(false);

//   const [result, setResult] = useState(null);
//   const [rows, setRows] = useState([]);
//   const [saved, setSaved] = useState(false);

//   const [targetCfg, setTargetCfg] = useState({
//     db_type: "postgres",
//     host: "localhost",
//     port: "5432",
//     database: "",
//     username: "postgres",
//     password: "",
//     schema_name: "public",
//   });

//   /* ================= RESET WHEN DB CONFIG CHANGES ================= */
//   useEffect(() => {
//     sessionStorage.removeItem(STORAGE_KEY);
//     setResult(null);
//     setRows([]);
//     setSaved(false);
//   }, [dbConfig]);

//   /* ================= RESTORE STATE ================= */
//   useEffect(() => {
//     const cached = sessionStorage.getItem(STORAGE_KEY);
//     if (!cached) return;

//     try {
//       const s = JSON.parse(cached);
//       setFormat(s.format);
//       setMinConfidence(s.minConfidence);
//       setResult(s.result);
//       setRows(s.rows);
//       setSaved(s.saved);
//       setTargetCfg(s.targetCfg);
//     } catch {
//       sessionStorage.removeItem(STORAGE_KEY);
//     }
//   }, []);

//   /* ================= PERSIST STATE ================= */
//   useEffect(() => {
//     if (!rows.length) return;

//     sessionStorage.setItem(
//       STORAGE_KEY,
//       JSON.stringify({
//         format,
//         minConfidence,
//         result,
//         rows,
//         saved,
//         targetCfg,
//       })
//     );
//   }, [format, minConfidence, result, rows, saved, targetCfg]);

//   /* ================= DASHBOARD ================= */
//   const dashboard = useMemo(() => {
//     const d = result?.details?.dashboard;
//     if (!d) return [];

//     return [
//       ["Source Tables", d.source_tables],
//       ["Target Tables", d.target_tables],
//       ["Matched Tables", d.matched_tables],
//       ["Matched Columns", d.matched_columns],
//       ["Avg Confidence", d.avg_confidence_score ?? "—"],
//     ];
//   }, [result]);

//   /* ================= DROPDOWN OPTIONS ================= */
//   const targetTableOptions = useMemo(
//     () =>
//       Array.from(
//         new Set(rows.map(r => r.target_table).filter(Boolean))
//       ),
//     [rows]
//   );

//   const bestMatchColumnOptions = useMemo(
//     () =>
//       Array.from(
//         new Set(rows.map(r => r.best_match_column).filter(Boolean))
//       ),
//     [rows]
//   );

//   /* ================= GENERATE ================= */
//   async function generate() {
//     setLoading(true);
//     setSaved(false);

//     const payload = {
//       src_cfg: { ...dbConfig, port: Number(dbConfig.port) },
//       tgt_cfg: { ...targetCfg, port: Number(targetCfg.port) },
//       output_format: format,
//       min_confidence: minConfidence,
//     };

//     const res = await runHybridMapping(payload);
//     setResult(res);
//     setRows(res.details?.all_rows || []);
//     setLoading(false);
//   }

//   /* ================= EDIT ================= */
//   function updateRow(rowIndex, key, value) {
//     setRows(prev =>
//       prev.map((r, i) =>
//         i === rowIndex ? { ...r, [key]: value } : r
//       )
//     );
//     setSaved(false);
//   }

//   /* ================= SAVE ================= */
//   function saveChanges() {
//     if (!rows.length) return;
//     setSaved(true);
//     alert("Changes saved. You can now download.");
//   }

//   /* ================= DOWNLOAD ================= */
//   function download() {
//     if (!saved || !rows.length) return;

//     if (format === "csv") {
//       const header = Object.keys(rows[0]).join(",");
//       const body = rows
//         .map(r =>
//           Object.values(r).map(v => `"${v ?? ""}"`).join(",")
//         )
//         .join("\n");

//       triggerDownload(`${header}\n${body}`, "mapping.csv", "text/csv");
//     }

//     if (format === "json") {
//       triggerDownload(
//         JSON.stringify(rows, null, 2),
//         "mapping.json",
//         "application/json"
//       );
//     }

//     if (format === "xlsx") {
//       const ws = XLSX.utils.json_to_sheet(rows);
//       const wb = XLSX.utils.book_new();
//       XLSX.utils.book_append_sheet(wb, ws, "Mapping");
//       XLSX.writeFile(wb, "mapping.xlsx");
//     }
//   }

//   function triggerDownload(content, filename, type) {
//     const blob = new Blob([content], { type });
//     const url = URL.createObjectURL(blob);
//     const a = document.createElement("a");
//     a.href = url;
//     a.download = filename;
//     a.click();
//     URL.revokeObjectURL(url);
//   }

//   /* ================= UI ================= */
//   return (
//     <div className="space-y-10">

//       {/* CONFIG */}
//       <div className="bg-white border rounded-2xl p-8">
//         <h2 className="text-lg font-extrabold mb-6">
//           Mapping Configuration
//         </h2>

//         <div className="grid grid-cols-2 md:grid-cols-3 gap-6 mb-6">
//           {Object.keys(targetCfg).map(k => (
//             <input
//               key={k}
//               type={k === "password" ? "password" : "text"}
//               value={targetCfg[k]}
//               onChange={e =>
//                 setTargetCfg({ ...targetCfg, [k]: e.target.value })
//               }
//               placeholder={k.replace("_", " ")}
//               className="border rounded-lg px-4 py-2"
//             />
//           ))}
//         </div>

//         <div className="grid grid-cols-3 gap-6 items-end">
//           <select
//             value={format}
//             onChange={e => setFormat(e.target.value)}
//             className="border rounded-lg px-4 py-2"
//           >
//             <option value="csv">CSV</option>
//             <option value="json">JSON</option>
//             <option value="xlsx">XLSX</option>
//           </select>

//           {/* MIN CONFIDENCE + INFO */}
//           <div className="relative">
//             <label className="text-xs font-bold flex items-center gap-2">
//               Min Confidence
//               <button
//                 type="button"
//                 onClick={() => setShowLegend(!showLegend)}
//                 className="text-indigo-600 font-extrabold"
//               >
//                 ⓘ
//               </button>
//             </label>

//             <input
//               type="number"
//               step="0.05"
//               min="0"
//               max="1"
//               value={minConfidence}
//               onChange={e => setMinConfidence(Number(e.target.value))}
//               className="border rounded-lg px-4 py-2 w-full"
//             />

//             {showLegend && (
//               <div className="absolute z-20 mt-2 w-96 bg-white border rounded-xl p-4 text-xs shadow-xl">
//                 <p className="font-bold mb-2">Confidence Levels Legend</p>
//                 <ul className="space-y-1">
//                   <li>🟢 ≥ 0.90 — Very High</li>
//                   <li>🟢 0.80 – 0.89 — High</li>
//                   <li>🟡 0.65 – 0.79 — Medium</li>
//                   <li>🟠 0.50 – 0.64 — Low</li>
//                   <li>🔴 &lt; 0.50 — Very Low</li>
//                 </ul>
//               </div>
//             )}
//           </div>

//           <button
//             onClick={generate}
//             className="bg-indigo-600 text-white px-6 py-3 rounded-xl font-bold"
//           >
//             {loading ? "Generating…" : "Generate Mapping"}
//           </button>
//         </div>
//       </div>

//       {/* DASHBOARD + TABLE */}
//       {rows.length > 0 && (
//         <>
//           <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
//             {dashboard.map(([k, v]) => (
//               <div key={k} className="bg-white border rounded-xl p-4">
//                 <div className="text-xs text-slate-500">{k}</div>
//                 <div className="text-xl font-extrabold">{v}</div>
//               </div>
//             ))}
//           </div>

//           {/* EDITABLE TABLE */}
//           <div className="bg-white border rounded-2xl">
//             <div className="px-6 py-4 border-b font-extrabold">
//               Editable Mapping Results
//             </div>

//             <div className="overflow-x-auto max-h-[500px]">
//               <table className="min-w-full text-sm">
//                 <thead className="bg-slate-100 sticky top-0">
//                   <tr>
//                     {Object.keys(rows[0]).map(h => (
//                       <th key={h} className="px-3 py-2 text-left">
//                         {h}
//                       </th>
//                     ))}
//                   </tr>
//                 </thead>

//                 <tbody>
//                   {rows.map((r, i) => (
//                     <tr key={i} className="border-t">
//                       {Object.keys(r).map(k => (
//                         <td key={k} className="px-3 py-2">
//                           {k === "target_table" && (
//                             <select
//                               value={r[k]}
//                               onChange={e =>
//                                 updateRow(i, k, e.target.value)
//                               }
//                               className="w-full border rounded px-2 py-1"
//                             >
//                               {targetTableOptions.map(t => (
//                                 <option key={t} value={t}>{t}</option>
//                               ))}
//                             </select>
//                           )}

//                           {k === "best_match_column" && (
//                             <select
//                               value={r[k]}
//                               onChange={e =>
//                                 updateRow(i, k, e.target.value)
//                               }
//                               className="w-full border rounded px-2 py-1"
//                             >
//                               {bestMatchColumnOptions.map(c => (
//                                 <option key={c} value={c}>{c}</option>
//                               ))}
//                             </select>
//                           )}

//                           {k !== "target_table" &&
//                             k !== "best_match_column" && (
//                               <span>{r[k]}</span>
//                             )}
//                         </td>
//                       ))}
//                     </tr>
//                   ))}
//                 </tbody>
//               </table>
//             </div>

//             <div className="flex justify-end gap-4 px-6 py-4 border-t">
//               <button
//                 onClick={saveChanges}
//                 className="bg-indigo-600 text-white px-5 py-2 rounded-lg"
//               >
//                 Save Changes
//               </button>

//               <button
//                 onClick={download}
//                 disabled={!saved}
//                 className={`px-5 py-2 rounded-lg font-bold ${
//                   saved
//                     ? "bg-emerald-600 text-white"
//                     : "bg-slate-300 text-slate-600"
//                 }`}
//               >
//                 Download
//               </button>
//             </div>
//           </div>
//         </>
//       )}
//     </div>
//   );
// }
import { useEffect, useMemo, useState } from "react";
import * as XLSX from "xlsx";
import { runHybridMapping } from "../api/client";

const STORAGE_KEY = "mapping_state_final_v1";

export default function MappingPage({ dbConfig }) {
  /* ================= STATE ================= */
  const [format, setFormat] = useState("csv");
  const [minConfidence, setMinConfidence] = useState(0.5);
  const [showLegend, setShowLegend] = useState(false);
  const [loading, setLoading] = useState(false);

  const [result, setResult] = useState(null);
  const [rows, setRows] = useState([]);
  const [saved, setSaved] = useState(false);

  const [showPassword, setShowPassword] = useState(false);

  const [targetCfg, setTargetCfg] = useState({
    db_type: "postgres",
    host: "localhost",
    port: "5432",
    database: "",
    username: "postgres",
    password: "",
    schema_name: "public",
  });

  /* ================= RESTORE SESSION ================= */
  useEffect(() => {
    const cached = sessionStorage.getItem(STORAGE_KEY);
    if (!cached) return;

    try {
      const s = JSON.parse(cached);
      setFormat(s.format);
      setMinConfidence(s.minConfidence);
      setResult(s.result);
      setRows(s.rows);
      setSaved(s.saved);
      setTargetCfg(s.targetCfg);
    } catch {
      sessionStorage.removeItem(STORAGE_KEY);
    }
  }, []);

  /* ================= PERSIST SESSION ================= */
  useEffect(() => {
    if (!rows.length) return;

    sessionStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({
        format,
        minConfidence,
        result,
        rows,
        saved,
        targetCfg,
      })
    );
  }, [format, minConfidence, result, rows, saved, targetCfg]);

  /* ================= DASHBOARD ================= */
  const dashboard = useMemo(() => {
    const d = result?.details?.dashboard;
    if (!d) return [];

    return [
      ["Source Tables", d.source_tables],
      ["Target Tables", d.target_tables],
      ["Matched Tables", d.matched_tables],
      ["Matched Columns", d.matched_columns],
      ["Avg Confidence", d.avg_confidence_score ?? "—"],
    ];
  }, [result]);

  /* ================= DROPDOWNS ================= */
  const targetTableOptions = useMemo(
    () =>
      Array.from(
        new Set(rows.map(r => r.target_table).filter(Boolean))
      ),
    [rows]
  );

  const bestMatchColumnOptions = useMemo(
    () =>
      Array.from(
        new Set(rows.map(r => r.best_match_column).filter(Boolean))
      ),
    [rows]
  );

  /* ================= GENERATE ================= */
  async function generate() {
    setLoading(true);
    setSaved(false);

    const res = await runHybridMapping({
      src_cfg: { ...dbConfig, port: Number(dbConfig.port) },
      tgt_cfg: { ...targetCfg, port: Number(targetCfg.port) },
      output_format: format,
      min_confidence: minConfidence,
    });

    setResult(res);
    setRows(res.details?.all_rows || []);
    setLoading(false);
  }

  /* ================= UPDATE ================= */
  function updateRow(i, key, value) {
    setRows(prev =>
      prev.map((r, idx) =>
        idx === i ? { ...r, [key]: value } : r
      )
    );
    setSaved(false);
  }

  /* ================= SAVE ================= */
  function saveChanges() {
    setSaved(true);
    alert("Changes saved. You can now download.");
  }

  /* ================= DOWNLOAD ================= */
  function download() {
    if (!saved || !rows.length) return;

    if (format === "csv") {
      const header = Object.keys(rows[0]).join(",");
      const body = rows
        .map(r =>
          Object.values(r)
            .map(v => `"${v ?? ""}"`)
            .join(",")
        )
        .join("\n");

      triggerDownload(
        `${header}\n${body}`,
        "mapping.csv",
        "text/csv"
      );
    }

    if (format === "json") {
      triggerDownload(
        JSON.stringify(rows, null, 2),
        "mapping.json",
        "application/json"
      );
    }

    if (format === "xlsx") {
      const ws = XLSX.utils.json_to_sheet(rows);
      const wb = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(wb, ws, "Mapping");
      XLSX.writeFile(wb, "mapping.xlsx");
    }
  }

  function triggerDownload(content, filename, type) {
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  }

  /* ================= UI ================= */
  return (
    <div className="space-y-10">

      {/* CONFIG */}
      <div className="bg-white border rounded-2xl p-8">
        <h2 className="text-lg font-extrabold mb-6">
          Mapping Configuration
        </h2>

        <div className="grid grid-cols-2 md:grid-cols-3 gap-6 mb-6">
          {Object.keys(targetCfg).map(k => (
            <div key={k} className="relative">
              <input
                type={
                  k === "password"
                    ? showPassword
                      ? "text"
                      : "password"
                    : "text"
                }
                value={targetCfg[k]}
                onChange={e =>
                  setTargetCfg({
                    ...targetCfg,
                    [k]: e.target.value,
                  })
                }
                placeholder={k.replace("_", " ")}
                className="border rounded-lg px-4 py-2 w-full pr-10"
              />

              {k === "password" && (
                <button
                  type="button"
                  onClick={() =>
                    setShowPassword(v => !v)
                  }
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500"
                >
                  {showPassword ? "Hide" : "Show"}
                </button>
              )}
            </div>
          ))}
        </div>

        <div className="grid grid-cols-3 gap-6 items-end">
          <select
            value={format}
            onChange={e => setFormat(e.target.value)}
            className="border rounded-lg px-4 py-2"
          >
            <option value="csv">CSV</option>
            <option value="json">JSON</option>
            <option value="xlsx">XLSX</option>
          </select>

          <div className="relative">
            <label className="text-xs font-bold flex items-center gap-2">
              Min Confidence
              <button
                type="button"
                onClick={() =>
                  setShowLegend(v => !v)
                }
                className="text-indigo-600 font-bold"
              >
                i
              </button>
            </label>

            <input
              type="number"
              step="0.05"
              min="0"
              max="1"
              value={minConfidence}
              onChange={e =>
                setMinConfidence(Number(e.target.value))
              }
              className="border rounded-lg px-4 py-2 w-full"
            />

            {showLegend && (
              <div className="absolute z-20 mt-2 w-[520px] bg-white border rounded-xl p-4 text-xs shadow-xl">
                <p className="font-bold mb-3">
                  Confidence Levels Legend
                </p>

                <table className="w-full">
                  <tbody>
                    <tr><td>≥ 0.90</td><td>🟢 Very High</td></tr>
                    <tr><td>0.80 – 0.89</td><td>🟢 High</td></tr>
                    <tr><td>0.65 – 0.79</td><td>🟡 Medium</td></tr>
                    <tr><td>0.50 – 0.64</td><td>🟠 Low</td></tr>
                    <tr><td>&lt; 0.50</td><td>🔴 Very Low</td></tr>
                  </tbody>
                </table>
              </div>
            )}
          </div>

          <button
            onClick={generate}
            className="bg-indigo-600 text-white px-6 py-3 rounded-xl font-bold"
          >
            {loading ? "Generating…" : "Generate Mapping"}
          </button>
        </div>
      </div>

      {/* RESULTS */}
      {rows.length > 0 && (
        <>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            {dashboard.map(([k, v]) => (
              <div key={k} className="bg-white border rounded-xl p-4">
                <div className="text-xs text-slate-500">{k}</div>
                <div className="text-xl font-extrabold">{v}</div>
              </div>
            ))}
          </div>

          <div className="bg-white border rounded-2xl">
            <div className="px-6 py-4 border-b font-extrabold">
              Editable Mapping Results
            </div>

            <div className="overflow-x-auto max-h-[500px]">
              <table className="min-w-full text-sm">
                <thead className="bg-slate-100 sticky top-0">
                  <tr>
                    {Object.keys(rows[0]).map(h => (
                      <th key={h} className="px-3 py-2 text-left">
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>

                <tbody>
                  {rows.map((r, i) => (
                    <tr key={i} className="border-t">
                      {Object.keys(r).map(k => (
                        <td key={k} className="px-3 py-2">
                          {k === "target_table" ? (
                            <select
                              value={r[k]}
                              onChange={e =>
                                updateRow(i, k, e.target.value)
                              }
                              className="w-full border rounded px-2 py-1"
                            >
                              {targetTableOptions.map(t => (
                                <option key={t} value={t}>{t}</option>
                              ))}
                            </select>
                          ) : k === "best_match_column" ? (
                            <select
                              value={r[k]}
                              onChange={e =>
                                updateRow(i, k, e.target.value)
                              }
                              className="w-full border rounded px-2 py-1"
                            >
                              {bestMatchColumnOptions.map(c => (
                                <option key={c} value={c}>{c}</option>
                              ))}
                            </select>
                          ) : (
                            <span>{r[k]}</span>
                          )}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="flex justify-end gap-4 px-6 py-4 border-t">
              <button
                onClick={saveChanges}
                className="bg-indigo-600 text-white px-5 py-2 rounded-lg"
              >
                Save Changes
              </button>

              <button
                onClick={download}
                disabled={!saved}
                className={`px-5 py-2 rounded-lg font-bold ${
                  saved
                    ? "bg-emerald-600 text-white"
                    : "bg-slate-300 text-slate-600"
                }`}
              >
                Download
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
