"use client";
import { useEffect, useState } from "react";

export default function TopBar({ title }: { title: string }) {
  const [user, setUser] = useState<{ full_name: string; role: string } | null>(null);
  const [time, setTime] = useState(new Date());

  useEffect(() => {
    const u = localStorage.getItem("user");
    if (u) setUser(JSON.parse(u));
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
      <h2 className="text-xl font-semibold text-gray-800">{title}</h2>
      <div className="flex items-center gap-6">
        <div className="text-sm text-gray-500">
          {time.toLocaleDateString("en-RW", { weekday: "long", year: "numeric", month: "long", day: "numeric" })}
          {" · "}
          <span className="font-mono">{time.toLocaleTimeString()}</span>
        </div>
        {user && (
          <div className="flex items-center gap-2">
            <div className="w-9 h-9 bg-green-600 rounded-full flex items-center justify-center text-white font-bold text-sm">
              {user.full_name.charAt(0).toUpperCase()}
            </div>
            <div>
              <p className="text-sm font-medium text-gray-800">{user.full_name}</p>
              <p className="text-xs text-gray-500 capitalize">{user.role}</p>
            </div>
          </div>
        )}
      </div>
    </header>
  );
}
