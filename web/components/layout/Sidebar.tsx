"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import clsx from "clsx";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: "📊" },
  { href: "/farms", label: "My Farm", icon: "🌿" },
  { href: "/sensors", label: "IoT Sensors", icon: "📡" },
  { href: "/detections", label: "Detections", icon: "🔬" },
  { href: "/alerts", label: "Alerts", icon: "🔔" },
  { href: "/profile", label: "My Profile", icon: "👤" },
];

export default function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const [userRole, setUserRole] = useState<string>("");
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    const user = JSON.parse(localStorage.getItem("user") || "{}");
    setUserRole(user?.role || "");
    fetchUnreadCount();
    const interval = setInterval(fetchUnreadCount, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchUnreadCount = async () => {
    try {
      const res = await fetch("http://localhost:8002/alerts/?limit=100", {
        headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
      });
      if (!res.ok) return;
      const data = await res.json();
      const unread = (data.alerts || []).filter((a: any) => !a.is_read).length;
      setUnreadCount(unread);
    } catch {}
  };

  const handleLogout = () => {
    if (!confirm("Are you sure you want to sign out?")) return;
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    router.push("/login");
  };

  return (
    <aside className="w-64 bg-green-900 min-h-screen flex flex-col fixed left-0 top-0">
      {/* Logo */}
      <div className="flex items-center gap-3 px-6 py-5 border-b border-green-800">
        <span className="text-3xl">🍅</span>
        <div>
          <h1 className="text-white font-bold text-lg leading-tight">TomatoGuard</h1>
          <p className="text-green-400 text-xs">Disease Detection</p>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-4 py-6 space-y-1">
        {navItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={clsx(
              "flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200",
              pathname === item.href
                ? "bg-green-600 text-white shadow-md"
                : "text-green-200 hover:bg-green-800 hover:text-white"
            )}
          >
            <span className="text-lg">{item.icon}</span>
            <span className="flex-1">{item.label}</span>
            {item.href === "/alerts" && unreadCount > 0 && (
              <span className="bg-red-500 text-white text-xs font-bold rounded-full px-1.5 py-0.5 min-w-[20px] text-center">
                {unreadCount > 99 ? "99+" : unreadCount}
              </span>
            )}
          </Link>
        ))}
      </nav>

      {/* Admin Panel Link — only visible to admins */}
      {userRole === "admin" && (
        <div className="px-4 pb-2">
          <Link
            href="/admin"
            className={clsx(
              "flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200",
              pathname === "/admin"
                ? "bg-purple-600 text-white shadow-md"
                : "text-purple-300 hover:bg-purple-900 hover:text-white border border-purple-800"
            )}
          >
            <span className="text-lg">⚙️</span>
            Admin Panel
          </Link>
        </div>
      )}

      {/* User & Logout */}
      <div className="px-4 py-4 border-t border-green-800">
        <button
          onClick={handleLogout}
          className="flex items-center gap-3 px-4 py-3 w-full rounded-xl text-green-200 hover:bg-green-800 hover:text-white text-sm font-medium transition-all"
        >
          <span className="text-lg">🚪</span>
          Sign Out
        </button>
      </div>
    </aside>
  );
}
