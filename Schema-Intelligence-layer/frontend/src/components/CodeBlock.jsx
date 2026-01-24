export function CodeBlock({ value }) {
  return (
    <pre className="rounded-2xl bg-gray-50 border border-gray-100 p-4 text-xs overflow-auto max-h-[360px]">
      {typeof value === "string" ? value : JSON.stringify(value, null, 2)}
    </pre>
  );
}
