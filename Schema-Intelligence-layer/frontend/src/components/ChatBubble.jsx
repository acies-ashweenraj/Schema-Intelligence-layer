export default function ChatBubble({ role, text }) {
  const isUser = role === "user";

  // Base classes for all bubbles
  const baseClasses = "max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed shadow-sm";

  // Role-specific classes
  const userClasses = "bg-indigo-600 text-white rounded-br-lg";
  const botClasses = "bg-white text-gray-800 border border-gray-100 rounded-bl-lg";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div className={`${baseClasses} ${isUser ? userClasses : botClasses}`}>
        {/* Use pre-wrap to respect newlines in the text from the LLM */}
        <p className="whitespace-pre-wrap">{text}</p>
      </div>
    </div>
  );
}
