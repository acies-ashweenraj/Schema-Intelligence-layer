// import { useEffect, useRef, useState } from "react";
// import { askQuestion } from "../api/client";

// export default function ChatPage({ onExit }) {
//   const [question, setQuestion] = useState("");
//   const [loading, setLoading] = useState(false);

//   const [chats, setChats] = useState([
//     {
//       id: "chat-1",
//       title: "New Chat",
//       messages: [
//         {
//           role: "bot",
//           text: "Hi 👋 I’m your Data Assistant. Ask me anything about your data!",
//         },
//       ],
//     },
//   ]);

//   const [activeChatId, setActiveChatId] = useState("chat-1");
//   const activeChat = chats.find((c) => c.id === activeChatId);

//   const bottomRef = useRef(null);

//   useEffect(() => {
//     bottomRef.current?.scrollIntoView({ behavior: "smooth" });
//   }, [activeChat?.messages, loading]);

//   function newChat() {
//     const id = `chat-${Date.now()}`;
//     const newOne = {
//       id,
//       title: "New Chat",
//       messages: [
//         {
//           role: "bot",
//           text: "✨ New chat started. Ask your question!",
//         },
//       ],
//     };
//     setChats((prev) => [newOne, ...prev]);
//     setActiveChatId(id);
//   }

//   async function handleSend() {
//     if (!question.trim() || loading) return;

//     const q = question.trim();
//     setQuestion("");

//     setChats((prev) =>
//       prev.map((chat) =>
//         chat.id === activeChatId
//           ? {
//               ...chat,
//               title: chat.title === "New Chat" ? q.slice(0, 24) : chat.title,
//               messages: [...chat.messages, { role: "user", text: q }],
//             }
//           : chat
//       )
//     );

//     setLoading(true);

//     try {
//       const res = await askQuestion({ question: q }); // ✅ correct payload

//       setChats((prev) =>
//         prev.map((chat) =>
//           chat.id === activeChatId
//             ? {
//                 ...chat,
//                 messages: [
//                   ...chat.messages,
//                   { role: "bot", text: res.result || "No answer found." },
//                 ],
//               }
//             : chat
//         )
//       );
//     } catch (err) {
//       console.error(err);
//       setChats((prev) =>
//         prev.map((chat) =>
//           chat.id === activeChatId
//             ? {
//                 ...chat,
//                 messages: [
//                   ...chat.messages,
//                   {
//                     role: "bot",
//                     text: "❌ Error while fetching response from backend.",
//                   },
//                 ],
//               }
//             : chat
//         )
//       );
//     } finally {
//       setLoading(false);
//     }
//   }

//   return (
//     <div className="h-screen w-screen bg-gradient-to-br from-sky-50 via-white to-indigo-50">
//       <div className="h-full w-full grid grid-cols-1 lg:grid-cols-[320px_1fr]">
//         {/* SIDEBAR */}
//         <aside className="bg-white border-r border-gray-100 p-5 flex flex-col">
//           <div className="flex items-center justify-between">
//             <div>
//               <h2 className="text-lg font-semibold text-gray-900">
//                 KG Assistant
//               </h2>
//               <p className="text-xs text-gray-500">Chat History</p>
//             </div>

//             <span className="text-xs px-3 py-1 rounded-full bg-green-50 border border-green-200 text-green-700 font-medium">
//               Connected
//             </span>
//           </div>

//           <button
//             onClick={newChat}
//             className="w-full mt-4 rounded-2xl bg-indigo-600 text-white font-semibold py-3 hover:bg-indigo-700 transition"
//           >
//             + New Chat
//           </button>

//           <div className="mt-5 space-y-2 flex-1 overflow-y-auto pr-1">
//             {chats.map((c) => (
//               <button
//                 key={c.id}
//                 onClick={() => setActiveChatId(c.id)}
//                 className={`w-full text-left px-4 py-3 rounded-2xl border transition ${
//                   c.id === activeChatId
//                     ? "bg-indigo-50 border-indigo-200"
//                     : "bg-white border-gray-100 hover:bg-gray-50"
//                 }`}
//               >
//                 <p className="text-sm font-semibold text-gray-900 truncate">
//                   {c.title}
//                 </p>
//                 <p className="text-xs text-gray-500 truncate mt-1">
//                   {c.messages?.[c.messages.length - 1]?.text}
//                 </p>
//               </button>
//             ))}
//           </div>

//           {/* ✅ ONLY EXIT BUTTON */}
//           <button
//             onClick={onExit}
//             className="mt-4 w-full rounded-2xl bg-red-50 border border-red-200 text-red-700 font-semibold py-3 hover:bg-red-100 transition"
//           >
//             Exit
//           </button>
//         </aside>

//         {/* CHAT MAIN */}
//         <main className="flex flex-col h-full">
//           {/* TOP BAR */}
//           <div className="p-5 border-b bg-white">
//             <h3 className="text-lg font-semibold text-gray-900">
//               {activeChat?.title || "Chat"}
//             </h3>
//             <p className="text-sm text-gray-500">
//               Ask questions & get summary answers from your Knowledge Graph
//             </p>
//           </div>

//           {/* MESSAGES */}
//           <div className="flex-1 bg-gray-50 p-6 overflow-y-auto space-y-4">
//             {activeChat?.messages?.map((m, idx) => (
//               <MessageBubble key={idx} role={m.role} text={m.text} />
//             ))}

//             {loading && (
//               <div className="flex justify-start">
//                 <div className="bg-white border border-gray-100 rounded-2xl px-4 py-3 text-sm text-gray-500 shadow-sm">
//                   <TypingDots />
//                 </div>
//               </div>
//             )}

//             <div ref={bottomRef} />
//           </div>

//           {/* INPUT */}
//           <div className="p-5 bg-white border-t">
//             <div className="flex gap-3 items-center">
//               <input
//                 value={question}
//                 onChange={(e) => setQuestion(e.target.value)}
//                 onKeyDown={(e) => e.key === "Enter" && handleSend()}
//                 placeholder="Type your question... (Example: Recently joined top 3 employees)"
//                 className="flex-1 rounded-2xl border border-gray-200 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-400"
//               />
//               <button
//                 onClick={handleSend}
//                 disabled={loading}
//                 className="rounded-2xl bg-indigo-600 text-white px-6 py-3 font-semibold hover:bg-indigo-700 transition disabled:opacity-60"
//               >
//                 Send
//               </button>
//             </div>

//             <p className="text-xs text-gray-400 mt-3">
//               Tip: Try “Show top 5 employees with most incidents”
//             </p>
//           </div>
//         </main>
//       </div>
//     </div>
//   );
// }

// function MessageBubble({ role, text }) {
//   const isUser = role === "user";
//   return (
//     <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
//       <div
//         className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed shadow-sm ${
//           isUser
//             ? "bg-indigo-600 text-white"
//             : "bg-white text-gray-800 border border-gray-100"
//         }`}
//       >
//         {text}
//       </div>
//     </div>
//   );
// }

// function TypingDots() {
//   return (
//     <div className="flex items-center gap-2">
//       <span className="text-gray-500">Thinking</span>
//       <span className="flex gap-1">
//         <span className="w-2 h-2 bg-gray-300 rounded-full animate-bounce"></span>
//         <span className="w-2 h-2 bg-gray-300 rounded-full animate-bounce [animation-delay:120ms]"></span>
//         <span className="w-2 h-2 bg-gray-300 rounded-full animate-bounce [animation-delay:240ms]"></span>
//       </span>
//     </div>
//   );
// }
export default function Chat() {
  return (
    <div>
      <h1>Chat Page</h1>
    </div>
  );
}
