import { useEffect, useRef, useState } from "react";
import { loadKG, initRAG, askQuestion } from "../api/client";
import { v4 as uuidv4 } from "uuid";
import logo from "../assets/logo.png";

/* =========================================================
   MAIN PAGE
========================================================= */

export default function ChatPage({ onExit, dbConfig }) {
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [ragReady, setRagReady] = useState(false);

  /* ---------------- SESSION ---------------- */
  const [sessionId] = useState(() => uuidv4());

  /* ---------------- NEO4J CONFIG ---------------- */
  const [neo4j, setNeo4j] = useState({
    uri: "",
    user: "",
    password: "",
  });

  /* ---------------- CHAT STATE ---------------- */
  const [chats, setChats] = useState([
    {
      id: "chat-1",
      title: "New Chat",
      messages: [
        {
          role: "bot",
          text: "Chat will be available once initialization is complete.",
        },
      ],
    },
  ]);

  const [activeChatId, setActiveChatId] = useState("chat-1");
  const activeChat = chats.find((c) => c.id === activeChatId);
  const bottomRef = useRef(null);

  /* ---------------- AUTO SCROLL ---------------- */
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [activeChat?.messages, loading]);

  /* ---------------- HELPERS ---------------- */
  function push(role, text) {
    setChats((prev) =>
      prev.map((c) =>
        c.id === activeChatId
          ? { ...c, messages: [...c.messages, { role, text }] }
          : c
      )
    );
  }

  /* ---------------- INITIALIZE CHAT ---------------- */
  async function initializeChat() {
    try {
      setLoading(true);
      push("bot", "Initializing knowledge graph...");

      await loadKG({ pg: dbConfig, neo4j });

      await initRAG({
        session_id: sessionId,
        neo4j_uri: neo4j.uri,
        neo4j_user: neo4j.user,
        neo4j_password: neo4j.password,
        neo4j_database: "neo4j",
      });

      setRagReady(true);
      push("bot", "Initialization complete. You may start asking questions.");
    } catch (err) {
      console.error(err);
      push("bot", "Initialization failed. Please verify Neo4j details.");
    } finally {
      setLoading(false);
    }
  }

  /* ---------------- SEND MESSAGE ---------------- */
  async function handleSend() {
    if (!question.trim() || loading || !ragReady) return;

    const q = question.trim();
    setQuestion("");

    setChats((prev) =>
      prev.map((c) =>
        c.id === activeChatId
          ? {
              ...c,
              title: c.title === "New Chat" ? q.slice(0, 24) : c.title,
              messages: [...c.messages, { role: "user", text: q }],
            }
          : c
      )
    );

    setLoading(true);
    try {
      const res = await askQuestion({
        session_id: sessionId,
        question: q,
      });
      push("bot", res.result || "No answer found.");
    } catch (err) {
      console.error(err);
      push("bot", "Error while fetching response.");
    } finally {
      setLoading(false);
    }
  }

  /* ---------------- NEW CHAT ---------------- */
  function newChat() {
    const id = `chat-${Date.now()}`;
    setChats((prev) => [
      {
        id,
        title: "New Chat",
        messages: [{ role: "bot", text: "New chat started." }],
      },
      ...prev,
    ]);
    setActiveChatId(id);
  }

  const inputClass =
    "w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm " +
    "text-slate-900 placeholder:text-slate-400 shadow-sm transition " +
    "focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 " +
    "disabled:bg-slate-100 disabled:text-slate-400";

  /* =========================================================
     RENDER
  ========================================================= */

  return (
    <div className="min-h-screen bg-slate-50">
      {/* ================= TOP BAR ================= */}
      <header className="sticky top-0 z-30 border-b bg-white/80 backdrop-blur">
        <div className="max-w-7xl mx-auto px-4 py-3 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="bg-slate-900 rounded-xl px-3 py-2">
              <img src={logo} alt="Logo" className="h-7" />
            </div>
            <div>
              <p className="text-sm font-extrabold">Schema Intelligence</p>
              <p className="text-xs text-slate-500">Workspace • Chatbot</p>
            </div>
          </div>

          <button
            onClick={onExit}
            className="px-4 py-2 rounded-xl bg-red-50 border border-red-200 text-red-700 font-semibold"
          >
            Exit
          </button>
        </div>
      </header>

      {/* ================= BODY ================= */}
      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-[340px_1fr] gap-6">

          {/* ================= SIDEBAR ================= */}
          <aside className="bg-white rounded-2xl border shadow-sm flex flex-col">
            <div className="p-4 border-b bg-gradient-to-r from-indigo-50 via-violet-50 to-fuchsia-50">
              <p className="text-sm font-bold uppercase tracking-wide">
                Neo4j Connection
              </p>
              <p className="text-xs text-slate-500 mt-1">
                Secure database connection settings
              </p>

              <div className="mt-4 space-y-4">
                <FormInput
                  label="Neo4j URI"
                  disabled={loading || ragReady}
                  onChange={(v) => setNeo4j({ ...neo4j, uri: v })}
                />
                <FormInput
                  label="Username"
                  disabled={loading || ragReady}
                  onChange={(v) => setNeo4j({ ...neo4j, user: v })}
                />
                <FormInput
                  label="Password"
                  type="password"
                  disabled={loading || ragReady}
                  onChange={(v) => setNeo4j({ ...neo4j, password: v })}
                />

                <button
                  onClick={initializeChat}
                  disabled={loading}
                  className="w-full py-2 rounded-xl bg-indigo-600 text-white font-semibold disabled:opacity-50"
                >
                  Initialize Chat
                </button>
              </div>
            </div>

            <div className="flex-1 p-3 space-y-2 overflow-y-auto">
              {chats.map((c) => (
                <ChatListItem
                  key={c.id}
                  title={c.title}
                  subtitle={c.messages.at(-1)?.text}
                  active={c.id === activeChatId}
                  onClick={() => setActiveChatId(c.id)}
                />
              ))}
            </div>

            <div className="p-4 border-t bg-slate-50">
              <button
                onClick={newChat}
                className="w-full py-2 rounded-xl border bg-white font-semibold"
              >
                New Chat
              </button>
            </div>
          </aside>

          {/* ================= CHAT ================= */}
          <main className="bg-white rounded-2xl border shadow-sm flex flex-col">
            <div className="flex-1 p-6 overflow-y-auto space-y-4 bg-slate-50">
              {activeChat?.messages.map((m, i) => (
                <ChatBubble key={i} role={m.role} text={m.text} />
              ))}
              {loading && ragReady && <Spinner />}
              <div ref={bottomRef} />
            </div>

            <div className="p-5 border-t">
              <div className="flex gap-3">
                <div className="relative flex-1">
                  <input
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleSend()}
                    disabled={!ragReady}
                    placeholder={
                      ragReady
                        ? "Type your question..."
                        : "Initialize Neo4j to start chatting"
                    }
                    className={`${inputClass} pr-10`}
                  />
                  {!ragReady && (
                    <span className="absolute right-3 top-1/2 -translate-y-1/2">
                      🔒
                    </span>
                  )}
                </div>

                <button
                  onClick={handleSend}
                  disabled={!ragReady || loading}
                  className="px-6 rounded-xl bg-indigo-600 text-white font-semibold disabled:opacity-50"
                >
                  Send
                </button>
              </div>
            </div>
          </main>
        </div>
      </div>
    </div>
  );
}

/* =========================================================
   COMPONENTS
========================================================= */

function FormInput({ label, type = "text", disabled, onChange }) {
  return (
    <div>
      <label className="block text-xs font-semibold text-slate-600 mb-1">
        {label}
      </label>
      <input
        type={type}
        disabled={disabled}
        onChange={(e) => onChange(e.target.value)}
        className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm
                   focus:outline-none focus:ring-2 focus:ring-indigo-500/20
                   disabled:bg-slate-100"
      />
    </div>
  );
}

function ChatListItem({ title, subtitle, active, onClick }) {
  return (
    <button
      onClick={onClick}
      className={`w-full text-left rounded-xl px-3 py-3 border transition ${
        active
          ? "bg-indigo-50 border-indigo-300"
          : "bg-white border-slate-200 hover:bg-slate-50"
      }`}
    >
      <p className="text-sm font-bold truncate">{title}</p>
      <p className="text-xs text-slate-500 truncate mt-1">{subtitle}</p>
    </button>
  );
}

function ChatBubble({ role, text }) {
  const isUser = role === "user";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[75%] px-4 py-3 rounded-2xl text-sm shadow-sm ${
          isUser
            ? "bg-indigo-600 text-white"
            : "bg-white border border-slate-200"
        }`}
      >
        {text}
      </div>
    </div>
  );
}

function Spinner() {
  return (
    <div className="flex justify-center py-2">
      <div className="h-5 w-5 animate-spin rounded-full border-2 border-slate-300 border-t-indigo-600" />
    </div>
  );
}
