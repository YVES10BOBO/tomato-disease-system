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
  healthy: "bg-green-100 border-green-300 text-green-700",
  low: "bg-green-100 border-green-300 text-green-700",
  medium: "bg-yellow-100 border-yellow-300 text-yellow-700",
  high: "bg-orange-100 border-orange-300 text-orange-700",
  critical: "bg-red-100 border-red-300 text-red-700",
};

const severityDot: Record<string, string> = {
  healthy: "bg-green-500",
  low: "bg-green-500",
  medium: "bg-yellow-400",
  high: "bg-orange-500",
  critical: "bg-red-500",
};

export default function FarmsPage() {
  const router = useRouter();
  const { farmId, loading: farmLoading, noFarm, refetch } = useFarm();
  const [farm, setFarm] = useState<any>(null);
  const [zones, setZones] = useState<any[]>([]);
  const [activeZones, setActiveZones] = useState<any[]>([]);
  const [settings, setSettings] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [selectedZone, setSelectedZone] = useState<any>(null);
  const [editSettings, setEditSettings] = useState(false);
  const [settingsForm, setSettingsForm] = useState<any>(null);
  const [savingSettings, setSavingSettings] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) { router.push("/login"); return; }
  }, []);

  useEffect(() => {
    if (farmId) fetchFarm(farmId);
    else if (!farmLoading) setLoading(false);
  }, [farmId, farmLoading]);

  const fetchFarm = async (id: string) => {
    try {
      const [farmRes, activeRes, settingsRes] = await Promise.all([
        api.get(`/farms/${id}`),
        api.get(`/disease/${id}/active-zones`),
        api.get(`/farms/${id}/settings`),
      ]);
      setFarm(farmRes.data);
      setZones(farmRes.data.zones || []);
      setActiveZones(activeRes.data.active_zones || []);
      setSettings(settingsRes.data);
      setSettingsForm(settingsRes.data);
    } catch {
      router.push("/login");
    } finally {
      setLoading(false);
    }
  };

  const saveSettings = async () => {
    if (!farmId) return;
    setSavingSettings(true);
    try {
      await api.put(`/farms/${farmId}/settings`, {
        scan_interval_minutes: parseInt(settingsForm.scan_interval_minutes),
        alert_threshold: parseInt(settingsForm.alert_threshold),
        adaptive_scanning: settingsForm.adaptive_scanning,
        auto_alerts: settingsForm.auto_alerts,
      });
      setSettings(settingsForm);
      setEditSettings(false);
    } catch {}
    setSavingSettings(false);
  };

  const getZoneStatus = (code: string) => {
    const active = activeZones.find((z: any) => z.zone_code === code);
    if (active) return active.severity || "high";
    const zone = zones.find((z: any) => z.zone_code === code);
    return zone?.status === "active" ? "healthy" : "healthy";
  };

  const getZoneDisease = (code: string) => {
    const active = activeZones.find((z: any) => z.zone_code === code);
    return active?.disease_name || null;
  };

  if (noFarm) return (
    <DashboardLayout title="My Farm">
      <CreateFarmPrompt onCreated={refetch} />
    </DashboardLayout>
  );

  if (farmLoading || loading) return (
    <DashboardLayout title="My Farm">
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-green-500 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
          <p className="text-gray-500">Loading farm data...</p>
        </div>
      </div>
    </DashboardLayout>
  );

  return (
    <DashboardLayout title="My Farm">
      {/* Farm Header */}
      <div className="bg-gradient-to-r from-green-800 to-green-700 rounded-2xl p-6 mb-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-3 mb-1">
              <span className="text-3xl">🌿</span>
              <h2 className="text-2xl font-bold">{farm?.name || "Rutembeza Tomato Farm"}</h2>
            </div>
            <p className="text-green-200 text-sm">📍 {farm?.location || "Musanze, Rwanda"}</p>
            <div className="flex gap-4 mt-3">
              <div className="bg-green-700 rounded-xl px-4 py-2 text-center">
                <p className="text-2xl font-bold">{farm?.total_zones || 16}</p>
                <p className="text-green-200 text-xs">Total Zones</p>
              </div>
              <div className="bg-green-700 rounded-xl px-4 py-2 text-center">
                <p className="text-2xl font-bold text-red-300">{activeZones.length}</p>
                <p className="text-green-200 text-xs">Active Disease</p>
              </div>
              <div className="bg-green-700 rounded-xl px-4 py-2 text-center">
                <p className="text-2xl font-bold text-green-300">{(farm?.total_zones || 16) - activeZones.length}</p>
                <p className="text-green-200 text-xs">Healthy Zones</p>
              </div>
            </div>
          </div>
          <div className="text-right">
            <p className="text-green-200 text-sm mb-1">Farm Size</p>
            <p className="text-3xl font-bold">{farm?.size_hectares || "2.5"} ha</p>
            <p className="text-green-200 text-xs mt-1">4×4 Grid Layout</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-6">
        {/* Zone Grid */}
        <div className="col-span-2">
          <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-gray-700 flex items-center gap-2">
                <span>🗺️</span> Farm Zone Map
              </h3>
              <div className="flex gap-3 text-xs">
                {["healthy", "medium", "high", "critical"].map(s => (
                  <div key={s} className="flex items-center gap-1">
                    <span className={`w-2.5 h-2.5 rounded-full ${severityDot[s]}`}></span>
                    <span className="text-gray-500 capitalize">{s}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Column labels */}
            <div className="grid grid-cols-5 gap-2 mb-1">
              <div></div>
              {COLS.map(c => (
                <div key={c} className="text-center text-xs font-bold text-gray-400">Col {c}</div>
              ))}
            </div>

            {/* Grid rows */}
            {ROWS.map((row) => (
              <div key={row} className="grid grid-cols-5 gap-2 mb-2">
                <div className="flex items-center justify-center">
                  <span className="text-xs font-bold text-gray-400 bg-gray-100 rounded-lg w-8 h-8 flex items-center justify-center">
                    Row {row}
                  </span>
                </div>
                {COLS.map((col) => {
                  const code = `${row}${col}`;
                  const status = getZoneStatus(code);
                  const disease = getZoneDisease(code);
                  const isSelected = selectedZone?.code === code;
                  return (
                    <button
                      key={code}
                      onClick={() => setSelectedZone(
                        isSelected ? null : { code, status, disease }
                      )}
                      className={`
                        relative rounded-xl border-2 p-3 text-center transition-all duration-200 cursor-pointer
                        ${severityColor[status] || severityColor.healthy}
                        ${isSelected ? "ring-2 ring-offset-1 ring-gray-800 scale-105 shadow-lg" : "hover:scale-102 hover:shadow-md"}
                      `}
                    >
                      <div className={`absolute top-2 right-2 w-2.5 h-2.5 rounded-full ${severityDot[status] || severityDot.healthy}`}></div>
                      <p className="font-bold text-lg">{code}</p>
                      {disease && (
                        <p className="text-xs mt-0.5 line-clamp-1 opacity-80">{disease.split(" ")[0]}</p>
                      )}
                      {!disease && (
                        <p className="text-xs mt-0.5 opacity-60">Clear</p>
                      )}
                    </button>
                  );
                })}
              </div>
            ))}
          </div>
        </div>

        {/* Right Panel */}
        <div className="space-y-4">
          {/* Zone Detail */}
          {selectedZone ? (
            <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
              <h3 className="font-semibold text-gray-700 mb-3 flex items-center gap-2">
                <span>📍</span> Zone {selectedZone.code}
              </h3>
              <div className={`rounded-xl p-4 mb-3 ${severityColor[selectedZone.status] || severityColor.healthy}`}>
                <div className="flex items-center gap-2 mb-1">
                  <span className={`w-3 h-3 rounded-full ${severityDot[selectedZone.status] || severityDot.healthy}`}></span>
                  <span className="font-bold capitalize">{selectedZone.status} Status</span>
                </div>
                {selectedZone.disease ? (
                  <p className="text-sm mt-1">Disease: <strong>{selectedZone.disease}</strong></p>
                ) : (
                  <p className="text-sm mt-1">No disease detected</p>
                )}
              </div>
              <button
                onClick={() => setSelectedZone(null)}
                className="w-full text-xs text-gray-400 hover:text-gray-600 transition"
              >
                Deselect zone
              </button>
            </div>
          ) : (
            <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
              <h3 className="font-semibold text-gray-700 mb-3 flex items-center gap-2">
                <span>📍</span> Zone Details
              </h3>
              <p className="text-sm text-gray-400 text-center py-4">Click a zone on the map to see details</p>
            </div>
          )}

          {/* Farm Settings */}
          <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-semibold text-gray-700 flex items-center gap-2">
                <span>⚙️</span> Farm Settings
              </h3>
              {settings && !editSettings && (
                <button onClick={() => setEditSettings(true)} className="text-xs text-green-600 hover:text-green-700 font-medium border border-green-200 px-2 py-1 rounded-lg transition">
                  Edit
                </button>
              )}
            </div>
            {settings && settingsForm ? (
              <div className="space-y-3">
                <div>
                  <label className="text-xs text-gray-500">Scan Interval (minutes)</label>
                  {editSettings ? (
                    <input type="number" min="1" value={settingsForm.scan_interval_minutes}
                      onChange={(e) => setSettingsForm({ ...settingsForm, scan_interval_minutes: e.target.value })}
                      className="w-full mt-1 px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                    />
                  ) : (
                    <p className="font-medium text-gray-800 text-sm">{settings.scan_interval_minutes} min</p>
                  )}
                </div>
                <div>
                  <label className="text-xs text-gray-500">Alert Threshold (%)</label>
                  {editSettings ? (
                    <input type="number" min="1" max="100" value={settingsForm.alert_threshold}
                      onChange={(e) => setSettingsForm({ ...settingsForm, alert_threshold: e.target.value })}
                      className="w-full mt-1 px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                    />
                  ) : (
                    <p className="font-medium text-gray-800 text-sm">{settings.alert_threshold}%</p>
                  )}
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-gray-500">Adaptive Scanning</span>
                  {editSettings ? (
                    <button type="button" onClick={() => setSettingsForm({ ...settingsForm, adaptive_scanning: !settingsForm.adaptive_scanning })}
                      className={`w-10 h-5 rounded-full transition-colors ${settingsForm.adaptive_scanning ? "bg-green-500" : "bg-gray-300"}`}>
                      <span className={`block w-4 h-4 bg-white rounded-full shadow transition-transform mx-0.5 ${settingsForm.adaptive_scanning ? "translate-x-5" : ""}`}></span>
                    </button>
                  ) : (
                    <span className={`text-xs font-medium ${settings.adaptive_scanning ? "text-green-600" : "text-gray-400"}`}>
                      {settings.adaptive_scanning ? "Enabled" : "Disabled"}
                    </span>
                  )}
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-gray-500">Auto Alerts</span>
                  {editSettings ? (
                    <button type="button" onClick={() => setSettingsForm({ ...settingsForm, auto_alerts: !settingsForm.auto_alerts })}
                      className={`w-10 h-5 rounded-full transition-colors ${settingsForm.auto_alerts ? "bg-green-500" : "bg-gray-300"}`}>
                      <span className={`block w-4 h-4 bg-white rounded-full shadow transition-transform mx-0.5 ${settingsForm.auto_alerts ? "translate-x-5" : ""}`}></span>
                    </button>
                  ) : (
                    <span className={`text-xs font-medium ${settings.auto_alerts ? "text-green-600" : "text-gray-400"}`}>
                      {settings.auto_alerts ? "Enabled" : "Disabled"}
                    </span>
                  )}
                </div>
                {editSettings && (
                  <div className="flex gap-2 pt-1">
                    <button onClick={() => { setEditSettings(false); setSettingsForm(settings); }}
                      className="flex-1 border border-gray-300 text-gray-600 py-1.5 rounded-lg text-xs font-medium hover:bg-gray-50 transition">
                      Cancel
                    </button>
                    <button onClick={saveSettings} disabled={savingSettings}
                      className="flex-1 bg-green-600 hover:bg-green-700 text-white py-1.5 rounded-lg text-xs font-medium transition disabled:opacity-50">
                      {savingSettings ? "Saving..." : "Save"}
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <p className="text-sm text-gray-400 text-center py-2">No settings found</p>
            )}
          </div>

          {/* Active Disease Zones List */}
          <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
            <h3 className="font-semibold text-gray-700 mb-3 flex items-center gap-2">
              <span>🦠</span> Disease Alerts
            </h3>
            {activeZones.length === 0 ? (
              <div className="text-center py-4">
                <span className="text-3xl">✅</span>
                <p className="text-sm text-green-600 font-medium mt-2">All zones healthy</p>
              </div>
            ) : (
              <div className="space-y-2">
                {activeZones.map((z: any) => (
                  <div key={z.zone_code} className={`flex items-center justify-between p-2 rounded-lg border ${severityColor[z.severity] || severityColor.high}`}>
                    <div className="flex items-center gap-2">
                      <span className={`w-2 h-2 rounded-full ${severityDot[z.severity] || severityDot.high}`}></span>
                      <span className="font-bold text-sm">Zone {z.zone_code}</span>
                    </div>
                    <span className="text-xs line-clamp-1">{z.disease_name?.split(" ")[0]}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
