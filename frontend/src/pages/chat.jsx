import { useEffect, useRef, useState } from "react";
import { loadKG, initRAG, askQuestion } from "../api/client";
import { v4 as uuidv4 } from "uuid";
import logo from "../assets/logo.png";

export default function ChatPage({ onExit, dbConfig }) {
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);

  /* ---------------- SESSION ---------------- */
  const [sessionId] = useState(() => uuidv4());
  const [ragReady, setRagReady] = useState(false);

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

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [activeChat?.messages, loading]);

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

      await loadKG({
        pg: dbConfig,
        neo4j,
      });

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
        messages: [
          {
            role: "bot",
            text: "New chat started. Ask your question after initialization.",
          },
        ],
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

  return (
    <div className="min-h-screen w-full bg-slate-50">
      {/* TOP BAR */}
      <header className="sticky top-0 z-30 border-b border-slate-200 bg-white/80 backdrop-blur">
        <div className="mx-auto max-w-7xl px-4 py-3 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="rounded-xl bg-slate-900 px-3 py-2 shadow-sm">
              <img src={logo} alt="Logo" className="h-7" />
            </div>
            <div>
              <div className="text-sm font-extrabold text-slate-900">
                Schema Intelligence
              </div>
              <div className="text-xs text-slate-500">
                Workspace • Chatbot
              </div>
            </div>
          </div>

          <button
            onClick={onExit}
            className="rounded-xl px-4 py-2 bg-red-50 border border-red-200 text-red-700 font-semibold hover:bg-red-100"
          >
            Exit
          </button>
        </div>
      </header>

      {/* BODY */}
      <div className="mx-auto max-w-7xl px-4 py-7">
        <div className="grid grid-cols-1 lg:grid-cols-[340px_1fr] gap-6">
          {/* LEFT SIDEBAR */}
          <aside className="rounded-2xl border border-slate-200 bg-white shadow-sm flex flex-col">
            <div className="p-4 border-b bg-gradient-to-r from-indigo-50 via-violet-50 to-fuchsia-50">
              <div className="text-sm font-bold uppercase tracking-wide text-slate-900">
                Neo4j Connection
              </div>
              <p className="text-xs text-slate-500 mt-1">
                Secure database connection settings
              </p>

              <div className="mt-4 space-y-4">
                <Input label="Neo4j URI" disabled={loading || ragReady} onChange={(v) => setNeo4j({ ...neo4j, uri: v })} />
                <Input label="Username" disabled={loading || ragReady} onChange={(v) => setNeo4j({ ...neo4j, user: v })} />
                <Input label="Password" type="password" disabled={loading || ragReady} onChange={(v) => setNeo4j({ ...neo4j, password: v })} />

                <button
                  onClick={initializeChat}
                  disabled={loading}
                  className="w-full rounded-xl px-4 py-2 font-semibold text-white
                             bg-gradient-to-r from-indigo-600 via-violet-600 to-fuchsia-600
                             shadow-md transition disabled:opacity-50"
                >
                  Initialize Chat
                </button>
              </div>
            </div>

            <div className="p-3 space-y-2 flex-1 overflow-y-auto">
              {chats.map((c) => (
                <SideChatItem
                  key={c.id}
                  active={c.id === activeChatId}
                  title={c.title}
                  subtitle={c.messages.at(-1)?.text || ""}
                  onClick={() => setActiveChatId(c.id)}
                />
              ))}
            </div>

            <div className="p-4 border-t bg-slate-50">
              <button
                onClick={newChat}
                className="w-full rounded-xl px-4 py-2 border border-slate-200 bg-white text-sm font-semibold hover:bg-slate-50"
              >
                New Chat
              </button>
            </div>
          </aside>

          {/* CHAT MAIN */}
          <main className="rounded-2xl border border-slate-200 bg-white shadow-sm flex flex-col">
            <div className="flex-1 p-6 overflow-y-auto space-y-4 bg-slate-50">
              {activeChat?.messages.map((m, i) => (
                <MessageBubble key={i} role={m.role} text={m.text} />
              ))}
              {loading && ragReady && <Spinner />}
              <div ref={bottomRef} />
            </div>

            {/* INPUT */}
            <div className="p-5 border-t">
              <div className="flex gap-3 items-center">
                <div className="relative flex-1">
                  <input
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleSend()}
                    disabled={!ragReady}
                    placeholder={
                      ragReady
                        ? "Type your question..."
                        : "Initialize Neo4j connection to start chatting"
                    }
                    className={`${inputClass} pr-10 ${
                      !ragReady ? "cursor-not-allowed" : ""
                    }`}
                  />
                  {!ragReady && (
                    <span className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400">
                      🔒
                    </span>
                  )}
                </div>

                <button
                  onClick={handleSend}
                  disabled={!ragReady || loading}
                  className="rounded-xl px-6 py-3 font-semibold text-white
                             bg-gradient-to-r from-indigo-600 via-violet-600 to-fuchsia-600
                             shadow-md transition disabled:opacity-50"
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

/* ---------------- HELPERS ---------------- */

function Input({ label, type = "text", disabled, onChange }) {
  return (
    <div>
      <label className="block text-xs font-semibold text-slate-600 mb-1">
        {label}
      </label>
      <input
        type={type}
        disabled={disabled}
        className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm
                   text-slate-900 placeholder:text-slate-400 shadow-sm
                   focus:outline-none focus:ring-2 focus:ring-indigo-500/20
                   disabled:bg-slate-100"
        onChange={(e) => onChange(e.target.value)}
      />
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

function SideChatItem({ title, subtitle, active, onClick }) {
  return (
    <button
      onClick={onClick}
      className={`w-full text-left rounded-xl border px-3 py-3 transition ${
        active
          ? "border-indigo-200 bg-indigo-50 shadow-sm"
          : "border-slate-200 bg-white hover:bg-slate-50"
      }`}
    >
      <div className="text-sm font-extrabold text-slate-900 truncate">
        {title}
      </div>
      <div className="text-xs text-slate-500 truncate mt-1">{subtitle}</div>
    </button>
  );
}

function MessageBubble({ role, text }) {
  const isUser = role === "user";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm shadow-sm ${
          isUser
            ? "bg-gradient-to-r from-indigo-600 via-violet-600 to-fuchsia-600 text-white"
            : "bg-white border border-slate-200 text-slate-800"
        }`}
      >
        {text}
      </div>
    </div>
  );
}

/* ------------------ UI COMPONENTS ------------------ */

function SideChatItem({ title, subtitle, active, onClick }) {
  return (
    <button
      onClick={onClick}
      className={`w-full text-left group flex flex-col rounded-xl border px-3 py-3 transition ${
        active
          ? "border-indigo-200 bg-gradient-to-r from-indigo-50 via-violet-50 to-fuchsia-50 shadow-sm"
          : "border-slate-200 bg-white hover:bg-slate-50"
      }`}
    >
      <div className="flex items-center justify-between gap-2">
        <p className="text-sm font-extrabold text-slate-900 truncate">{title}</p>
        {active && (
          <span className="text-[10px] px-2 py-1 rounded-full bg-indigo-600 text-white font-bold">
            ACTIVE
          </span>
        )}
      </div>

      <p className="text-xs text-slate-500 truncate mt-1">{subtitle}</p>
    </button>
  );
}

function MessageBubble({ role, text }) {
  const isUser = role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed shadow-sm ${
          isUser
            ? "bg-gradient-to-r from-indigo-600 via-violet-600 to-fuchsia-600 text-white"
            : "bg-white text-slate-800 border border-slate-200"
        }`}
      >
        {text}
      </div>
    </div>
  );
}

function TypingDots() {
  return (
    <div className="flex items-center gap-2">
      <span className="text-slate-500 font-semibold">Thinking</span>
      <span className="flex gap-1">
        <span className="w-2 h-2 bg-slate-300 rounded-full animate-bounce"></span>
        <span className="w-2 h-2 bg-slate-300 rounded-full animate-bounce [animation-delay:120ms]"></span>
        <span className="w-2 h-2 bg-slate-300 rounded-full animate-bounce [animation-delay:240ms]"></span>
      </span>
    </div>
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

function QuickPrompt({ children, onClick }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="text-xs font-semibold px-3 py-1.5 rounded-full border border-slate-200 bg-white
                 text-slate-600 hover:bg-slate-50 transition"
    >
      {children}
    </button>
  );
}
