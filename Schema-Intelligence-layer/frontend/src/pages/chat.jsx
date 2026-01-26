import { useEffect, useRef, useState } from "react";
import { askQuestion, getMetrics } from "../api/client";
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

  // METRICS STATE
  const [metrics, setMetrics] = useState(null);
  const [isMetricsOpen, setIsMetricsOpen] = useState(false);

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

  async function handleViewMetrics() {
    try {
      const metricsData = await getMetrics();
      setMetrics(metricsData);
      setIsMetricsOpen(true);
    } catch (error) {
      console.error("Failed to fetch metrics:", error);
      alert("Could not load metrics. Please check the backend server.");
    }
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
            <Button onClick={handleViewMetrics} variant="soft" className="w-full text-xs">
              View Query Metrics
            </Button>
            {/* Placeholder for future download history button */}
            <Button disabled variant="soft" className="w-full text-xs">
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
      {isMetricsOpen && <MetricsModal metrics={metrics} onClose={() => setIsMetricsOpen(false)} />}
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
                💡 **Suggestion:** You could visualize this data as a{" "}
                <strong>{chartSuggestion}</strong>.
              </p>
            </div>
          )}
        </div>
      )}
      {message.error && (
        <div className="max-w-[80%] min-w-0 rounded-2xl bg-red-50 border border-red-200 text-red-800 p-3 text-sm font-medium">
          <p>
            <strong>Error:</strong> {message.error}
          </p>
        </div>
      )}
    </div>
  );
}

// Chart suggestion utility
function getChartSuggestion(data) {
  if (!data || data.length === 0) return null;

  const firstRow = data[0];
  const headers = Object.keys(firstRow);
  if (headers.length < 2) return null;

  const types = headers.map((h) => {
    const value = firstRow[h];
    if (typeof value === "number") return "number";
    if (typeof value === "string") {
      // Simple date check
      if (/\d{4}-\d{2}-\d{2}/.test(value)) return "date";
      return "string";
    }
    return "other";
  });

  const stringCount = types.filter((t) => t === "string").length;
  const numberCount = types.filter((t) => t === "number").length;
  const dateCount = types.filter((t) => t === "date").length;

  if (stringCount === 1 && numberCount >= 1) {
    return "Bar Chart";
  }
  if (dateCount === 1 && numberCount >= 1) {
    return "Line Chart";
  }
  if (numberCount >= 2) {
    return "Scatter Plot";
  }

  return null;
}

// Sub-component for the data table
function DataTable({ data }) {
  const headers = Object.keys(data[0]);

  function convertToCSV(jsonData) {
    const headers = Object.keys(jsonData[0]);
    const csvRows = [];
    // Add header row
    csvRows.push(headers.join(","));

    // Add data rows
    for (const row of jsonData) {
      const values = headers.map((header) => {
        const escaped = ("" + row[header]).replace(/"/g, '""'); // Escape double quotes
        return `"${escaped}"`;
      });
      csvRows.push(values.join(","));
    }
    return csvRows.join("\n");
  }

  function downloadCSV() {
    const csvString = convertToCSV(data);
    const blob = new Blob([csvString], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `query_result_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  return (
    <div className="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden">
      <div className="p-3 border-b border-slate-200 flex justify-between items-center">
        <p className="text-xs font-bold text-slate-600">
          Query Result ({data.length} rows)
        </p>
        <Button
          onClick={downloadCSV}
          variant="soft"
          className="px-3 py-1.5 text-xs"
        >
          Download as CSV
        </Button>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm text-left">
          <thead className="bg-slate-50 border-b border-slate-200 text-xs text-slate-600 uppercase">
            <tr>
              {headers.map((h) => (
                <th key={h} className="px-4 py-2 font-semibold">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {data.map((row, i) => (
              <tr key={i} className="hover:bg-slate-50">
                {headers.map((h) => (
                  <td
                    key={h}
                    className="px-4 py-2 text-slate-700 truncate max-w-xs"
                  >
                    {String(row[h])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// Sub-component for settings dropdown
function SettingSelect({ label, value, onChange, options }) {
  return (
    <div>
      <label className="text-xs font-bold text-slate-600">{label}</label>
      <select
        value={value}
        onChange={onChange}
        className="mt-1 w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-indigo-400"
      >
        {options.map((opt) => (
          <option key={opt} value={opt}>
            {opt}
          </option>
        ))}
        {options.length === 0 && <option disabled>Loading...</option>}
      </select>
    </div>
  );
}

// Sub-component for typing indicator
function TypingDots() {
  return (
    <div className="flex items-center gap-2">
      <span className="text-sm text-slate-600">Thinking</span>
      <span className="flex items-center gap-1.5">
        <span className="h-1.5 w-1.5 rounded-full bg-slate-400 animate-bounce [animation-delay:-0.3s]"></span>
        <span className="h-1.5 w-1.5 rounded-full bg-slate-400 animate-bounce [animation-delay:-0.15s]"></span>
        <span className="h-1.5 w-1.5 rounded-full bg-slate-400 animate-bounce"></span>
      </span>
    </div>
  );
}

// Sub-component for the Metrics Modal
function MetricsModal({ metrics, onClose }) {
  if (!metrics) return null;

  function downloadMetrics() {
    const jsonString = JSON.stringify(metrics, null, 2);
    const blob = new Blob([jsonString], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", "query_metrics_summary.json");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  return (
    <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-2xl max-h-[90vh] flex flex-col">
        <header className="p-4 border-b border-slate-200 flex justify-between items-center">
          <h3 className="font-bold text-lg text-slate-800">Query Metrics Summary</h3>
          <Button onClick={onClose} variant="ghost" className="px-3 py-1.5 !rounded-lg">
            Close
          </Button>
        </header>
        <main className="p-6 space-y-4 overflow-y-auto">
          <MetricsRow label="Total Queries" value={metrics.total_queries} />
          <MetricsRow label="Successful" value={metrics.successful} />
          <MetricsRow label="Failed" value={metrics.failed} />
          <MetricsRow label="Success Rate" value={`${(metrics.success_rate * 100).toFixed(1)}%`} />
          <hr />
          <MetricsRow label="Total Cost (USD)" value={`$${metrics.total_cost_usd.toFixed(6)}`} />
          <MetricsRow label="Total Tokens" value={metrics.total_tokens.input + metrics.total_tokens.output} />
          <MetricsRow label="Avg Latency" value={`${metrics.avg_latency_ms.toFixed(2)} ms`} />
          <hr />
          <MetricsRow label="Avg. Confidence" value={metrics.avg_confidence.toFixed(2)} />
          <MetricsRow label="Avg. Retries" value={metrics.avg_retries.toFixed(2)} />

        </main>
        <footer className="p-4 border-t border-slate-200 bg-slate-50">
           <Button onClick={downloadMetrics} variant="soft" className="w-full">
            Download Full Metrics (JSON)
          </Button>
        </footer>
      </div>
    </div>
  );
}

function MetricsRow({label, value}) {
  return (
    <div className="flex justify-between items-center text-sm">
      <p className="text-slate-600">{label}</p>
      <p className="font-bold text-slate-800 bg-slate-100 px-2 py-0.5 rounded-md">{value}</p>
    </div>
  )
}
