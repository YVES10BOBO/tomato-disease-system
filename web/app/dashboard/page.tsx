"use client";
import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import DashboardLayout from "@/components/layout/DashboardLayout";
import CreateFarmPrompt from "@/components/CreateFarmPrompt";
import api from "@/lib/api";
import { useFarm } from "@/lib/useFarm";
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend,
} from "recharts";

// ─── CONSTANTS ───────────────────────────────────────────────
const RISK_COLOR: Record<string, string> = {
  low:      "bg-green-100 text-green-700 border-green-200",
  medium:   "bg-yellow-100 text-yellow-700 border-yellow-200",
  high:     "bg-orange-100 text-orange-700 border-orange-200",
  critical: "bg-red-100 text-red-700 border-red-200",
};
const RISK_DOT: Record<string, string> = {
  low: "bg-green-500", medium: "bg-yellow-500",
  high: "bg-orange-500", critical: "bg-red-500",
};
const HEALTH_STYLE: Record<string, string> = {
  HEALTHY:         "text-green-700 bg-green-50 border-green-200",
  "MODERATE RISK": "text-yellow-700 bg-yellow-50 border-yellow-200",
  "HIGH RISK":     "text-orange-700 bg-orange-50 border-orange-200",
  CRITICAL:        "text-red-700 bg-red-50 border-red-200",
};
const HEALTH_ICON: Record<string, string> = {
  HEALTHY: "✅", "MODERATE RISK": "⚠️", "HIGH RISK": "🔥", CRITICAL: "🚨",
};

// Disease risk thresholds — mirrors backend risk.py exactly
const DISEASE_GUIDE = [
  { disease: "Late Blight",       condition: "Temp 10–25°C  +  Humidity ≥ 90%",  level: "critical", icon: "🔴" },
  { disease: "Early Blight",      condition: "Temp 24–29°C  +  Humidity ≥ 80%",  level: "high",     icon: "🟠" },
  { disease: "Bacterial Spot",    condition: "Temp 24–30°C  +  Humidity ≥ 80%",  level: "high",     icon: "🟠" },
  { disease: "Septoria Leaf Spot",condition: "Temp 20–25°C  +  Humidity ≥ 70%",  level: "medium",   icon: "🟡" },
  { disease: "Leaf Curl Virus",   condition: "Temp > 30°C   +  Humidity < 50%",  level: "medium",   icon: "🟡" },
];

export default function DashboardPage() {
  const router = useRouter();
  const { farmId, farm, loading: farmLoading, noFarm, refetch } = useFarm();

  const [summary,       setSummary]       = useState<any>(null);
  const [latestSensor,  setLatestSensor]  = useState<any>(null);
  const [alerts,        setAlerts]        = useState<any[]>([]);
  const [detections,    setDetections]    = useState<any[]>([]);
  const [sensorHistory, setSensorHistory] = useState<any[]>([]);
  const [loading,       setLoading]       = useState(true);
  const [lastUpdated,   setLastUpdated]   = useState<Date | null>(null);
  const [iotOnline,     setIotOnline]     = useState(false);
  const [refreshing,    setRefreshing]    = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) { router.push("/login"); return; }
  }, []);

  useEffect(() => {
    if (farmId) fetchAll(farmId);
    else if (!farmLoading) setLoading(false);
  }, [farmId, farmLoading]);

  // Auto-refresh every 30 seconds — matches ESP32 send interval
  useEffect(() => {
    if (!farmId) return;
    const interval = setInterval(() => fetchLatestOnly(farmId), 30000);
    return () => clearInterval(interval);
  }, [farmId]);

  const fetchAll = useCallback(async (id: string) => {
    try {
      const [sumRes, sensorRes, alertRes, detRes, histRes] = await Promise.all([
        api.get(`/alerts/farm/${id}/summary`),
        api.get(`/iot/sensors/${id}/latest`),
        api.get(`/alerts/?limit=5`),
        api.get(`/disease/${id}/detections?limit=5`),
        api.get(`/iot/sensors/${id}/history?limit=24`),
      ]);
      setSummary(sumRes.data);
      setLatestSensor(sensorRes.data);
      setAlerts(alertRes.data.alerts || []);
      setDetections(detRes.data.detections || []);
      processSensorHistory(histRes.data.readings);
      setLastUpdated(new Date());
      checkIotStatus(sensorRes.data);
    } catch { router.push("/login"); }
    finally { setLoading(false); setRefreshing(false); }
  }, []);

  // Lightweight refresh — only latest sensor + summary
  const fetchLatestOnly = async (id: string) => {
    try {
      const [sensorRes, sumRes] = await Promise.all([
        api.get(`/iot/sensors/${id}/latest`),
        api.get(`/alerts/farm/${id}/summary`),
      ]);
      setLatestSensor(sensorRes.data);
      setSummary(sumRes.data);
      setLastUpdated(new Date());
      checkIotStatus(sensorRes.data);
    } catch {}
  };

  const processSensorHistory = (readings: any[]) => {
    const mapped = [...readings].reverse().map((r: any, i: number) => ({
      time: new Date(r.recorded_at).toLocaleTimeString("en-RW", { hour: "2-digit", minute: "2-digit" }),
      temp: r.temperature,
      humidity: r.humidity,
      soil: r.soil_moisture,
    }));
    setSensorHistory(mapped);
  };

  // IoT online = last reading was within 2 minutes
  const checkIotStatus = (sensor: any) => {
    if (!sensor?.recorded_at) { setIotOnline(false); return; }
    const diff = (Date.now() - new Date(sensor.recorded_at).getTime()) / 1000 / 60;
    setIotOnline(diff <= 2);
  };

  const handleRefresh = () => {
    if (!farmId) return;
    setRefreshing(true);
    fetchAll(farmId);
  };

  // ─── LOADING ───────────────────────────────────────────────
  if (farmLoading || loading) return (
    <DashboardLayout title="Dashboard">
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-green-500 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
          <p className="text-gray-500">Loading farm data...</p>
        </div>
      </div>
    </DashboardLayout>
  );

  if (noFarm) return (
    <DashboardLayout title="Dashboard">
      <CreateFarmPrompt onCreated={refetch} />
    </DashboardLayout>
  );

  const health = summary?.overall_health || "HEALTHY";

  return (
    <DashboardLayout title="Dashboard">

      {/* ── TOP BAR: Status + Refresh ─────────────────────── */}
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-3">
          {/* IoT Connection Status */}
          <div className={`flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs font-medium border ${
            iotOnline ? "bg-green-50 border-green-200 text-green-700" : "bg-gray-50 border-gray-200 text-gray-500"
          }`}>
            <span className={`w-2 h-2 rounded-full ${iotOnline ? "bg-green-500 animate-pulse" : "bg-gray-400"}`}></span>
            ESP32 {iotOnline ? "Online" : "Offline"}
          </div>
          {/* Last Updated */}
          {lastUpdated && (
            <span className="text-xs text-gray-400">
              Updated {lastUpdated.toLocaleTimeString("en-RW", { hour: "2-digit", minute: "2-digit", second: "2-digit" })}
            </span>
          )}
          <span className="text-xs text-gray-300">· Auto-refreshes every 30s</span>
        </div>

        <button
          onClick={handleRefresh}
          disabled={refreshing}
          className="flex items-center gap-2 text-sm text-gray-500 hover:text-green-600 border border-gray-200 hover:border-green-300 px-3 py-1.5 rounded-xl transition disabled:opacity-50"
        >
          <span className={refreshing ? "animate-spin" : ""}>🔄</span>
          {refreshing ? "Refreshing..." : "Refresh"}
        </button>
      </div>

      {/* ── FARM HEALTH BANNER ────────────────────────────── */}
      <div className={`border rounded-2xl p-5 mb-6 flex items-center justify-between ${HEALTH_STYLE[health] || HEALTH_STYLE["HEALTHY"]}`}>
        <div>
          <p className="text-sm font-medium opacity-70">Overall Farm Health</p>
          <h2 className="text-3xl font-bold">{health}</h2>
          <p className="text-sm opacity-70 mt-1">
            🌿 {farm?.name} &nbsp;·&nbsp; 📍 {farm?.location}
          </p>
          {health !== "HEALTHY" && (
            <p className="text-xs mt-2 opacity-80 font-medium">
              ⚠️ Disease-favorable conditions detected — check sensors and alerts
            </p>
          )}
        </div>
        <div className="text-right">
          <span className="text-6xl">{HEALTH_ICON[health] || "✅"}</span>
          <p className="text-xs opacity-60 mt-1">{farm?.size_hectares ?? "—"} ha · {farm?.total_zones ?? 16} zones</p>
        </div>
      </div>

      {/* ── STATS CARDS ───────────────────────────────────── */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        {[
          { label: "Active Diseases",  value: summary?.active_diseases ?? 0,   icon: "🦠", color: "text-red-600",    bg: "bg-red-50"    },
          { label: "Alerts Today",     value: summary?.alerts_today ?? 0,       icon: "🔔", color: "text-orange-600", bg: "bg-orange-50" },
          { label: "Zones Scanned",    value: summary?.scans_today ?? 0,        icon: "📷", color: "text-blue-600",   bg: "bg-blue-50"   },
          { label: "Detections Today", value: summary?.detections_today ?? 0,   icon: "🔬", color: "text-purple-600", bg: "bg-purple-50" },
        ].map((s) => (
          <div key={s.label} className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100 hover:shadow-md transition">
            <div className={`w-12 h-12 ${s.bg} rounded-xl flex items-center justify-center text-2xl mb-3`}>
              {s.icon}
            </div>
            <p className="text-sm text-gray-500">{s.label}</p>
            <p className={`text-3xl font-bold ${s.color}`}>{s.value}</p>
          </div>
        ))}
      </div>

      {/* ── SENSOR READINGS + CHART ───────────────────────── */}
      <div className="grid grid-cols-3 gap-4 mb-6">

        {/* Live Sensor Readings */}
        <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
          <h3 className="font-semibold text-gray-700 mb-4 flex items-center gap-2">
            <span>📡</span> Live Sensor Readings
          </h3>

          {latestSensor ? (
            <div className="space-y-3">
              {/* Temperature */}
              <div className="bg-orange-50 rounded-xl p-3">
                <div className="flex items-center justify-between mb-1">
                  <div className="flex items-center gap-2">
                    <span>🌡️</span>
                    <span className="text-sm text-gray-600">Temperature</span>
                  </div>
                  <span className="text-xl font-bold text-orange-600">{latestSensor.temperature}°C</span>
                </div>
                <div className="h-1.5 bg-orange-100 rounded-full">
                  <div className="h-full bg-orange-400 rounded-full transition-all" style={{ width: `${Math.min((latestSensor.temperature / 40) * 100, 100)}%` }}></div>
                </div>
                <p className="text-xs text-gray-400 mt-1">Normal: 18–30°C</p>
              </div>

              {/* Humidity */}
              <div className="bg-blue-50 rounded-xl p-3">
                <div className="flex items-center justify-between mb-1">
                  <div className="flex items-center gap-2">
                    <span>💧</span>
                    <span className="text-sm text-gray-600">Humidity</span>
                  </div>
                  <span className="text-xl font-bold text-blue-600">{latestSensor.humidity}%</span>
                </div>
                <div className="h-1.5 bg-blue-100 rounded-full">
                  <div className="h-full bg-blue-400 rounded-full transition-all" style={{ width: `${latestSensor.humidity}%` }}></div>
                </div>
                <p className="text-xs text-gray-400 mt-1">Normal: 60–80%</p>
              </div>

              {/* Soil Moisture */}
              <div className="bg-green-50 rounded-xl p-3">
                <div className="flex items-center justify-between mb-1">
                  <div className="flex items-center gap-2">
                    <span>🌱</span>
                    <span className="text-sm text-gray-600">Soil Moisture</span>
                  </div>
                  <span className="text-xl font-bold text-green-600">{latestSensor.soil_moisture}%</span>
                </div>
                <div className="h-1.5 bg-green-100 rounded-full">
                  <div className="h-full bg-green-400 rounded-full transition-all" style={{ width: `${latestSensor.soil_moisture}%` }}></div>
                </div>
                <p className="text-xs text-gray-400 mt-1">Normal: 40–70%</p>
              </div>

              {/* Risk Badge */}
              <div className={`flex items-center gap-2 px-3 py-2 rounded-xl border text-sm font-semibold ${RISK_COLOR[latestSensor.risk_level] || RISK_COLOR.low}`}>
                <span className={`w-2.5 h-2.5 rounded-full ${RISK_DOT[latestSensor.risk_level] || RISK_DOT.low}`}></span>
                {latestSensor.risk_level?.toUpperCase()} RISK
                <span className="ml-auto text-xs font-normal opacity-60">
                  {new Date(latestSensor.recorded_at).toLocaleTimeString("en-RW", { hour: "2-digit", minute: "2-digit" })}
                </span>
              </div>
            </div>
          ) : (
            <div className="text-center py-8">
              <p className="text-4xl mb-2">📡</p>
              <p className="text-gray-400 text-sm">No sensor readings yet</p>
              <p className="text-gray-300 text-xs mt-1">Start ESP32 / IoT simulator</p>
            </div>
          )}
        </div>

        {/* Sensor History Chart */}
        <div className="col-span-2 bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
          <h3 className="font-semibold text-gray-700 mb-4 flex items-center gap-2">
            <span>📈</span> Sensor Trends (Last 24 readings)
          </h3>
          {sensorHistory.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <AreaChart data={sensorHistory}>
                <defs>
                  <linearGradient id="gTemp" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#f97316" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#f97316" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="gHum" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="gSoil" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#22c55e" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="time" tick={{ fontSize: 10 }} interval={4} />
                <YAxis tick={{ fontSize: 10 }} />
                <Tooltip />
                <Legend />
                <Area type="monotone" dataKey="temp"     stroke="#f97316" fill="url(#gTemp)"  name="Temp °C"     strokeWidth={2} dot={false} />
                <Area type="monotone" dataKey="humidity" stroke="#3b82f6" fill="url(#gHum)"   name="Humidity %"  strokeWidth={2} dot={false} />
                <Area type="monotone" dataKey="soil"     stroke="#22c55e" fill="url(#gSoil)"  name="Soil %"      strokeWidth={2} dot={false} />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-48 text-gray-300">
              <p className="text-sm">No sensor history yet</p>
            </div>
          )}
        </div>
      </div>

      {/* ── ALERTS + DETECTIONS + DISEASE GUIDE ──────────── */}
      <div className="grid grid-cols-3 gap-4">

        {/* Recent Alerts */}
        <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-gray-700 flex items-center gap-2">
              <span>🔔</span> Recent Alerts
            </h3>
            <a href="/alerts" className="text-xs text-green-600 hover:text-green-700 font-medium">View all →</a>
          </div>
          {alerts.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-3xl mb-2">🎉</p>
              <p className="text-gray-400 text-sm">No alerts — farm is safe</p>
            </div>
          ) : (
            <div className="space-y-2">
              {alerts.map((a: any) => (
                <div key={a.id} className={`p-3 rounded-xl border ${a.is_read ? "bg-gray-50 border-gray-100" : "bg-orange-50 border-orange-200"}`}>
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-1.5 mb-0.5">
                        {!a.is_read && <span className="w-2 h-2 bg-orange-400 rounded-full shrink-0"></span>}
                        <p className={`text-sm text-gray-800 line-clamp-1 ${!a.is_read ? "font-semibold" : ""}`}>{a.title}</p>
                      </div>
                      <p className="text-xs text-gray-400 line-clamp-1">{a.message}</p>
                    </div>
                    <span className={`text-xs px-2 py-0.5 rounded-full shrink-0 border ${RISK_COLOR[a.risk_level] || "bg-gray-100 text-gray-600 border-gray-200"}`}>
                      {a.risk_level}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Recent Detections */}
        <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-gray-700 flex items-center gap-2">
              <span>🔬</span> Recent Detections
            </h3>
            <a href="/detections" className="text-xs text-green-600 hover:text-green-700 font-medium">View all →</a>
          </div>
          {detections.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-3xl mb-2">✅</p>
              <p className="text-gray-400 text-sm">No disease detections</p>
            </div>
          ) : (
            <div className="space-y-2">
              {detections.map((d: any) => (
                <div key={d.id} className="p-3 bg-gray-50 rounded-xl border border-gray-100">
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-semibold text-gray-800 line-clamp-1">{d.disease_name}</p>
                      <p className="text-xs text-gray-500 mt-0.5">
                        Zone {d.zone_code} · {d.confidence_score}% confidence
                      </p>
                      {/* Confidence bar */}
                      <div className="mt-1.5 h-1 bg-gray-200 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full ${d.confidence_score >= 90 ? "bg-red-500" : d.confidence_score >= 70 ? "bg-orange-400" : "bg-yellow-400"}`}
                          style={{ width: `${d.confidence_score}%` }}
                        ></div>
                      </div>
                    </div>
                    <div className="flex flex-col items-end gap-1 shrink-0">
                      <span className={`text-xs px-2 py-0.5 rounded-full ${RISK_COLOR[d.severity] || "bg-gray-100 text-gray-600 border-gray-200"} border`}>
                        {d.severity}
                      </span>
                      <span className={`text-xs px-2 py-0.5 rounded-full ${d.status === "active" ? "bg-red-100 text-red-600" : "bg-green-100 text-green-600"}`}>
                        {d.status}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Disease Risk Guide — matches backend risk.py exactly */}
        <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
          <h3 className="font-semibold text-gray-700 mb-4 flex items-center gap-2">
            <span>📋</span> Disease Risk Guide
          </h3>
          <p className="text-xs text-gray-400 mb-3">Conditions that trigger alerts from your IoT sensor</p>
          <div className="space-y-2">
            {DISEASE_GUIDE.map((d) => (
              <div key={d.disease} className={`p-2.5 rounded-xl border ${RISK_COLOR[d.level]}`}>
                <div className="flex items-center gap-2 mb-0.5">
                  <span className="text-sm">{d.icon}</span>
                  <p className="text-xs font-semibold">{d.disease}</p>
                </div>
                <p className="text-xs opacity-75 ml-5">{d.condition}</p>
              </div>
            ))}
          </div>
          <div className="mt-3 pt-3 border-t border-gray-100">
            <p className="text-xs text-gray-400 text-center">
              Data from ESP32 DHT22 sensor · Updates every 30s
            </p>
          </div>
        </div>

      </div>
    </DashboardLayout>
  );
}
