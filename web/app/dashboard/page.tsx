"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import DashboardLayout from "@/components/layout/DashboardLayout";
import CreateFarmPrompt from "@/components/CreateFarmPrompt";
import api from "@/lib/api";
import { useFarm } from "@/lib/useFarm";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, AreaChart, Area
} from "recharts";

const riskColor: Record<string, string> = {
  low: "bg-green-100 text-green-700",
  medium: "bg-yellow-100 text-yellow-700",
  high: "bg-orange-100 text-orange-700",
  critical: "bg-red-100 text-red-700",
};

const riskDot: Record<string, string> = {
  low: "bg-green-500",
  medium: "bg-yellow-500",
  high: "bg-orange-500",
  critical: "bg-red-500",
};

export default function DashboardPage() {
  const router = useRouter();
  const { farmId, farm, loading: farmLoading, noFarm, refetch } = useFarm();
  const [summary, setSummary] = useState<any>(null);
  const [latestSensor, setLatestSensor] = useState<any>(null);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [detections, setDetections] = useState<any[]>([]);
  const [sensorHistory, setSensorHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) { router.push("/login"); return; }
  }, []);

  useEffect(() => {
    if (farmId) fetchAll(farmId);
    else if (!farmLoading) setLoading(false);
  }, [farmId, farmLoading]);

  const fetchAll = async (id: string) => {
    try {
      const [sumRes, sensorRes, alertRes, detRes, histRes] = await Promise.all([
        api.get(`/alerts/farm/${id}/summary`),
        api.get(`/iot/sensors/${id}/latest`),
        api.get(`/alerts/?limit=5`),
        api.get(`/disease/${id}/detections?limit=5`),
        api.get(`/iot/sensors/${id}/history?limit=20`),
      ]);
      setSummary(sumRes.data);
      setLatestSensor(sensorRes.data);
      setAlerts(alertRes.data.alerts);
      setDetections(detRes.data.detections);
      const history = histRes.data.readings.reverse().map((r: any, i: number) => ({
        time: `${i + 1}`,
        temp: r.temperature,
        humidity: r.humidity,
        soil: r.soil_moisture,
      }));
      setSensorHistory(history);
    } catch { router.push("/login"); }
    finally { setLoading(false); }
  };

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
  const healthColors: Record<string, string> = {
    HEALTHY: "text-green-600 bg-green-50 border-green-200",
    "MODERATE RISK": "text-yellow-600 bg-yellow-50 border-yellow-200",
    "HIGH RISK": "text-orange-600 bg-orange-50 border-orange-200",
    CRITICAL: "text-red-600 bg-red-50 border-red-200",
  };

  return (
    <DashboardLayout title="Dashboard">
      {/* Refresh Button */}
      <div className="flex justify-end mb-4">
        <button onClick={() => { setLoading(true); fetchAll(farmId!); }}
          className="flex items-center gap-2 text-sm text-gray-500 hover:text-green-600 border border-gray-200 hover:border-green-300 px-3 py-1.5 rounded-xl transition">
          🔄 Refresh
        </button>
      </div>

      {/* Farm Health Banner */}
      <div className={`border rounded-2xl p-5 mb-6 flex items-center justify-between ${healthColors[health] || healthColors["HEALTHY"]}`}>
        <div>
          <p className="text-sm font-medium opacity-70">Overall Farm Health</p>
          <h2 className="text-2xl font-bold">{health}</h2>
          <p className="text-sm opacity-70 mt-1">{farm?.name} — {farm?.location}</p>
        </div>
        <span className="text-5xl">
          {health === "HEALTHY" ? "✅" : health === "CRITICAL" ? "🚨" : "⚠️"}
        </span>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        {[
          { label: "Active Diseases", value: summary?.active_diseases ?? 0, icon: "🦠", color: "text-red-600", bg: "bg-red-50" },
          { label: "Alerts Today", value: summary?.alerts_today ?? 0, icon: "🔔", color: "text-orange-600", bg: "bg-orange-50" },
          { label: "Zones Scanned", value: summary?.scans_today ?? 0, icon: "📷", color: "text-blue-600", bg: "bg-blue-50" },
          { label: "Detections Today", value: summary?.detections_today ?? 0, icon: "🔬", color: "text-purple-600", bg: "bg-purple-50" },
        ].map((s) => (
          <div key={s.label} className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
            <div className={`w-12 h-12 ${s.bg} rounded-xl flex items-center justify-center text-2xl mb-3`}>
              {s.icon}
            </div>
            <p className="text-sm text-gray-500">{s.label}</p>
            <p className={`text-3xl font-bold ${s.color}`}>{s.value}</p>
          </div>
        ))}
      </div>

      {/* Sensor + Chart Row */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        {/* Live Sensor Readings */}
        <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
          <h3 className="font-semibold text-gray-700 mb-4 flex items-center gap-2">
            <span>📡</span> Live Sensor Readings
          </h3>
          {latestSensor ? (
            <div className="space-y-4">
              {[
                { label: "Temperature", value: `${latestSensor.temperature}°C`, icon: "🌡️", color: "text-orange-500" },
                { label: "Humidity", value: `${latestSensor.humidity}%`, icon: "💧", color: "text-blue-500" },
                { label: "Soil Moisture", value: `${latestSensor.soil_moisture}%`, icon: "🌱", color: "text-green-500" },
              ].map((item) => (
                <div key={item.label} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span>{item.icon}</span>
                    <span className="text-sm text-gray-600">{item.label}</span>
                  </div>
                  <span className={`font-bold ${item.color}`}>{item.value}</span>
                </div>
              ))}
              <div className="pt-2 border-t">
                <span className={`text-xs px-3 py-1 rounded-full font-medium ${riskColor[latestSensor.risk_level] || riskColor.low}`}>
                  <span className={`inline-block w-2 h-2 rounded-full mr-1 ${riskDot[latestSensor.risk_level] || riskDot.low}`}></span>
                  {latestSensor.risk_level?.toUpperCase()} RISK
                </span>
              </div>
            </div>
          ) : <p className="text-gray-400 text-sm">No readings yet</p>}
        </div>

        {/* Temperature & Humidity Chart */}
        <div className="col-span-2 bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
          <h3 className="font-semibold text-gray-700 mb-4 flex items-center gap-2">
            <span>📈</span> Temperature & Humidity Trend
          </h3>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={sensorHistory}>
              <defs>
                <linearGradient id="tempGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#f97316" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#f97316" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="humGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="time" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Area type="monotone" dataKey="temp" stroke="#f97316" fill="url(#tempGrad)" name="Temp °C" strokeWidth={2} />
              <Area type="monotone" dataKey="humidity" stroke="#3b82f6" fill="url(#humGrad)" name="Humidity %" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Alerts + Detections Row */}
      <div className="grid grid-cols-2 gap-4">
        {/* Recent Alerts */}
        <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
          <h3 className="font-semibold text-gray-700 mb-4 flex items-center gap-2">
            <span>🔔</span> Recent Alerts
          </h3>
          {alerts.length === 0 ? (
            <p className="text-gray-400 text-sm text-center py-6">No alerts</p>
          ) : (
            <div className="space-y-3">
              {alerts.map((a: any) => (
                <div key={a.id} className={`p-3 rounded-xl border ${a.is_read ? "bg-gray-50 border-gray-100" : "bg-orange-50 border-orange-100"}`}>
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-800 line-clamp-1">{a.title}</p>
                      <p className="text-xs text-gray-500 mt-0.5 line-clamp-1">{a.message}</p>
                    </div>
                    <span className={`text-xs px-2 py-0.5 rounded-full shrink-0 ${riskColor[a.risk_level] || "bg-gray-100 text-gray-600"}`}>
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
          <h3 className="font-semibold text-gray-700 mb-4 flex items-center gap-2">
            <span>🔬</span> Recent Detections
          </h3>
          {detections.length === 0 ? (
            <p className="text-gray-400 text-sm text-center py-6">No detections</p>
          ) : (
            <div className="space-y-3">
              {detections.map((d: any) => (
                <div key={d.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-xl border border-gray-100">
                  <div>
                    <p className="text-sm font-medium text-gray-800">{d.disease_name}</p>
                    <p className="text-xs text-gray-500">Zone {d.zone_code} · {d.confidence_score}% confidence</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={`text-xs px-2 py-1 rounded-full ${riskColor[d.severity] || "bg-gray-100 text-gray-600"}`}>
                      {d.severity}
                    </span>
                    <span className={`text-xs px-2 py-1 rounded-full ${d.status === "active" ? "bg-red-100 text-red-600" : "bg-green-100 text-green-600"}`}>
                      {d.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
}
