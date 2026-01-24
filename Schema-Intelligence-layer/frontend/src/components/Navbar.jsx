import { Database, MessageSquareText } from "lucide-react";

export default function Navbar({ title, subtitle }) {
  return (
    <div style={styles.nav}>
      <div style={styles.left}>
        <div style={styles.iconWrap}>
          <MessageSquareText size={18} />
        </div>
        <div>
          <div style={styles.title}>{title}</div>
          <div style={styles.sub}>{subtitle}</div>
        </div>
      </div>

      <div style={styles.badge}>
        <Database size={14} />
        Connected
      </div>
    </div>
  );
}

const styles = {
  nav: {
    height: 64,
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    padding: "0 18px",
    borderBottom: "1px solid #e5e7eb",
    background: "rgba(255,255,255,0.9)",
    backdropFilter: "blur(10px)",
    position: "sticky",
    top: 0,
    zIndex: 10,
  },
  left: { display: "flex", gap: 12, alignItems: "center" },
  iconWrap: {
    width: 38,
    height: 38,
    borderRadius: 12,
    display: "grid",
    placeItems: "center",
    background: "linear-gradient(135deg,#eff6ff,#eef2ff)",
    border: "1px solid #e5e7eb",
  },
  title: { fontWeight: 800, fontSize: 14, color: "#111827" },
  sub: { fontSize: 12, color: "#6b7280" },
  badge: {
    display: "flex",
    gap: 6,
    alignItems: "center",
    padding: "8px 10px",
    borderRadius: 999,
    border: "1px solid #e5e7eb",
    background: "#f8fafc",
    fontSize: 12,
    fontWeight: 600,
    color: "#111827",
  },
};
