import { useEffect, useRef, useState } from "react";
import { askQuestion } from "../api/client";
import ChatBubble from "../components/ChatBubble";
import { CodeBlock } from "../components/CodeBlock";
import { Button } from "../components/Button";
import { Loader } from "../components/Loader";
import { api } from "../api/client"; // To get config

// Main Chat Page Component
export default function ChatPage({ onExit }) {
  // CONFIG & SETTINGS STATE
  const [configOptions, setConfigOptions] = useState({
    client_ids: [],
    agent_types: [],
    model_names: [],
  });
  const [chatSettings, setChatSettings] = useState({
    client_id: "",
    agent_name: "",
    model_name: "",
  });

  // CHAT STATE
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [chats, setChats] = useState([]);
  const [activeChatId, setActiveChatId] = useState(null);

  // FULL HISTORY DATA for download
  const [fullHistoryData, setFullHistoryData] = useState([]);

  const activeChat = chats.find((c) => c.id === activeChatId);
  const bottomRef = useRef(null);

  // Initial data fetch for config dropdowns
  useEffect(() => {
    async function fetchConfig() {
      try {
        const res = await api.get("/nl2sql/config");
        const data = res.data;
        setConfigOptions(data);
        // Set initial chat settings from fetched config
        setChatSettings({
          client_id: data.client_ids[0] || "",
          agent_name: data.agent_types[0] || "",
          model_name: data.model_names[0] || "",
        });
        // Start the first chat automatically
        if (chats.length === 0) {
          newChat(data);
        }
      } catch (error) {
        console.error("Failed to fetch config:", error);
      }
    }
    fetchConfig();
  }, []);

  // Effect to scroll to the latest message
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [activeChat?.messages, loading]);

  // Function to create a new chat session
  function newChat(currentConfig) {
    const config = currentConfig || configOptions;
    if (!config.client_ids.length) return; // Don't create chat if config is not loaded

    const id = `chat-${Date.now()}`;
    const initialMessage = `Hi! I'm your AI assistant, ready to answer questions about the **${
      chatSettings.client_id || config.client_ids[0]
    }** database. What can I help you with?`;

    const newSession = {
      id,
      title: "New Chat",
      messages: [{ role: "assistant", summary: initialMessage }],
    };
    setChats((prev) => [newSession, ...prev]);
    setActiveChatId(id);
  }

  // Function to handle sending a message
  async function handleSend() {
    const q = question.trim();
    if (!q || loading || !chatSettings.client_id) return;

    setQuestion("");

    // Add user message to the active chat
    const userMessage = { role: "user", summary: q };
    const updatedMessages = [...(activeChat.messages || []), userMessage];

    setChats((prev) =>
      prev.map((chat) =>
        chat.id === activeChatId
          ? {
              ...chat,
              title: chat.title === "New Chat" ? q.slice(0, 30) + "..." : chat.title,
              messages: updatedMessages,
            }
          : chat
      )
    );

    setLoading(true);

    try {
      const payload = {
        user_message: q,
        history: activeChat.messages.map((m) => ({
          role: m.role,
          content: m.summary, // Send only the text summary as history content
        })),
        ...chatSettings,
      };

      const res = await askQuestion(payload);

      // Add bot response to the active chat
      const botMessage = { role: "assistant", ...res };
      setChats((prev) =>
        prev.map((chat) =>
          chat.id === activeChatId
            ? { ...chat, messages: [...updatedMessages, botMessage] }
            : chat
        )
      );

      // Update full history for download
      if (res.full_history) {
        setFullHistoryData(res.full_history);
      }

    } catch (err) {
      console.error(err);
      const errorText =
        err.response?.data?.detail || "An error occurred while fetching the response.";
      const errorMessage = { role: "assistant", error: errorText };
      setChats((prev) =>
        prev.map((chat) =>
          chat.id === activeChatId
            ? { ...chat, messages: [...updatedMessages, errorMessage] }
            : chat
        )
      );
    } finally {
      setLoading(false);
    }
  }

  function handleDownloadHistory() {
    if (!fullHistoryData || fullHistoryData.length === 0) {
      alert("No chat history available to download.");
      return;
    }
    const jsonString = JSON.stringify(fullHistoryData, null, 2);
    const blob = new Blob([jsonString], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `chat_history_${Date.now()}.json`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }


  return (
    <>
      <div className="h-screen w-full bg-slate-50 grid grid-cols-1 lg:grid-cols-[340px_1fr]">
        {/* --- SIDEBAR --- */}
        <aside className="bg-white border-r border-slate-200 p-4 flex flex-col gap-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-bold text-slate-800">KG Assistant</h2>
              <p className="text-xs text-slate-500">Conversational NL2SQL</p>
            </div>
            <span className="text-xs px-3 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-700 font-semibold">
              Connected
            </span>
          </div>

          <Button onClick={() => newChat()} variant="primary" className="w-full">
            + New Chat
          </Button>

          <div className="flex gap-2">
            {/* Download Metrics as a direct link */}
            <a
              href="http://localhost:8000/nl2sql/download-metrics"
              target="_blank" // Open in new tab
              rel="noopener noreferrer" // Security best practice
              className="w-full text-xs inline-flex items-center justify-center rounded-2xl px-3 py-2 font-semibold transition
                         bg-indigo-50 text-indigo-700 border border-indigo-200 hover:bg-indigo-100"
            >
              Download Query Metrics
            </a>
            {/* Placeholder for future download history button */}
            <Button onClick={handleDownloadHistory} variant="soft" className="w-full text-xs" disabled={fullHistoryData.length === 0}>
              Download History
            </Button>
          </div>

          {/* CHAT HISTORY */}
          <div className="flex-1 space-y-2 overflow-y-auto pr-1 -mr-1">
            <p className="text-xs font-semibold text-slate-500 px-2 uppercase">
              Chat History
            </p>
            {chats.map((c) => (
              <button
                key={c.id}
                onClick={() => setActiveChatId(c.id)}
                className={`w-full text-left px-3 py-2.5 rounded-xl border transition ${ 
                  c.id === activeChatId
                    ? "bg-indigo-50 border-indigo-200"
                    : "bg-white hover:bg-slate-50 border-slate-200"
                }`}
              >
                <p className="text-sm font-semibold text-slate-800 truncate">
                  {c.title}
                </p>
                <p className="text-xs text-slate-500 truncate mt-1">
                  {c.messages?.[c.messages.length - 1]?.summary}
                </p>
              </button>
            ))}
          </div>

          {/* SETTINGS */}
          <div className="border-t border-slate-200 pt-4 space-y-3">
            <p className="text-xs font-semibold text-slate-500 px-2 uppercase">
              Settings
            </p>
            <SettingSelect
              label="Client ID"
              value={chatSettings.client_id}
              onChange={(e) =>
                setChatSettings((p) => ({ ...p, client_id: e.target.value }))
              }
              options={configOptions.client_ids}
            />
            <SettingSelect
              label="Agent Type"
              value={chatSettings.agent_name}
              onChange={(e) =>
                setChatSettings((p) => ({ ...p, agent_name: e.target.value }))
              }
              options={configOptions.agent_types}
            />
            <SettingSelect
              label="Model Name"
              value={chatSettings.model_name}
              onChange={(e) =>
                setChatSettings((p) => ({ ...p, model_name: e.target.value }))
              }
              options={configOptions.model_names}
            />
          </div>

          <Button onClick={onExit} variant="danger" className="w-full">
            Exit Workspace
          </Button>
        </aside>

        {/* --- CHAT PANEL --- */}
        <main className="flex flex-col h-screen bg-slate-100">
          <div className="p-4 border-b bg-white/70 backdrop-blur-lg">
            <h3 className="text-lg font-bold text-slate-800">
              {activeChat?.title || "Chat"}
            </h3>
            <p className="text-sm text-slate-500">
              Ask questions to get summaries and data from the Knowledge Graph.
            </p>
          </div>

          {/* MESSAGES */}
          <div className="flex-1 p-6 overflow-y-auto space-y-6">
            {activeChat?.messages?.map((m, idx) => (
              <Message key={idx} message={m} />
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-white border border-slate-200 rounded-2xl px-4 py-3 shadow-sm">
                  <TypingDots />
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          {/* INPUT AREA */}
          <div className="p-4 bg-white border-t border-slate-200">
            <div className="flex gap-3">
              <input
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSend()}
                placeholder="Type your question... (e.g., Show top 5 employees with most incidents)"
                className="flex-1 w-full rounded-xl border border-slate-300 px-4 py-3 outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
              <Button
                onClick={handleSend}
                disabled={loading || !question.trim()}
                className="px-6"
              >
                Send
              </Button>
            </div>
          </div>
        </main>
      </div>
    </>
  );
}

// Sub-component for rendering a single message
function Message({ message }) {
  if (message.role === "user") {
    return <ChatBubble role="user" text={message.summary} />;
  }

  // Determine chart suggestion based on data
  const chartSuggestion =
    message.dataframe && message.dataframe.length > 0
      ? getChartSuggestion(message.dataframe)
      : null;

  // Handle bot messages, which can have summary, sql, dataframe, or error
  return (
    <div className="space-y-4">
      {message.summary && <ChatBubble role="assistant" text={message.summary} />}
      {message.sql && (
        <div className="max-w-[80%] min-w-0">
          <CodeBlock value={message.sql} />
        </div>
      )}
      {message.dataframe && message.dataframe.length > 0 && (
        <div className="max-w-[80%] min-w-0 space-y-3">
          <DataTable data={message.dataframe} />
          {chartSuggestion && (
            <div className="rounded-2xl bg-indigo-50 border border-indigo-200 text-indigo-800 p-3 text-sm font-medium">
              <p>
                💡 **Suggestion:** You could visualize this data as a{