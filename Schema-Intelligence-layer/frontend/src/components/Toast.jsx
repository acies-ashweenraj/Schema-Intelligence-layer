export default function Toast({ text, type }) {
  if (!text) return null;

  return (
    <div style={{ ...styles.toast, ...(type === "error" ? styles.error : styles.ok) }}>
      {text}
    </div>
  );
}

const styles = {
  toast: {
    position: "fixed",
    bottom: 18,
    left: "50%",
    transform: "translateX(-50%)",
    padding: "10px 14px",
    borderRadius: 12,
    fontSize: 13,
    fontWeight: 600,
    boxShadow: "0 12px 28px rgba(0,0,0,0.12)",
    zIndex: 50,
  },
  ok: { background: "#ecfdf5", border: "1px solid #bbf7d0", color: "#065f46" },
  error: { background: "#fef2f2", border: "1px solid #fecaca", color: "#991b1b" },
};
