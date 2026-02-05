// // // // import { useEffect, useMemo, useRef, useState } from "react";
// // // // import { v4 as uuidv4 } from "uuid";
// // // // import {
// // // //   loadKG,
// // // //   initRAG,
// // // //   askQuestion,
// // // // } from "../api/client";

// // // // export default function ChatbotPage({ dbConfig }) {
// // // //   const sessionId = useMemo(() => uuidv4(), []);
// // // //   const bottomRef = useRef(null);

// // // //   const [neo4j, setNeo4j] = useState({
// // // //     uri: "",
// // // //     user: "",
// // // //     password: "",
// // // //   });

// // // //   const [ready, setReady] = useState(false);
// // // //   const [loading, setLoading] = useState(false);
// // // //   const [messages, setMessages] = useState([]);
// // // //   const [question, setQuestion] = useState("");

// // // //   useEffect(() => {
// // // //     bottomRef.current?.scrollIntoView({ behavior: "smooth" });
// // // //   }, [messages]);

// // // //   async function initChat() {
// // // //     setLoading(true);

// // // //     await loadKG({ pg: dbConfig, neo4j });
// // // //     await initRAG({
// // // //       session_id: sessionId,
// // // //       neo4j_uri: neo4j.uri,
// // // //       neo4j_user: neo4j.user,
// // // //       neo4j_password: neo4j.password,
// // // //       neo4j_database: "neo4j",
// // // //     });

// // // //     setMessages([{ role: "bot", text: "Chat initialized." }]);
// // // //     setReady(true);
// // // //     setLoading(false);
// // // //   }

// // // //   async function send() {
// // // //     if (!question.trim()) return;
// // // //     const q = question;
// // // //     setQuestion("");
// // // //     setMessages((m) => [...m, { role: "user", text: q }]);
// // // //     const res = await askQuestion({
// // // //       session_id: sessionId,
// // // //       question: q,
// // // //     });
// // // //     setMessages((m) => [...m, { role: "bot", text: res.result }]);
// // // //   }

// // // //   return (
// // // //     <div className="bg-white border rounded-xl p-6 shadow-sm">
// // // //       <h2 className="text-lg font-bold mb-4">Chatbot</h2>

// // // //       {!ready && (
// // // //         <>
// // // //           {["uri", "user", "password"].map((k) => (
// // // //             <div key={k} className="mb-3">
// // // //               <label className="block text-xs font-bold mb-1">
// // // //                 {k}
// // // //               </label>
// // // //               <input
// // // //                 type={k === "password" ? "password" : "text"}
// // // //                 onChange={(e) =>
// // // //                   setNeo4j({ ...neo4j, [k]: e.target.value })
// // // //                 }
// // // //                 className="w-full border rounded px-3 py-2"
// // // //               />
// // // //             </div>
// // // //           ))}

// // // //           <button
// // // //             onClick={initChat}
// // // //             className="bg-indigo-600 text-white px-5 py-2 rounded font-semibold"
// // // //           >
// // // //             {loading ? "Initializing…" : "Initialize Chat"}
// // // //           </button>
// // // //         </>
// // // //       )}

// // // //       {ready && (
// // // //         <>
// // // //           <div className="h-96 border rounded p-4 bg-slate-50 overflow-y-auto space-y-2">
// // // //             {messages.map((m, i) => (
// // // //               <div
// // // //                 key={i}
// // // //                 className={`p-3 rounded max-w-[80%] ${
// // // //                   m.role === "user"
// // // //                     ? "bg-indigo-600 text-white ml-auto"
// // // //                     : "bg-white"
// // // //                 }`}
// // // //               >
// // // //                 {m.text}
// // // //               </div>
// // // //             ))}
// // // //             <div ref={bottomRef} />
// // // //           </div>

// // // //           <div className="flex gap-3 mt-3">
// // // //             <input
// // // //               value={question}
// // // //               onChange={(e) => setQuestion(e.target.value)}
// // // //               onKeyDown={(e) => e.key === "Enter" && send()}
// // // //               className="flex-1 border px-3 py-2 rounded"
// // // //               placeholder="Ask a question…"
// // // //             />
// // // //             <button
// // // //               onClick={send}
// // // //               className="bg-indigo-600 text-white px-5 py-2 rounded font-semibold"
// // // //             >
// // // //               Send
// // // //             </button>
// // // //           </div>
// // // //         </>
// // // //       )}
// // // //     </div>
// // // //   );
// // // // }
// // // import { useEffect, useMemo, useRef, useState } from "react";
// // // import { v4 as uuidv4 } from "uuid";
// // // import { loadKG, initRAG, askQuestion } from "../api/client";

// // // export default function ChatbotPage({ dbConfig }) {
// // //   const [sessionId, setSessionId] = useState(uuidv4());
// // //   const bottomRef = useRef(null);

// // //   const [neo4j, setNeo4j] = useState({
// // //     uri: "",
// // //     user: "",
// // //     password: "",
// // //   });

// // //   const [stage, setStage] = useState("config"); 
// // //   // config → loadingKG → showKG → chat

// // //   const [loading, setLoading] = useState(false);
// // //   const [messages, setMessages] = useState([]);
// // //   const [question, setQuestion] = useState("");

// // //   useEffect(() => {
// // //     bottomRef.current?.scrollIntoView({ behavior: "smooth" });
// // //   }, [messages]);

// // //   /* ================= INIT CHAT ================= */
// // //   async function initChat() {
// // //     setLoading(true);
// // //     setStage("loadingKG");

// // //     await loadKG({ pg: dbConfig, neo4j });
// // //     await initRAG({
// // //       session_id: sessionId,
// // //       neo4j_uri: neo4j.uri,
// // //       neo4j_user: neo4j.user,
// // //       neo4j_password: neo4j.password,
// // //       neo4j_database: "neo4j",
// // //     });

// // //     setStage("showKG");
// // //     setLoading(false);
// // //   }

// // //   /* ================= START CHAT ================= */
// // //   function startChat() {
// // //     setMessages([
// // //       { role: "bot", text: "Knowledge Graph loaded. You can start asking questions." },
// // //     ]);
// // //     setStage("chat");
// // //   }

// // //   /* ================= SEND QUESTION ================= */
// // //   async function send() {
// // //     if (!question.trim()) return;

// // //     const q = question;
// // //     setQuestion("");
// // //     setMessages(m => [...m, { role: "user", text: q }]);

// // //     const res = await askQuestion({
// // //       session_id: sessionId,
// // //       question: q,
// // //     });

// // //     setMessages(m => [...m, { role: "bot", text: res.result }]);
// // //   }

// // //   /* ================= NEW CHAT ================= */
// // //   function newChat() {
// // //     setSessionId(uuidv4());
// // //     setMessages([]);
// // //     setQuestion("");
// // //     setStage("chat");
// // //   }

// // //   /* ================= UI ================= */
// // //   return (
// // //     <div className="bg-white border rounded-2xl p-6 shadow-sm space-y-6">

// // //       {/* HEADER */}
// // //       <div className="flex justify-between items-center">
// // //         <h2 className="text-xl font-extrabold">Knowledge Graph Chatbot</h2>
// // //         {stage === "chat" && (
// // //           <button
// // //             onClick={newChat}
// // //             className="text-sm border px-3 py-1 rounded-lg hover:bg-slate-100"
// // //           >
// // //             New Chat
// // //           </button>
// // //         )}
// // //       </div>

// // //       {/* CONFIG */}
// // //       {stage === "config" && (
// // //         <>
// // //           {["uri", "user", "password"].map(k => (
// // //             <div key={k}>
// // //               <label className="block text-xs font-bold mb-1">
// // //                 Neo4j {k}
// // //               </label>
// // //               <input
// // //                 type={k === "password" ? "password" : "text"}
// // //                 onChange={e =>
// // //                   setNeo4j({ ...neo4j, [k]: e.target.value })
// // //                 }
// // //                 className="w-full border rounded-lg px-3 py-2"
// // //               />
// // //             </div>
// // //           ))}

// // //           <button
// // //             onClick={initChat}
// // //             className="bg-indigo-600 text-white px-6 py-2 rounded-xl font-bold"
// // //           >
// // //             Initialize Knowledge Graph
// // //           </button>
// // //         </>
// // //       )}

// // //       {/* KG LOADING */}
// // //       {stage === "loadingKG" && (
// // //         <div className="flex flex-col items-center py-12 space-y-4">
// // //           <div className="w-12 h-12 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin" />
// // //           <p className="text-sm text-slate-600">
// // //             Loading Knowledge Graph from databases…
// // //           </p>
// // //         </div>
// // //       )}

// // //       {/* KG PREVIEW */}
// // //       {stage === "showKG" && (
// // //         <div className="space-y-4">
// // //           <div className="border rounded-xl p-4 bg-slate-50">
// // //             <h3 className="font-bold mb-2">Knowledge Graph Loaded</h3>
// // //             <p className="text-sm text-slate-600">
// // //               Nodes and relationships have been created from your PostgreSQL data.
// // //             </p>

// // //             {/* Placeholder for real graph later */}
// // //             <div className="mt-4 h-48 border rounded-lg flex items-center justify-center text-slate-400">
// // //               Knowledge Graph Visualization
// // //             </div>
// // //           </div>

// // //           <button
// // //             onClick={startChat}
// // //             className="bg-emerald-600 text-white px-6 py-2 rounded-xl font-bold"
// // //           >
// // //             Start Chat
// // //           </button>
// // //         </div>
// // //       )}

// // //       {/* CHAT */}
// // //       {stage === "chat" && (
// // //         <>
// // //           <div className="h-[420px] border rounded-xl p-4 bg-slate-50 overflow-y-auto space-y-3">
// // //             {messages.map((m, i) => (
// // //               <div
// // //                 key={i}
// // //                 className={`px-4 py-2 rounded-xl max-w-[75%] ${
// // //                   m.role === "user"
// // //                     ? "bg-indigo-600 text-white ml-auto"
// // //                     : "bg-white border"
// // //                 }`}
// // //               >
// // //                 {m.text}
// // //               </div>
// // //             ))}
// // //             <div ref={bottomRef} />
// // //           </div>

// // //           <div className="flex gap-3">
// // //             <input
// // //               value={question}
// // //               onChange={e => setQuestion(e.target.value)}
// // //               onKeyDown={e => e.key === "Enter" && send()}
// // //               className="flex-1 border rounded-xl px-4 py-2"
// // //               placeholder="Ask a question about incidents, risks, actions…"
// // //             />
// // //             <button
// // //               onClick={send}
// // //               className="bg-indigo-600 text-white px-6 py-2 rounded-xl font-bold"
// // //             >
// // //               Send
// // //             </button>
// // //           </div>
// // //         </>
// // //       )}
// // //     </div>
// // //   );
// // // }
// // // import { useEffect, useMemo, useRef, useState } from "react";
// // // import { v4 as uuidv4 } from "uuid";
// // // import {
// // //   loadKG,
// // //   initRAG,
// // //   askQuestion,
// // // } from "../api/client";
// // // import KnowledgeGraph from "./KnowledgeGraph";

// // // export default function ChatbotPage({ dbConfig }) {
// // //   /* ================= SESSION ================= */
// // //   const sessionId = useMemo(() => uuidv4(), []);
// // //   const bottomRef = useRef(null);

// // //   /* ================= STAGES ================= */
// // //   // config → loadingKG → showKG → chat
// // //   const [stage, setStage] = useState("config");

// // //   /* ================= NEO4J ================= */
// // //   const [neo4j, setNeo4j] = useState({
// // //     uri: "",
// // //     user: "",
// // //     password: "",
// // //   });

// // //   /* ================= CHAT ================= */
// // //   const [messages, setMessages] = useState([]);
// // //   const [question, setQuestion] = useState("");
// // //   const [loading, setLoading] = useState(false);

// // //   /* ================= AUTOSCROLL ================= */
// // //   useEffect(() => {
// // //     bottomRef.current?.scrollIntoView({ behavior: "smooth" });
// // //   }, [messages]);

// // //   /* ================= LOAD KG ================= */
// // //   async function loadKnowledgeGraph() {
// // //     setStage("loadingKG");
// // //     setLoading(true);

// // //     try {
// // //       await loadKG({ pg: dbConfig, neo4j });

// // //       await initRAG({
// // //         session_id: sessionId,
// // //         neo4j_uri: neo4j.uri,
// // //         neo4j_user: neo4j.user,
// // //         neo4j_password: neo4j.password,
// // //         neo4j_database: "neo4j",
// // //       });

// // //       setStage("showKG");
// // //     } catch (err) {
// // //       alert("Failed to load Knowledge Graph");
// // //       setStage("config");
// // //     } finally {
// // //       setLoading(false);
// // //     }
// // //   }

// // //   /* ================= START CHAT ================= */
// // //   function startChat() {
// // //     setMessages([
// // //       { role: "bot", text: "Knowledge Graph is ready. You can ask questions now." },
// // //     ]);
// // //     setStage("chat");
// // //   }

// // //   /* ================= SEND QUESTION ================= */
// // //   async function send() {
// // //     if (!question.trim()) return;

// // //     const q = question;
// // //     setQuestion("");

// // //     setMessages((m) => [...m, { role: "user", text: q }]);

// // //     const res = await askQuestion({
// // //       session_id: sessionId,
// // //       question: q,
// // //     });

// // //     setMessages((m) => [...m, { role: "bot", text: res.result }]);
// // //   }

// // //   /* ================= NEW CHAT ================= */
// // //   function newChat() {
// // //     setMessages([
// // //       { role: "bot", text: "New chat started. Ask your next question." },
// // //     ]);
// // //   }

// // //   /* ================= UI ================= */
// // //   return (
// // //     <div className="bg-white border rounded-2xl p-6 shadow-sm space-y-6">

// // //       <h2 className="text-lg font-bold">Knowledge Graph Chatbot</h2>

// // //       {/* ================= CONFIG ================= */}
// // //       {stage === "config" && (
// // //         <div className="space-y-4">
// // //           {["uri", "user", "password"].map((k) => (
// // //             <div key={k}>
// // //               <label className="block text-xs font-bold mb-1">
// // //                 Neo4j {k}
// // //               </label>
// // //               <input
// // //                 type={k === "password" ? "password" : "text"}
// // //                 value={neo4j[k]}
// // //                 onChange={(e) =>
// // //                   setNeo4j({ ...neo4j, [k]: e.target.value })
// // //                 }
// // //                 className="w-full border rounded px-3 py-2"
// // //               />
// // //             </div>
// // //           ))}

// // //           <button
// // //             onClick={loadKnowledgeGraph}
// // //             className="bg-indigo-600 text-white px-6 py-2 rounded-xl font-bold"
// // //           >
// // //             Load Knowledge Graph
// // //           </button>
// // //         </div>
// // //       )}

// // //       {/* ================= LOADING ================= */}
// // //       {stage === "loadingKG" && (
// // //         <div className="flex flex-col items-center justify-center h-64 space-y-3">
// // //           <div className="animate-spin h-10 w-10 border-4 border-indigo-600 border-t-transparent rounded-full" />
// // //           <div className="text-sm text-slate-600">
// // //             Building Knowledge Graph from database…
// // //           </div>
// // //         </div>
// // //       )}

// // //       {/* ================= SHOW KG ================= */}
// // //       {stage === "showKG" && (
// // //         <div className="space-y-4">
// // //           <div className="text-sm text-slate-600">
// // //             Knowledge Graph Loaded. Review relationships before starting chat.
// // //           </div>

// // //           <KnowledgeGraph neo4j={neo4j} />

// // //           <button
// // //             onClick={startChat}
// // //             className="bg-emerald-600 text-white px-6 py-2 rounded-xl font-bold"
// // //           >
// // //             Start Chat
// // //           </button>
// // //         </div>
// // //       )}

// // //       {/* ================= CHAT ================= */}
// // //       {stage === "chat" && (
// // //         <>
// // //           <div className="flex justify-between items-center">
// // //             <div className="font-bold text-sm">Chat Session</div>
// // //             <button
// // //               onClick={newChat}
// // //               className="text-sm text-indigo-600 font-semibold"
// // //             >
// // //               New Chat
// // //             </button>
// // //           </div>

// // //           <div className="h-96 border rounded-xl p-4 bg-slate-50 overflow-y-auto space-y-2">
// // //             {messages.map((m, i) => (
// // //               <div
// // //                 key={i}
// // //                 className={`p-3 rounded-lg max-w-[80%] text-sm ${
// // //                   m.role === "user"
// // //                     ? "bg-indigo-600 text-white ml-auto"
// // //                     : "bg-white border"
// // //                 }`}
// // //               >
// // //                 {m.text}
// // //               </div>
// // //             ))}
// // //             <div ref={bottomRef} />
// // //           </div>

// // //           <div className="flex gap-3">
// // //             <input
// // //               value={question}
// // //               onChange={(e) => setQuestion(e.target.value)}
// // //               onKeyDown={(e) => e.key === "Enter" && send()}
// // //               className="flex-1 border px-3 py-2 rounded-lg"
// // //               placeholder="Ask a question about incidents, risks, actions…"
// // //             />
// // //             <button
// // //               onClick={send}
// // //               className="bg-indigo-600 text-white px-6 py-2 rounded-lg font-bold"
// // //             >
// // //               Send
// // //             </button>
// // //           </div>
// // //         </>
// // //       )}
// // //     </div>
// // //   );
// // // }
// // import { useEffect, useMemo, useRef, useState } from "react";
// // import { v4 as uuidv4 } from "uuid";
// // import { loadKG, initRAG, askQuestion } from "../api/client";

// // export default function ChatbotPage({ dbConfig }) {
// //   /* ================= SESSION ================= */
// //   const sessionId = useMemo(() => uuidv4(), []);
// //   const bottomRef = useRef(null);

// //   /* ================= STAGES ================= */
// //   // config → loading → chat
// //   const [stage, setStage] = useState("config");

// //   /* ================= NEO4J ================= */
// //   const [neo4j, setNeo4j] = useState({
// //     uri: "",
// //     user: "",
// //     password: "",
// //   });

// //   /* ================= CHAT ================= */
// //   const [messages, setMessages] = useState([]);
// //   const [question, setQuestion] = useState("");
// //   const [loading, setLoading] = useState(false);

// //   /* ================= AUTOSCROLL ================= */
// //   useEffect(() => {
// //     bottomRef.current?.scrollIntoView({ behavior: "smooth" });
// //   }, [messages]);

// //   /* ================= LOAD KG ================= */
// //   async function loadKnowledgeGraph() {
// //     setStage("loading");
// //     setLoading(true);

// //     try {
// //       await loadKG({ pg: dbConfig, neo4j });

// //       await initRAG({
// //         session_id: sessionId,
// //         neo4j_uri: neo4j.uri,
// //         neo4j_user: neo4j.user,
// //         neo4j_password: neo4j.password,
// //         neo4j_database: "neo4j",
// //       });

// //       setMessages([
// //         {
// //           role: "bot",
// //           text: "Knowledge Graph is ready. You can start asking questions.",
// //         },
// //       ]);

// //       setStage("chat");
// //     } catch (err) {
// //       alert("Failed to load Knowledge Graph");
// //       setStage("config");
// //     } finally {
// //       setLoading(false);
// //     }
// //   }

// //   /* ================= SEND QUESTION ================= */
// //   async function send() {
// //     if (!question.trim()) return;

// //     const q = question;
// //     setQuestion("");

// //     setMessages((m) => [...m, { role: "user", text: q }]);

// //     const res = await askQuestion({
// //       session_id: sessionId,
// //       question: q,
// //     });

// //     setMessages((m) => [...m, { role: "bot", text: res.result }]);
// //   }

// //   /* ================= VIEW KG (NEO4J BROWSER) ================= */
// //   function viewKnowledgeGraph() {
// //   if (!neo4j.uri || !neo4j.user || !neo4j.password) {
// //     alert("Neo4j credentials are missing");
// //     return;
// //   }

// //   const user = encodeURIComponent(neo4j.user);
// //   const pass = encodeURIComponent(neo4j.password);

// //   // Extract host from bolt://localhost:7687 or neo4j://localhost:7687
// //   const host = neo4j.uri
// //     .replace(/^neo4j:\/\//, "")
// //     .replace(/^bolt:\/\//, "")
// //     .split(":")[0];

// //   /**
// //    * Neo4j Browser supports basic-auth in URL.
// //    * This is the ONLY supported automation.
// //    */
// //   const url = `http://${user}:${pass}@${host}:7474/browser/`;

// //   window.open(url, "_blank", "noopener,noreferrer");
// // }

// //   /* ================= UI ================= */
// //   return (
// //     <div className="bg-white border rounded-2xl p-6 shadow-sm space-y-6">

// //       <h2 className="text-lg font-bold">Knowledge Graph Chatbot</h2>

// //       {/* ================= CONFIG ================= */}
// //       {stage === "config" && (
// //         <div className="space-y-4">
// //           {["uri", "user", "password"].map((k) => (
// //             <div key={k}>
// //               <label className="block text-xs font-bold mb-1">
// //                 Neo4j {k}
// //               </label>
// //               <input
// //                 type={k === "password" ? "password" : "text"}
// //                 value={neo4j[k]}
// //                 onChange={(e) =>
// //                   setNeo4j({ ...neo4j, [k]: e.target.value })
// //                 }
// //                 className="w-full border rounded px-3 py-2"
// //               />
// //             </div>
// //           ))}

// //           <button
// //             onClick={loadKnowledgeGraph}
// //             className="bg-indigo-600 text-white px-6 py-2 rounded-xl font-bold"
// //           >
// //             Load Knowledge Graph
// //           </button>
// //         </div>
// //       )}

// //       {/* ================= LOADING ================= */}
// //       {stage === "loading" && (
// //         <div className="flex flex-col items-center justify-center h-64 space-y-3">
// //           <div className="animate-spin h-10 w-10 border-4 border-indigo-600 border-t-transparent rounded-full" />
// //           <div className="text-sm text-slate-600">
// //             Knowledge Graph is loading…
// //           </div>
// //         </div>
// //       )}

// //       {/* ================= CHAT ================= */}
// //       {stage === "chat" && (
// //         <>
// //           {/* HEADER */}
// //           <div className="flex justify-between items-center">
// //             <div className="font-bold text-sm">Chat Session</div>

// //             <button
// //               onClick={viewKnowledgeGraph}
// //               className="bg-slate-100 border px-4 py-1.5 rounded-lg text-sm font-semibold hover:bg-slate-200"
// //             >
// //               View Knowledge Graph
// //             </button>
// //           </div>

// //           {/* CHAT WINDOW */}
// //           <div className="h-96 border rounded-xl p-4 bg-slate-50 overflow-y-auto space-y-2">
// //             {messages.map((m, i) => (
// //               <div
// //                 key={i}
// //                 className={`p-3 rounded-lg max-w-[80%] text-sm ${
// //                   m.role === "user"
// //                     ? "bg-indigo-600 text-white ml-auto"
// //                     : "bg-white border"
// //                 }`}
// //               >
// //                 {m.text}
// //               </div>
// //             ))}
// //             <div ref={bottomRef} />
// //           </div>

// //           {/* INPUT */}
// //           <div className="flex gap-3">
// //             <input
// //               value={question}
// //               onChange={(e) => setQuestion(e.target.value)}
// //               onKeyDown={(e) => e.key === "Enter" && send()}
// //               className="flex-1 border px-3 py-2 rounded-lg"
// //               placeholder="Ask a question about schema, tables, risks…"
// //             />
// //             <button
// //               onClick={send}
// //               className="bg-indigo-600 text-white px-6 py-2 rounded-lg font-bold"
// //             >
// //               Send
// //             </button>
// //           </div>
// //         </>
// //       )}
// //     </div>
// //   );
// // }
// import { useEffect, useMemo, useRef, useState } from "react";
// import { v4 as uuidv4 } from "uuid";
// import { loadKG, initRAG, askQuestion } from "../api/client";

// export default function ChatbotPage({ dbConfig }) {
//   /* ================= SESSION ================= */
//   const sessionId = useMemo(() => uuidv4(), []);
//   const bottomRef = useRef(null);

//   /* ================= STAGE ================= */
//   // config → loading → chat
//   const [stage, setStage] = useState("config");

//   /* ================= NEO4J ================= */
//   const [neo4j, setNeo4j] = useState({
//     uri: "",
//     user: "",
//     password: "",
//   });

//   /* ================= CHAT STATE ================= */
//   const [chats, setChats] = useState([]);
//   const [activeChatId, setActiveChatId] = useState(null);
//   const [question, setQuestion] = useState("");
//   const [loading, setLoading] = useState(false);

//   const activeChat = chats.find(c => c.id === activeChatId);

//   /* ================= AUTOSCROLL ================= */
//   useEffect(() => {
//     bottomRef.current?.scrollIntoView({ behavior: "smooth" });
//   }, [activeChat?.messages]);

//   /* ================= LOAD KNOWLEDGE GRAPH ================= */
//   async function loadKnowledgeGraph() {
//     setStage("loading");
//     setLoading(true);

//     try {
//       await loadKG({ pg: dbConfig, neo4j });

//       await initRAG({
//         session_id: sessionId,
//         neo4j_uri: neo4j.uri,
//         neo4j_user: neo4j.user,
//         neo4j_password: neo4j.password,
//         neo4j_database: "neo4j",
//       });

//       createNewChat("Welcome");

//       setStage("chat");
//     } catch {
//       alert("Failed to load Knowledge Graph");
//       setStage("config");
//     } finally {
//       setLoading(false);
//     }
//   }

//   /* ================= CHAT MANAGEMENT ================= */
//   function createNewChat(title = "New Chat") {
//     const id = uuidv4();
//     const newChat = {
//       id,
//       title,
//       messages: [
//         {
//           role: "bot",
//           text: "Knowledge Graph is ready. Ask your questions.",
//         },
//       ],
//     };

//     setChats(prev => [newChat, ...prev]);
//     setActiveChatId(id);
//   }

//   function selectChat(id) {
//     setActiveChatId(id);
//   }

//   /* ================= SEND MESSAGE ================= */
//   async function send() {
//     if (!question.trim() || !activeChat) return;

//     const q = question;
//     setQuestion("");

//     setChats(prev =>
//       prev.map(chat =>
//         chat.id === activeChatId
//           ? {
//               ...chat,
//               messages: [...chat.messages, { role: "user", text: q }],
//             }
//           : chat
//       )
//     );

//     const res = await askQuestion({
//       session_id: sessionId,
//       question: q,
//     });

//     setChats(prev =>
//       prev.map(chat =>
//         chat.id === activeChatId
//           ? {
//               ...chat,
//               messages: [...chat.messages, { role: "bot", text: res.result }],
//             }
//           : chat
//       )
//     );
//   }

//   /* ================= VIEW NEO4J BROWSER ================= */
//   function viewKnowledgeGraph() {
//     const user = encodeURIComponent(neo4j.user);
//     const pass = encodeURIComponent(neo4j.password);

//     const host = neo4j.uri
//       .replace(/^neo4j:\/\//, "")
//       .replace(/^bolt:\/\//, "")
//       .split(":")[0];

//     const url = `http://${user}:${pass}@${host}:7474/browser/`;
//     window.open(url, "_blank", "noopener,noreferrer");
//   }

//   /* ================= UI ================= */
//   return (
//     <div className="flex h-[720px] bg-white border rounded-2xl shadow-sm overflow-hidden">

//       {/* ================= SIDEBAR ================= */}
//       <div className="w-64 border-r bg-slate-50 flex flex-col">
//         <div className="p-4 font-extrabold text-sm">
//           Chats
//         </div>

//         <button
//           onClick={() => createNewChat()}
//           className="mx-4 mb-3 bg-indigo-600 text-white text-sm py-2 rounded-lg font-semibold"
//         >
//           + New Chat
//         </button>

//         <div className="flex-1 overflow-y-auto px-2 space-y-1">
//           {chats.map(chat => (
//             <button
//               key={chat.id}
//               onClick={() => selectChat(chat.id)}
//               className={`w-full text-left px-3 py-2 rounded-lg text-sm ${
//                 chat.id === activeChatId
//                   ? "bg-indigo-100 font-semibold"
//                   : "hover:bg-slate-200"
//               }`}
//             >
//               {chat.title}
//             </button>
//           ))}
//         </div>
//       </div>

//       {/* ================= MAIN ================= */}
//       <div className="flex-1 flex flex-col">

//         {/* ================= HEADER ================= */}
//         <div className="border-b px-6 py-3 flex justify-between items-center">
//           <div className="font-bold text-sm">
//             Knowledge Graph Chatbot
//           </div>

//           {stage === "chat" && (
//             <button
//               onClick={viewKnowledgeGraph}
//               className="text-sm font-semibold border px-4 py-1.5 rounded-lg hover:bg-slate-100"
//             >
//               View Knowledge Graph
//             </button>
//           )}
//         </div>

//         {/* ================= CONFIG ================= */}
//         {stage === "config" && (
//           <div className="p-6 space-y-4">
//             {["uri", "user", "password"].map(k => (
//               <div key={k}>
//                 <label className="block text-xs font-bold mb-1">
//                   Neo4j {k}
//                 </label>
//                 <input
//                   type={k === "password" ? "password" : "text"}
//                   value={neo4j[k]}
//                   onChange={e =>
//                     setNeo4j({ ...neo4j, [k]: e.target.value })
//                   }
//                   className="w-full border rounded px-3 py-2"
//                 />
//               </div>
//             ))}

//             <button
//               onClick={loadKnowledgeGraph}
//               className="bg-indigo-600 text-white px-6 py-2 rounded-xl font-bold"
//             >
//               Load Knowledge Graph
//             </button>
//           </div>
//         )}

//         {/* ================= LOADING ================= */}
//         {stage === "loading" && (
//           <div className="flex-1 flex flex-col items-center justify-center space-y-3">
//             <div className="animate-spin h-10 w-10 border-4 border-indigo-600 border-t-transparent rounded-full" />
//             <div className="text-sm text-slate-600">
//               Knowledge Graph is loading…
//             </div>
//           </div>
//         )}

//         {/* ================= CHAT ================= */}
//         {stage === "chat" && activeChat && (
//           <>
//             <div className="flex-1 overflow-y-auto p-6 space-y-3 bg-slate-50">
//               {activeChat.messages.map((m, i) => (
//                 <div
//                   key={i}
//                   className={`max-w-[75%] px-4 py-3 rounded-xl text-sm ${
//                     m.role === "user"
//                       ? "bg-indigo-600 text-white ml-auto"
//                       : "bg-white border"
//                   }`}
//                 >
//                   {m.text}
//                 </div>
//               ))}
//               <div ref={bottomRef} />
//             </div>

//             <div className="border-t p-4 flex gap-3">
//               <input
//                 value={question}
//                 onChange={e => setQuestion(e.target.value)}
//                 onKeyDown={e => e.key === "Enter" && send()}
//                 placeholder="Ask a question…"
//                 className="flex-1 border rounded-lg px-4 py-2"
//               />
//               <button
//                 onClick={send}
//                 className="bg-indigo-600 text-white px-6 rounded-lg font-bold"
//               >
//                 Send
//               </button>
//             </div>
//           </>
//         )}
//       </div>
//     </div>
//   );
// }
import { useEffect, useMemo, useRef, useState } from "react";
import { askQuestion } from "../api/client";

/* ================= SESSION KEYS ================= */
const SESSION_KEY = "rag_session_id";
const KG_READY_KEY = "kg_initialized";
const NEO4J_CFG_KEY = "neo4j_cfg";

export default function ChatbotPage({ onExit }) {
  /* ================= SESSION ================= */
  const sessionId = useMemo(
    () => sessionStorage.getItem(SESSION_KEY),
    []
  );

  const kgReady = sessionStorage.getItem(KG_READY_KEY) === "true";

  const neo4j = useMemo(() => {
    const raw = sessionStorage.getItem(NEO4J_CFG_KEY);
    return raw ? JSON.parse(raw) : null;
  }, []);

  /* ================= GUARD ================= */
  if (!sessionId || !kgReady || !neo4j?.uri) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-100">
        <div className="bg-white p-8 rounded-2xl shadow-xl text-center space-y-4">
          <h2 className="text-lg font-extrabold text-slate-800">
            Session Not Initialized
          </h2>
          <p className="text-sm text-slate-600">
            Please return to configuration and initialize the Knowledge Graph.
          </p>
          <button
            onClick={onExit}
            className="px-6 py-2 rounded-lg bg-indigo-600 text-white font-semibold"
          >
            Go to Configuration
          </button>
        </div>
      </div>
    );
  }

  /* ================= CHAT STATE ================= */
  const [messages, setMessages] = useState(() => [
    {
      role: "bot",
      text: "Knowledge Graph is ready. Ask questions about your data.",
    },
  ]);

  const [input, setInput] = useState("");
  const [thinking, setThinking] = useState(false);

  const bottomRef = useRef(null);

  /* ================= AUTOSCROLL ================= */
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, thinking]);

  /* ================= SEND ================= */
  async function send() {
    if (!input.trim() || thinking) return;

    const q = input;
    setInput("");
    setThinking(true);

    setMessages((m) => [...m, { role: "user", text: q }]);

    try {
      const res = await askQuestion({
        session_id: sessionId,
        question: q,
      });

      setMessages((m) => [
        ...m,
        { role: "bot", text: res.result },
      ]);
    } catch {
      setMessages((m) => [
        ...m,
        {
          role: "bot",
          text: "An error occurred while generating the response.",
        },
      ]);
    } finally {
      setThinking(false);
    }
  }

  /* ================= NEW CHAT ================= */
  function newChat() {
    setMessages([
      {
        role: "bot",
        text: "New conversation started. Ask your next question.",
      },
    ]);
  }

  /* ================= VIEW KG ================= */
  function viewKnowledgeGraph() {
    const host = neo4j.uri
      .replace(/^neo4j:\/\//, "")
      .replace(/^bolt:\/\//, "")
      .split(":")[0];

    window.open(`http://${host}:7474/browser/`, "_blank");
  }

  /* ================= UI ================= */
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-indigo-50
                    flex flex-col">

      {/* ================= HEADER ================= */}
      <header className="bg-white border-b px-6 py-4 flex justify-between items-center">
        <h1 className="text-lg font-extrabold text-indigo-700">
          Knowledge Graph Assistant
        </h1>

        <div className="flex gap-3">
          <button
            onClick={newChat}
            className="px-4 py-2 rounded-lg border bg-white
                       text-sm font-semibold hover:bg-slate-100"
          >
            New Chat
          </button>

          <button
            onClick={viewKnowledgeGraph}
            className="px-4 py-2 rounded-lg border bg-white
                       text-sm font-semibold hover:bg-slate-100"
          >
            View Knowledge Graph
          </button>

          <button
            onClick={onExit}
            className="px-4 py-2 rounded-lg bg-red-600
                       text-white text-sm font-semibold"
          >
            Exit
          </button>
        </div>
      </header>

      {/* ================= CHAT ================= */}
      <main className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.map((m, i) => (
          <div
            key={i}
            className={`max-w-[72%] px-4 py-3 rounded-xl text-sm ${
              m.role === "user"
                ? "ml-auto bg-indigo-600 text-white"
                : "bg-white border"
            }`}
          >
            {m.text}
          </div>
        ))}

        {thinking && (
          <div className="bg-white border rounded-lg px-4 py-2
                          text-sm w-fit">
            Generating response…
          </div>
        )}

        <div ref={bottomRef} />
      </main>

      {/* ================= INPUT ================= */}
      <footer className="bg-white border-t px-6 py-4 flex gap-3">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send()}
          disabled={thinking}
          placeholder="Ask a question about your schema, risks, or relationships"
          className="flex-1 px-4 py-3 rounded-lg border
                     disabled:bg-slate-100"
        />

        <button
          onClick={send}
          disabled={thinking}
          className="px-6 rounded-lg font-semibold text-white
                     bg-indigo-600 hover:bg-indigo-700
                     disabled:opacity-50"
        >
          Send
        </button>
      </footer>
    </div>
  );
}
