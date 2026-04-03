"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import DashboardLayout from "@/components/layout/DashboardLayout";
import CreateFarmPrompt from "@/components/CreateFarmPrompt";
import api from "@/lib/api";
import { useFarm } from "@/lib/useFarm";
const ROWS = ["A", "B", "C", "D"];
const COLS = [1, 2, 3, 4];

const severityColor: Record<string, string> = {
  low: "bg-green-100 text-green-700",
  medium: "bg-yellow-100 text-yellow-700",
  high: "bg-orange-100 text-orange-700",
  critical: "bg-red-100 text-red-700",
};

const severityZone: Record<string, string> = {
  low: "bg-green-100 border-green-300",
  medium: "bg-yellow-100 border-yellow-300",
  high: "bg-orange-100 border-orange-300",
  critical: "bg-red-100 border-red-300",
};

const severityDot: Record<string, string> = {
  low: "bg-green-500",
  medium: "bg-yellow-400",
  high: "bg-orange-500",
  critical: "bg-red-500",
};

export default function DetectionsPage() {
  const router = useRouter();
  const { farmId, loading: farmLoading, noFarm, refetch } = useFarm();
  const [detections, setDetections] = useState<any[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [activeZones, setActiveZones] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<"all" | "active" | "resolved">("all");
  const [selectedDetection, setSelectedDetection] = useState<any>(null);

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
      const [detRes, statsRes, activeRes] = await Promise.all([
        api.get(`/disease/${id}/detections?limit=50`),
        api.get(`/disease/${id}/stats`),
        api.get(`/disease/${id}/active-zones`),
      ]);
      setDetections(detRes.data.detections);
      setStats(statsRes.data);
      setActiveZones(activeRes.data.active_zones || []);
    } catch {
      router.push("/login");
    } finally {
      setLoading(false);
    }
  };

  const filtered = detections.filter(d => {
    if (filter === "active") return d.status === "active";
    if (filter === "resolved") return d.status === "resolved";
    return true;
  });

  const getZoneSeverity = (code: string) => {
    return activeZones.find(z => z.zone_code === code)?.severity || null;
  };

  if (noFarm) return (
    <DashboardLayout title="Disease Detections">
      <CreateFarmPrompt onCreated={refetch} />
    </DashboardLayout>
  );

  if (farmLoading || loading) return (
    <DashboardLayout title="Detections">
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-green-500 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
          <p className="text-gray-500">Loading detections...</p>
        </div>
      </div>
    </DashboardLayout>
  );

  return (
    <DashboardLayout title="Disease Detections">
      {/* Stats Row */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        {[
          { label: "Total Detections", value: stats?.total_detections ?? 0, icon: "🔬", color: "text-purple-600", bg: "bg-purple-50" },
          { label: "Active Cases", value: stats?.active_detections ?? 0, icon: "🦠", color: "text-red-600", bg: "bg-red-50" },
          { label: "Resolved", value: stats?.resolved_detections ?? 0, icon: "✅", color: "text-green-600", bg: "bg-green-50" },
          { label: "Affected Zones", value: activeZones.length, icon: "🗺️", color: "text-orange-600", bg: "bg-orange-50" },
        ].map((s) => (
          <div key={s.label} className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
            <div className={`w-12 h-12 ${s.bg} rounded-xl flex items-center justify-center text-2xl mb-3`}>{s.icon}</div>
            <p className="text-sm text-gray-500">{s.label}</p>
            <p className={`text-3xl font-bold ${s.color}`}>{s.value}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-3 gap-5">
        {/* Detections List */}
        <div className="col-span-2 space-y-4">
          {/* Filter Tabs */}
          <div className="bg-white rounded-2xl p-1.5 shadow-sm border border-gray-100 inline-flex gap-1">
            {(["all", "active", "resolved"] as const).map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={`px-5 py-2 rounded-xl text-sm font-medium capitalize transition-all ${
                  filter === f ? "bg-green-600 text-white shadow-sm" : "text-gray-500 hover:bg-gray-100"
                }`}
              >
                {f} {f === "all" ? `(${detections.length})` : f === "active" ? `(${detections.filter(d => d.status === "active").length})` : `(${detections.filter(d => d.status === "resolved").length})`}
              </button>
            ))}
          </div>

          {/* Detections Cards */}
          <div className="space-y-3">
            {filtered.length === 0 ? (
              <div className="bg-white rounded-2xl p-12 shadow-sm border border-gray-100 text-center">
                <span className="text-4xl">🔬</span>
                <p className="text-gray-400 mt-3">No {filter !== "all" ? filter : ""} detections found</p>
              </div>
            ) : (
              filtered.map((d: any) => (
                <div
                  key={d.id}
                  onClick={() => setSelectedDetection(selectedDetection?.id === d.id ? null : d)}
                  className={`bg-white rounded-2xl p-4 shadow-sm border cursor-pointer transition-all hover:shadow-md ${
                    selectedDetection?.id === d.id ? "border-green-400 ring-1 ring-green-300" : "border-gray-100"
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-3">
                      <div className="w-11 h-11 bg-red-50 rounded-xl flex items-center justify-center text-xl shrink-0">
                        🦠
                      </div>
                      <div>
                        <p className="font-semibold text-gray-800">{d.disease_name}</p>
                        <p className="text-xs text-gray-500 mt-0.5">
                          Zone <span className="font-bold text-gray-700">{d.zone_code}</span> · {d.confidence_score}% confidence
                        </p>
                        <p className="text-xs text-gray-400 mt-0.5">
                          {new Date(d.detected_at).toLocaleDateString("en-RW", { day: "numeric", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit" })}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 shrink-0">
                      <span className={`text-xs px-2 py-1 rounded-full font-medium ${severityColor[d.severity] || "bg-gray-100 text-gray-600"}`}>
                        {d.severity}
                      </span>
                      <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                        d.status === "active" ? "bg-red-100 text-red-600" : "bg-green-100 text-green-600"
                      }`}>
                        {d.status}
                      </span>
                    </div>
                  </div>

                  {/* Confidence Bar */}
                  <div className="mt-3">
                    <div className="flex justify-between text-xs text-gray-400 mb-1">
                      <span>AI Confidence</span>
                      <span>{d.confidence_score}%</span>
                    </div>
                    <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full ${d.confidence_score >= 90 ? "bg-red-500" : d.confidence_score >= 70 ? "bg-orange-400" : "bg-yellow-400"}`}
                        style={{ width: `${d.confidence_score}%` }}
                      ></div>
                    </div>
                  </div>

                  {/* Detail Panel (expanded) */}
                  {selectedDetection?.id === d.id && (
                    <div className="mt-4 pt-4 border-t border-gray-100">
                      <div className="grid grid-cols-2 gap-3">
                        <div className="bg-gray-50 rounded-xl p-3">
                          <p className="text-xs text-gray-400 mb-0.5">Treatment</p>
                          <p className="text-sm text-gray-700">{d.treatment_applied || "No treatment recorded"}</p>
                        </div>
                        <div className="bg-gray-50 rounded-xl p-3">
                          <p className="text-xs text-gray-400 mb-0.5">Notes</p>
                          <p className="text-sm text-gray-700">{d.notes || "—"}</p>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>

        {/* Right: Zone Map + Disease Summary */}
        <div className="space-y-4">
          {/* Mini Zone Map */}
          <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
            <h3 className="font-semibold text-gray-700 mb-3 flex items-center gap-2">
              <span>🗺️</span> Affected Zones
            </h3>
            <div className="space-y-1.5">
              {ROWS.map((row) => (
                <div key={row} className="flex gap-1.5">
                  {COLS.map((col) => {
                    const code = `${row}${col}`;
                    const sev = getZoneSeverity(code);
                    return (
                      <div
                        key={code}
                        className={`flex-1 rounded-lg border-2 p-1.5 text-center transition-all ${
                          sev ? severityZone[sev] : "bg-gray-50 border-gray-200"
                        }`}
                      >
                        <p className={`text-xs font-bold ${sev ? "" : "text-gray-400"}`}>{code}</p>
                        {sev && <span className={`inline-block w-1.5 h-1.5 rounded-full mt-0.5 ${severityDot[sev]}`}></span>}
                      </div>
                    );
                  })}
                </div>
              ))}
            </div>
            <div className="flex flex-wrap gap-2 mt-3">
              {["low", "medium", "high", "critical"].map(s => (
                <div key={s} className="flex items-center gap-1 text-xs text-gray-500">
                  <span className={`w-2 h-2 rounded-full ${severityDot[s]}`}></span>
                  <span className="capitalize">{s}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Disease Breakdown */}
          <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
            <h3 className="font-semibold text-gray-700 mb-3 flex items-center gap-2">
              <span>📊</span> Disease Breakdown
            </h3>
            {stats?.disease_breakdown && Object.keys(stats.disease_breakdown).length > 0 ? (
              <div className="space-y-2">
                {Object.entries(stats.disease_breakdown).map(([name, count]: any) => {
                  const pct = Math.round((count / (stats.total_detections || 1)) * 100);
                  return (
                    <div key={name}>
                      <div className="flex justify-between text-xs text-gray-600 mb-1">
                        <span className="truncate">{name}</span>
                        <span className="ml-2 font-medium">{count}</span>
                      </div>
                      <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-red-400 to-orange-400 rounded-full"
                          style={{ width: `${pct}%` }}
                        ></div>
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <p className="text-sm text-gray-400 text-center py-4">No data available</p>
            )}
          </div>

          {/* Active Zones List */}
          {activeZones.length > 0 && (
            <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
              <h3 className="font-semibold text-gray-700 mb-3 flex items-center gap-2">
                <span>🚨</span> Active Zones ({activeZones.length})
              </h3>
              <div className="space-y-2">
                {activeZones.map((z: any) => (
                  <div key={z.zone_code} className={`flex items-center justify-between p-2 rounded-lg ${severityColor[z.severity] || "bg-gray-50 text-gray-600"}`}>
                    <div className="flex items-center gap-2">
                      <span className={`w-2 h-2 rounded-full ${severityDot[z.severity] || "bg-gray-400"}`}></span>
                      <span className="font-bold text-sm">Zone {z.zone_code}</span>
                    </div>
                    <span className="text-xs">{z.disease_name?.split(" ").slice(0, 2).join(" ")}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
}
