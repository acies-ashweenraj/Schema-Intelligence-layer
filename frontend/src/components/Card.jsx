export function Card({ title, desc, children, rightSlot }) {
  return (
    <div className="bg-white rounded-3xl shadow-sm border border-gray-100 p-6">
      {(title || desc || rightSlot) && (
        <div className="flex items-start justify-between gap-4 mb-5">
          <div>
            {title && <h3 className="text-lg font-semibold text-gray-900">{title}</h3>}
            {desc && <p className="text-sm text-gray-500 mt-1">{desc}</p>}
          </div>
          {rightSlot ? <div>{rightSlot}</div> : null}
        </div>
      )}
      {children}
    </div>
  );
}
