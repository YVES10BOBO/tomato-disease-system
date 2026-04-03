"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import DashboardLayout from "@/components/layout/DashboardLayout";
import CreateFarmPrompt from "@/components/CreateFarmPrompt";
import api from "@/lib/api";
import { useFarm } from "@/lib/useFarm";

const riskColor: Record<string, string> = {
  low: "bg-green-100 text-green-700 border-green-200",
  medium: "bg-yellow-100 text-yellow-700 border-yellow-200",
  high: "bg-orange-100 text-orange-700 border-orange-200",
  critical: "bg-red-100 text-red-700 border-red-200",
};

const riskDot: Record<string, string> = {
  low: "bg-green-500",
  medium: "bg-yellow-400",
  high: "bg-orange-500",
  critical: "bg-red-500",
};

const alertTypeIcon: Record<string, string> = {
  disease_detected: "🦠",
  high_risk: "🔥",
  critical: "🚨",
  sensor: "📡",
  default: "🔔",
};

export default function AlertsPage() {
  const router = useRouter();
  const { farmId, loading: farmLoading, noFarm, refetch } = useFarm();
  const [alerts, setAlerts] = useState<any[]>([]);
  const [summary, setSummary] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<"all" | "unread" | "read">("all");
  const [markingAll, setMarkingAll] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) { router.push("/login"); return; }
  }, []);

  useEffect(() => {
    if (farmId) fetchData(farmId);
    else if (!farmLoading) setLoading(false);
  }, [farmId, farmLoading]);

  const fetchData = async (id: string) => {
    try {
      const [alertRes, sumRes] = await Promise.all([
        api.get(`/alerts/?limit=100`),
        api.get(`/alerts/farm/${id}/summary`),
      ]);
      setAlerts(alertRes.data.alerts);
      setSummary(sumRes.data);
    } catch {
      router.push("/login");
    } finally {
      setLoading(false);
    }
  };

  const markRead = async (id: string) => {
    try {
      await api.put(`/alerts/${id}/read`);
      setAlerts(prev => prev.map(a => a.id === id ? { ...a, is_read: true } : a));
    } catch {}
  };

  const markAllRead = async () => {
    setMarkingAll(true);
    try {
      const unread = alerts.filter(a => !a.is_read);
      await Promise.all(unread.map(a => api.put(`/alerts/${a.id}/read`)));
      setAlerts(prev => prev.map(a => ({ ...a, is_read: true })));
    } catch {}
    setMarkingAll(false);
  };

  const filtered = alerts.filter(a => {
    if (filter === "unread") return !a.is_read;
    if (filter === "read") return a.is_read;
    return true;
  });

  const unreadCount = alerts.filter(a => !a.is_read).length;

  if (noFarm) return (
    <DashboardLayout title="Alerts">
      <CreateFarmPrompt onCreated={refetch} />
    </DashboardLayout>
  );

  if (farmLoading || loading) return (
    <DashboardLayout title="Alerts">
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-green-500 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
          <p className="text-gray-500">Loading alerts...</p>
        </div>
      </div>
    </DashboardLayout>
  );

  return (
    <DashboardLayout title="Alerts">
      {/* Summary Stats */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        {[
          { label: "Total Alerts", value: alerts.length, icon: "🔔", color: "text-blue-600", bg: "bg-blue-50" },
          { label: "Unread", value: unreadCount, icon: "📬", color: "text-orange-600", bg: "bg-orange-50" },
          { label: "Today", value: summary?.alerts_today ?? 0, icon: "📅", color: "text-purple-600", bg: "bg-purple-50" },
          { label: "Critical", value: alerts.filter(a => a.risk_level === "critical").length, icon: "🚨", color: "text-red-600", bg: "bg-red-50" },
        ].map((s) => (
          <div key={s.label} className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
            <div className={`w-12 h-12 ${s.bg} rounded-xl flex items-center justify-center text-2xl mb-3`}>{s.icon}</div>
            <p className="text-sm text-gray-500">{s.label}</p>
            <p className={`text-3xl font-bold ${s.color}`}>{s.value}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-3 gap-5">
        {/* Alert List */}
        <div className="col-span-2">
          {/* Controls */}
          <div className="flex items-center justify-between mb-4">
            <div className="bg-white rounded-2xl p-1.5 shadow-sm border border-gray-100 inline-flex gap-1">
              {(["all", "unread", "read"] as const).map((f) => (
                <button
                  key={f}
                  onClick={() => setFilter(f)}
                  className={`px-4 py-2 rounded-xl text-sm font-medium capitalize transition-all ${
                    filter === f ? "bg-green-600 text-white shadow-sm" : "text-gray-500 hover:bg-gray-100"
                  }`}
                >
                  {f}
                  {f === "unread" && unreadCount > 0 && (
                    <span className="ml-1.5 bg-orange-500 text-white text-xs rounded-full px-1.5">{unreadCount}</span>
                  )}
                </button>
              ))}
            </div>
            {unreadCount > 0 && (
              <button
                onClick={markAllRead}
                disabled={markingAll}
                className="text-sm text-green-600 hover:text-green-700 font-medium disabled:opacity-50 transition"
              >
                {markingAll ? "Marking..." : "Mark all as read"}
              </button>
            )}
          </div>

          {/* Alerts */}
          {filtered.length === 0 ? (
            <div className="bg-white rounded-2xl p-12 shadow-sm border border-gray-100 text-center">
              <span className="text-5xl">🎉</span>
              <p className="text-gray-500 mt-3 font-medium">
                {filter === "unread" ? "All caught up! No unread alerts." : "No alerts found."}
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {filtered.map((a: any) => (
                <div
                  key={a.id}
                  className={`bg-white rounded-2xl p-4 shadow-sm border transition-all ${
                    !a.is_read ? "border-orange-200 bg-orange-50/30" : "border-gray-100"
                  }`}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-start gap-3 flex-1">
                      {/* Unread dot */}
                      <div className="flex-shrink-0 mt-1">
                        {!a.is_read ? (
                          <span className="w-2.5 h-2.5 bg-orange-400 rounded-full inline-block"></span>
                        ) : (
                          <span className="w-2.5 h-2.5 bg-gray-200 rounded-full inline-block"></span>
                        )}
                      </div>

                      {/* Icon */}
                      <span className="text-2xl flex-shrink-0">
                        {alertTypeIcon[a.alert_type] || alertTypeIcon.default}
                      </span>

                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-0.5">
                          <p className={`font-semibold text-gray-800 ${!a.is_read ? "font-bold" : ""}`}>
                            {a.title}
                          </p>
                          <span className={`text-xs px-2 py-0.5 rounded-full border font-medium shrink-0 ${riskColor[a.risk_level] || "bg-gray-100 text-gray-600 border-gray-200"}`}>
                            <span className={`inline-block w-1.5 h-1.5 rounded-full mr-1 ${riskDot[a.risk_level] || "bg-gray-400"}`}></span>
                            {a.risk_level}
                          </span>
                        </div>
                        <p className="text-sm text-gray-600">{a.message}</p>
                        <p className="text-xs text-gray-400 mt-1.5">
                          {new Date(a.created_at).toLocaleDateString("en-RW", {
                            weekday: "short", day: "numeric", month: "short",
                            hour: "2-digit", minute: "2-digit"
                          })}
                        </p>
                      </div>
                    </div>

                    {/* Mark read button */}
                    {!a.is_read && (
                      <button
                        onClick={() => markRead(a.id)}
                        className="shrink-0 text-xs text-gray-400 hover:text-green-600 border border-gray-200 hover:border-green-300 px-2 py-1 rounded-lg transition"
                      >
                        Mark read
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Right Panel */}
        <div className="space-y-4">
          {/* Risk Level Breakdown */}
          <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
            <h3 className="font-semibold text-gray-700 mb-4 flex items-center gap-2">
              <span>📊</span> By Risk Level
            </h3>
            {["critical", "high", "medium", "low"].map((level) => {
              const count = alerts.filter(a => a.risk_level === level).length;
              const pct = alerts.length ? Math.round((count / alerts.length) * 100) : 0;
              return (
                <div key={level} className="mb-3">
                  <div className="flex justify-between text-sm mb-1">
                    <div className="flex items-center gap-1.5">
                      <span className={`w-2 h-2 rounded-full ${riskDot[level]}`}></span>
                      <span className="capitalize text-gray-600">{level}</span>
                    </div>
                    <span className="font-medium text-gray-800">{count}</span>
                  </div>
                  <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full ${
                        level === "critical" ? "bg-red-500" :
                        level === "high" ? "bg-orange-500" :
                        level === "medium" ? "bg-yellow-400" : "bg-green-500"
                      }`}
                      style={{ width: `${pct}%` }}
                    ></div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Alert Type Breakdown */}
          <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
            <h3 className="font-semibold text-gray-700 mb-4 flex items-center gap-2">
              <span>📋</span> By Type
            </h3>
            {(() => {
              const types: Record<string, number> = {};
              alerts.forEach(a => {
                types[a.alert_type || "other"] = (types[a.alert_type || "other"] || 0) + 1;
              });
              return Object.entries(types).length > 0 ? (
                <div className="space-y-2">
                  {Object.entries(types).map(([type, count]) => (
                    <div key={type} className="flex items-center justify-between text-sm">
                      <div className="flex items-center gap-2">
                        <span>{alertTypeIcon[type] || alertTypeIcon.default}</span>
                        <span className="text-gray-600 capitalize">{type.replace("_", " ")}</span>
                      </div>
                      <span className="bg-gray-100 text-gray-700 text-xs rounded-full px-2 py-0.5 font-medium">{count}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-gray-400 text-center py-2">No data</p>
              );
            })()}
          </div>

          {/* Farm Health Summary */}
          {summary && (
            <div className={`rounded-2xl p-5 shadow-sm border ${
              summary.overall_health === "HEALTHY" ? "bg-green-50 border-green-200" :
              summary.overall_health === "CRITICAL" ? "bg-red-50 border-red-200" :
              "bg-yellow-50 border-yellow-200"
            }`}>
              <h3 className="font-semibold mb-3 flex items-center gap-2 text-gray-700">
                <span>🌿</span> Farm Status
              </h3>
              <p className={`text-2xl font-bold ${
                summary.overall_health === "HEALTHY" ? "text-green-700" :
                summary.overall_health === "CRITICAL" ? "text-red-700" : "text-yellow-700"
              }`}>
                {summary.overall_health}
              </p>
              <div className="mt-3 space-y-1 text-sm">
                <div className="flex justify-between text-gray-600">
                  <span>Active diseases</span>
                  <span className="font-medium">{summary.active_diseases}</span>
                </div>
                <div className="flex justify-between text-gray-600">
                  <span>Alerts today</span>
                  <span className="font-medium">{summary.alerts_today}</span>
                </div>
                <div className="flex justify-between text-gray-600">
                  <span>Detections today</span>
                  <span className="font-medium">{summary.detections_today}</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
}
