export default function ChatBubble({ role, text, time }) {
  const isUser = role === "user";

  return (
    <div style={{ display: "flex", justifyContent: isUser ? "flex-end" : "flex-start" }}>
      <div style={{ ...styles.bubble, ...(isUser ? styles.user : styles.bot) }}>
        <div style={styles.text}>{text}</div>
        <div style={styles.time}>{time}</div>
      </div>
    </div>
  );
}

const styles = {
  bubble: {
    maxWidth: "72%",
    padding: "12px 14px",
    borderRadius: 16,
    fontSize: 14,
    lineHeight: 1.45,
    boxShadow: "0 10px 22px rgba(0,0,0,0.06)",
  },
  user: {
    background: "linear-gradient(135deg,#2563eb,#1d4ed8)",
    color: "white",
    borderBottomRightRadius: 6,
  },
  bot: {
    background: "white",
    border: "1px solid #e5e7eb",
    color: "#111827",
    borderBottomLeftRadius: 6,
  },
  text: { whiteSpace: "pre-wrap" },
  time: {
    marginTop: 6,
    fontSize: 11,
    opacity: 0.7,
    textAlign: "right",
  },
};
