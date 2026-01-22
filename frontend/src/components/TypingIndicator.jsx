export default function TypingIndicator() {
  return (
    <div style={styles.wrap}>
      <div style={styles.dot} />
      <div style={styles.dot} />
      <div style={styles.dot} />
    </div>
  );
}

const styles = {
  wrap: {
    display: "flex",
    gap: 6,
    padding: "10px 14px",
    borderRadius: 16,
    border: "1px solid #e5e7eb",
    background: "#fff",
    width: "fit-content",
    boxShadow: "0 10px 22px rgba(0,0,0,0.06)",
  },
  dot: {
    width: 7,
    height: 7,
    borderRadius: 999,
    background: "#9ca3af",
    animation: "pulse 1s infinite ease-in-out",
  },
};
