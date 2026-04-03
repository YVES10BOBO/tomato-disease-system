import Link from "next/link";

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-900 via-green-800 to-emerald-900">
      <div className="text-center">
        <span className="text-8xl">🍅</span>
        <h1 className="text-6xl font-bold text-white mt-4">404</h1>
        <p className="text-green-200 text-lg mt-2">Page not found</p>
        <p className="text-green-300 text-sm mt-1">This page doesn't exist in TomatoGuard</p>
        <Link href="/dashboard"
          className="inline-block mt-6 bg-green-500 hover:bg-green-400 text-white font-semibold px-6 py-3 rounded-xl transition">
          Back to Dashboard
        </Link>
      </div>
    </div>
  );
}
