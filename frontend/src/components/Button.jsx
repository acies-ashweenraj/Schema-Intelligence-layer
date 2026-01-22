export function Button({ variant = "primary", className = "", ...props }) {
  const base =
    "rounded-2xl px-5 py-3 font-semibold transition disabled:opacity-60 disabled:cursor-not-allowed";

  const styles = {
    primary: "bg-indigo-600 text-white hover:bg-indigo-700",
    soft: "bg-indigo-50 text-indigo-700 border border-indigo-200 hover:bg-indigo-100",
    danger: "bg-red-50 text-red-700 border border-red-200 hover:bg-red-100",
    ghost: "bg-white text-gray-700 border border-gray-200 hover:bg-gray-50",
  };

  return <button {...props} className={`${base} ${styles[variant]} ${className}`} />;
}
