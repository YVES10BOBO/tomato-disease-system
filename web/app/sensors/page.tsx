"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import DashboardLayout from "@/components/layout/DashboardLayout";
import CreateFarmPrompt from "@/components/CreateFarmPrompt";
import api from "@/lib/api";
import { useFarm } from "@/lib/useFarm";
import {
  AreaChart, Area, LineChart, Line, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from "recharts";

const riskColor: Record<string, string> = {
  low: "bg-green-100 text-green-700 border-green-200",
  medium: "bg-yellow-100 text-yellow-700 border-yellow-200",
  high: "bg-orange-100 text-orange-700 border-orange-200",
  critical: "bg-red-100 text-red-700 border-red-200",
};

const riskBg: Record<string, string> = {
  low: "from-green-500 to-green-600",
  medium: "from-yellow-400 to-yellow-500",
  high: "from-orange-500 to-orange-600",
  critical: "from-red-500 to-red-600",
};

export default function SensorsPage() {
  const router = useRouter();
  const { farmId, farm, loading: farmLoading, noFarm, refetch } = useFarm();
  const [latest, setLatest] = useState<any>(null);
  const [history, setHistory] = useState<any[]>([]);
  const [riskData, setRiskData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) { router.push("/login"); return; }
  }, []);

  useEffect(() => {
    if (farmId) fetchData(farmId);
    else if (!farmLoading) setLoading(false);
  }, [farmId, farmLoading]);

  useEffect(() => {
    if (!autoRefresh || !farmId) return;
    const interval = setInterval(() => fetchLatest(farmId), 15000);
    return () => clearInterval(interval);
  }, [autoRefresh, farmId]);

  const fetchData = async (id: string) => {
    try {
      const [latestRes, histRes, riskRes] = await Promise.all([
        api.get(`/iot/sensors/${id}/latest`),
        api.get(`/iot/sensors/${id}/history?limit=30`),
        api.get(`/iot/sensors/${id}/risk`),
      ]);
      setLatest(latestRes.data);
      setRiskData(riskRes.data.risk_analysis);
      const mapped = histRes.data.readings.reverse().map((r: any, i: number) => ({
        idx: i + 1,
        temp: r.temperature,
        humidity: r.humidity,
        soil: r.soil_moisture,
        time: new Date(r.recorded_at).toLocaleTimeString("en-RW", { hour: "2-digit", minute: "2-digit" }),
      }));
      setHistory(mapped);
    } catch {
      router.push("/login");
    } finally {
      setLoading(false);
    }
  };

  const fetchLatest = async (id: string) => {
    try {
      const res = await api.get(`/iot/sensors/${id}/latest`);
      setLatest(res.data);
    } catch {}
  };

  if (noFarm) return (
    <DashboardLayout title="IoT Sensors">
      <CreateFarmPrompt onCreated={refetch} />
    </DashboardLayout>
  );

  if (farmLoading || loading) return (
    <DashboardLayout title="IoT Sensors">
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-green-500 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
          <p className="text-gray-500">Loading sensor data...</p>
        </div>
      </div>
    </DashboardLayout>
  );

  const risk = latest?.risk_level || "low";

  return (
    <DashboardLayout title="IoT Sensors">
      {/* Risk Banner */}
      <div className={`bg-gradient-to-r ${riskBg[risk] || riskBg.low} rounded-2xl p-5 mb-6 text-white`}>
        <div className="flex items-center justify-between">
          <div>
            <p className="text-white/70 text-sm font-medium">Current Environmental Risk</p>
            <h2 className="text-3xl font-bold uppercase">{risk} RISK</h2>
            <p className="text-white/70 text-sm mt-1">ESP32 sensor node · {farm?.name}</p>
          </div>
          <div className="text-right">
            <span className="text-5xl">
              {risk === "low" ? "✅" : risk === "medium" ? "⚠️" : risk === "high" ? "🔥" : "🚨"}
            </span>
            <div className="flex items-center gap-2 mt-2 justify-end">
              <button
                onClick={() => setAutoRefresh(!autoRefresh)}
                className={`text-xs px-3 py-1 rounded-full border transition ${autoRefresh ? "bg-white/20 border-white/40" : "border-white/30 opacity-60"}`}
              >
                {autoRefresh ? "🔄 Auto-refresh ON" : "⏸ Auto-refresh OFF"}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Live Readings Cards */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        {[
          {
            label: "Temperature",
            value: latest?.temperature,
            unit: "°C",
            icon: "🌡️",
            color: "text-orange-600",
            bg: "bg-orange-50",
            border: "border-orange-100",
            normal: "18–30°C",
            status: latest?.temperature > 30 ? "High" : latest?.temperature < 18 ? "Low" : "Normal",
            statusColor: latest?.temperature > 30 || latest?.temperature < 18 ? "text-orange-500" : "text-green-500",
          },
          {
            label: "Humidity",
            value: latest?.humidity,
            unit: "%",
            icon: "💧",
            color: "text-blue-600",
            bg: "bg-blue-50",
            border: "border-blue-100",
            normal: "60–80%",
            status: latest?.humidity > 85 ? "High" : latest?.humidity < 50 ? "Low" : "Normal",
            statusColor: latest?.humidity > 85 || latest?.humidity < 50 ? "text-orange-500" : "text-green-500",
          },
          {
            label: "Soil Moisture",
            value: latest?.soil_moisture,
            unit: "%",
            icon: "🌱",
            color: "text-green-600",
            bg: "bg-green-50",
            border: "border-green-100",
            normal: "40–70%",
            status: latest?.soil_moisture > 80 ? "Waterlogged" : latest?.soil_moisture < 30 ? "Dry" : "Optimal",
            statusColor: latest?.soil_moisture > 80 || latest?.soil_moisture < 30 ? "text-orange-500" : "text-green-500",
          },
        ].map((s) => (
          <div key={s.label} className={`bg-white rounded-2xl p-5 shadow-sm border ${s.border}`}>
            <div className={`w-14 h-14 ${s.bg} rounded-2xl flex items-center justify-center text-3xl mb-4`}>
              {s.icon}
            </div>
            <p className="text-sm text-gray-500 mb-1">{s.label}</p>
            <div className="flex items-baseline gap-1 mb-2">
              <span className={`text-4xl font-bold ${s.color}`}>{s.value ?? "--"}</span>
              <span className="text-lg text-gray-400">{s.unit}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-400">Normal: {s.normal}</span>
              <span className={`text-xs font-semibold ${s.statusColor}`}>{s.status}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        {/* Temp & Humidity Chart */}
        <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
          <h3 className="font-semibold text-gray-700 mb-4 flex items-center gap-2">
            <span>📈</span> Temperature & Humidity (Last 30 readings)
          </h3>
          <ResponsiveContainer width="100%" height={220}>
            <AreaChart data={history}>
              <defs>
                <linearGradient id="t" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#f97316" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#f97316" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="h" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="time" tick={{ fontSize: 10 }} interval={4} />
              <YAxis tick={{ fontSize: 10 }} />
              <Tooltip />
              <Legend />
              <Area type="monotone" dataKey="temp" stroke="#f97316" fill="url(#t)" name="Temp °C" strokeWidth={2} dot={false} />
              <Area type="monotone" dataKey="humidity" stroke="#3b82f6" fill="url(#h)" name="Humidity %" strokeWidth={2} dot={false} />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Soil Moisture Chart */}
        <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
          <h3 className="font-semibold text-gray-700 mb-4 flex items-center gap-2">
            <span>🌱</span> Soil Moisture Trend
          </h3>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={history}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="time" tick={{ fontSize: 10 }} interval={4} />
              <YAxis tick={{ fontSize: 10 }} domain={[0, 100]} />
              <Tooltip />
              <Line type="monotone" dataKey="soil" stroke="#22c55e" name="Soil %" strokeWidth={2} dot={false} />
              {/* Reference lines */}
              <Line type="monotone" dataKey={() => 70} stroke="#f59e0b" strokeDasharray="4 4" name="Upper limit" dot={false} strokeWidth={1} />
              <Line type="monotone" dataKey={() => 40} stroke="#f59e0b" strokeDasharray="4 4" name="Lower limit" dot={false} strokeWidth={1} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Risk Analysis + Recent Readings Table */}
      <div className="grid grid-cols-3 gap-4">
        {/* Risk Analysis */}
        <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
          <h3 className="font-semibold text-gray-700 mb-4 flex items-center gap-2">
            <span>🔬</span> Risk Analysis
          </h3>
          {riskData ? (
            <div className="space-y-3">
              <div className={`p-3 rounded-xl border ${riskColor[riskData.risk_level] || riskColor.low}`}>
                <p className="text-xs font-medium mb-1 opacity-70">Overall Risk</p>
                <p className="text-xl font-bold uppercase">{riskData.risk_level}</p>
              </div>
              {riskData.risks?.length > 0 && (
                <div>
                  <p className="text-xs text-gray-500 mb-2 font-medium">Detected Risks:</p>
                  {riskData.risks.map((r: any, i: number) => (
                    <div key={i} className="mb-2 p-2 bg-orange-50 rounded-lg border border-orange-100">
                      <div className="flex items-center gap-1 text-xs font-medium text-orange-700 mb-0.5">
                        <span>⚠</span> {r.disease}
                      </div>
                      <p className="text-xs text-gray-600">{r.action}</p>
                    </div>
                  ))}
                </div>
              )}
              <div className="bg-gray-50 rounded-xl p-2">
                <p className="text-xs text-gray-500">{riskData.summary}</p>
              </div>
            </div>
          ) : (
            <p className="text-sm text-gray-400 text-center py-6">No risk data</p>
          )}
        </div>

        {/* Recent Readings Table */}
        <div className="col-span-2 bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
          <h3 className="font-semibold text-gray-700 mb-4 flex items-center gap-2">
            <span>📋</span> Recent Readings
          </h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-100">
                  <th className="text-left text-xs text-gray-400 font-medium pb-2">#</th>
                  <th className="text-left text-xs text-gray-400 font-medium pb-2">Time</th>
                  <th className="text-right text-xs text-gray-400 font-medium pb-2">Temp (°C)</th>
                  <th className="text-right text-xs text-gray-400 font-medium pb-2">Humidity (%)</th>
                  <th className="text-right text-xs text-gray-400 font-medium pb-2">Soil (%)</th>
                </tr>
              </thead>
              <tbody>
                {history.slice(-10).reverse().map((r) => (
                  <tr key={r.idx} className="border-b border-gray-50 hover:bg-gray-50 transition">
                    <td className="py-2 text-gray-400 text-xs">{r.idx}</td>
                    <td className="py-2 text-gray-600 font-mono text-xs">{r.time}</td>
                    <td className={`py-2 text-right font-medium ${r.temp > 30 ? "text-orange-500" : "text-gray-800"}`}>{r.temp}</td>
                    <td className={`py-2 text-right font-medium ${r.humidity > 85 ? "text-blue-500" : "text-gray-800"}`}>{r.humidity}</td>
                    <td className={`py-2 text-right font-medium ${r.soil < 30 || r.soil > 80 ? "text-orange-500" : "text-green-600"}`}>{r.soil}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
