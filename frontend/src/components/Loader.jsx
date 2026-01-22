export function Loader({ text = "Working..." }) {
  return (
    <div className="flex items-center gap-3 text-sm text-gray-600">
      <span className="w-4 h-4 rounded-full border-2 border-gray-300 border-t-indigo-600 animate-spin"></span>
      {text}
    </div>
  );
}
