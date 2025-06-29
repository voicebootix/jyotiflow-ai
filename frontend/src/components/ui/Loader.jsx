// தமில - Loader spiritual animation
export default function Loader({ message }) {
  return (
    <div className="flex flex-col items-center justify-center py-16">
      <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-purple-700 flex items-center justify-center">
        <span className="text-4xl">🕉️</span>
      </div>
      <div className="mt-4 text-purple-700 font-bold">{message}</div>
    </div>
  );
} 