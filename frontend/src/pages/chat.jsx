import { useEffect, useRef, useState } from "react";
import { askQuestion } from "../api/client";
import logo from "../assets/logo.png";

export default function ChatPage({ onExit }) {
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);

  const [chats, setChats] = useState([
    {
      id: "chat-1",
      title: "New Chat",
      messages: [
        {
          role: "bot",
          text: "Hi 👋 I’m your Data Assistant. Ask me anything about your data!",
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

  function newChat() {
    const id = `chat-${Date.now()}`;
    const newOne = {
      id,
      title: "New Chat",
      messages: [
        {
          role: "bot",
          text: "✨ New chat started. Ask your question!",
        },
      ],
    };
    setChats((prev) => [newOne, ...prev]);
    setActiveChatId(id);
  }

  async function handleSend() {
    if (!question.trim() || loading) return;

    const q = question.trim();
    setQuestion("");

    setChats((prev) =>
      prev.map((chat) =>
        chat.id === activeChatId
          ? {
              ...chat,
              title: chat.title === "New Chat" ? q.slice(0, 24) : chat.title,
              messages: [...chat.messages, { role: "user", text: q }],
            }
          : chat
      )
    );

    setLoading(true);

    try {
      const res = await askQuestion({ question: q });

      setChats((prev) =>
        prev.map((chat) =>
          chat.id === activeChatId
            ? {
                ...chat,
                messages: [
                  ...chat.messages,
                  { role: "bot", text: res.result || "No answer found." },
                ],
              }
            : chat
        )
      );
    } catch (err) {
      console.error(err);
      setChats((prev) =>
        prev.map((chat) =>
          chat.id === activeChatId
            ? {
                ...chat,
                messages: [
                  ...chat.messages,
                  {
                    role: "bot",
                    text: "❌ Error while fetching response from backend.",
                  },
                ],
              }
            : chat
        )
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen w-full bg-slate-50">
      {/* TOP BAR (Same as Workspace) */}
      <header className="sticky top-0 z-30 border-b border-slate-200 bg-white/80 backdrop-blur">
        <div className="mx-auto max-w-7xl px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="rounded-xl bg-slate-900 px-3 py-2 shadow-sm">
              <img
                src={logo}
                alt="Logo"
                className="h-7 w-auto object-contain"
              />
            </div>

            <div className="leading-tight">
              <div className="text-sm font-extrabold text-slate-900">
                Schema Intelligence
              </div>
              <div className="text-xs text-slate-500">
                Workspace • Chatbot • Quick Insights
              </div>
            </div>
          </div>

          <button
            onClick={onExit}
            className="rounded-xl px-4 py-2 bg-red-50 border border-red-200 text-red-700 font-semibold hover:bg-red-100 transition"
          >
            Exit
          </button>
        </div>
      </header>

      {/* BODY */}
      <div className="mx-auto max-w-7xl px-4 py-7">
        <div className="grid grid-cols-1 lg:grid-cols-[320px_1fr] gap-6">
          {/* SIDEBAR */}
          <aside className="rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden flex flex-col">
            <div className="px-4 py-4 border-b border-slate-200 bg-gradient-to-r from-indigo-50 via-violet-50 to-fuchsia-50">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm font-extrabold text-slate-900">
                    Chat Sessions
                  </div>
                  <div className="text-xs text-slate-500 mt-1">
                    Your conversation history
                  </div>
                </div>

                <StatusChip color="emerald" text="Connected" />
              </div>

              <button
                onClick={newChat}
                className="w-full mt-4 rounded-xl px-4 py-3 font-semibold text-white
                           bg-gradient-to-r from-indigo-600 via-violet-600 to-fuchsia-600
                           shadow-md shadow-indigo-500/20 hover:shadow-lg hover:shadow-fuchsia-500/20 transition"
              >
                + New Chat
              </button>
            </div>

            <div className="p-3 space-y-2 flex-1 overflow-y-auto">
              {chats.map((c) => (
                <SideChatItem
                  key={c.id}
                  active={c.id === activeChatId}
                  title={c.title}
                  subtitle={c.messages?.[c.messages.length - 1]?.text || ""}
                  onClick={() => setActiveChatId(c.id)}
                />
              ))}
            </div>

            <div className="p-4 border-t border-slate-200 bg-slate-50">
              
            </div>
          </aside>

          {/* CHAT MAIN */}
          <main className="rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden flex flex-col">
            {/* CHAT HEADER */}
            <div className="px-6 py-5 border-b border-slate-200 bg-gradient-to-r from-indigo-50 via-violet-50 to-fuchsia-50">
              <h3 className="text-lg font-extrabold text-slate-900">
                {activeChat?.title || "Chat"}
              </h3>
              <p className="text-sm text-slate-600 mt-1">
                Get quick insights through summary of your data.
              </p>
            </div>

            {/* MESSAGES */}
            <div className="flex-1 p-6 overflow-y-auto space-y-4 bg-slate-50">
              {activeChat?.messages?.map((m, idx) => (
                <MessageBubble key={idx} role={m.role} text={m.text} />
              ))}

              {loading && (
                <div className="flex justify-start">
                  <div className="bg-white border border-slate-200 rounded-2xl px-4 py-3 text-sm text-slate-500 shadow-sm">
                    <TypingDots />
                  </div>
                </div>
              )}

              <div ref={bottomRef} />
            </div>

            {/* INPUT */}
            <div className="p-5 bg-white border-t border-slate-200">
              <div className="flex gap-3 items-center">
                <input
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleSend()}
                  placeholder="Type your question... (Example: top 3 employees joined recently)"
                  className="flex-1 rounded-xl border border-slate-200 bg-white px-4 py-3
                             focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-400 transition"
                />

                <button
                  onClick={handleSend}
                  disabled={loading}
                  className="rounded-xl px-6 py-3 font-semibold text-white
                             bg-gradient-to-r from-indigo-600 via-violet-600 to-fuchsia-600
                             shadow-md shadow-indigo-500/20 hover:shadow-lg hover:shadow-fuchsia-500/20 transition
                             disabled:opacity-60 disabled:cursor-not-allowed"
                >
                  Send
                </button>
              </div>

              <div className="mt-3 flex flex-wrap gap-2">
                <QuickPrompt onClick={() => setQuestion("Recently joined top 3 employees")}>
                  Recently joined top 3 employees
                </QuickPrompt>
                <QuickPrompt onClick={() => setQuestion("tell about incidents trend by risk level over time")}>
                  tell about incidents trend by risk level over time
                </QuickPrompt>
                <QuickPrompt onClick={() => setQuestion("Show department wise staff count")}>
                  Department wise staff count
                </QuickPrompt>
              </div>
            </div>
          </main>
        </div>
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
