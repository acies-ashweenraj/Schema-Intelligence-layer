export function Input({ label, hint, ...props }) {
  return (
    <div>
      {label && <label className="text-sm font-medium text-gray-700">{label}</label>}
      <input
        {...props}
        className="mt-1 w-full rounded-2xl border border-gray-200 px-4 py-3 outline-none focus:ring-2 focus:ring-indigo-400"
      />
      {hint && <p className="text-xs text-gray-400 mt-1">{hint}</p>}
    </div>
  );
}
