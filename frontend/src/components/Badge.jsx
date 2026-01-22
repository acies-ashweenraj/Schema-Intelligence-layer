export function Badge({ children, color = "green" }) {
  const styles = {
    green: "bg-green-50 border-green-200 text-green-700",
    blue: "bg-blue-50 border-blue-200 text-blue-700",
    gray: "bg-gray-50 border-gray-200 text-gray-700",
    amber: "bg-amber-50 border-amber-200 text-amber-700",
  };

  return (
    <span className={`text-xs px-3 py-1 rounded-full border font-medium ${styles[color]}`}>
      {children}
    </span>
  );
}
