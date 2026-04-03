"use client";
import { useState } from "react";
import api from "@/lib/api";

interface Props {
  onCreated: () => void;
}

export default function CreateFarmPrompt({ onCreated }: Props) {
  const [form, setForm] = useState({
    name: "",
    location: "",
    district: "",
    size_hectares: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await api.post("/farms/", {
        name: form.name,
        location: form.location,
        district: form.district,
        size_hectares: parseFloat(form.size_hectares) || 1.0,
        latitude: null,
        longitude: null,
      });
      onCreated();
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Failed to create farm");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-8 w-full max-w-md text-center">
        <span className="text-6xl">🌿</span>
        <h2 className="text-xl font-bold text-gray-800 mt-4 mb-1">Set Up Your Farm</h2>
        <p className="text-gray-500 text-sm mb-6">
          You don't have a farm yet. Create one to start monitoring.
        </p>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg mb-4 text-sm text-left">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-3 text-left">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Farm Name</label>
            <input
              type="text" required value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 text-sm"
              placeholder="e.g. Rutembeza Tomato Farm"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Location</label>
            <input
              type="text" required value={form.location}
              onChange={(e) => setForm({ ...form, location: e.target.value })}
              className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 text-sm"
              placeholder="e.g. Musanze, Rwanda"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">District</label>
            <input
              type="text" required value={form.district}
              onChange={(e) => setForm({ ...form, district: e.target.value })}
              className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 text-sm"
              placeholder="e.g. Musanze"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Farm Size (hectares)</label>
            <input
              type="number" step="0.1" min="0.1" required value={form.size_hectares}
              onChange={(e) => setForm({ ...form, size_hectares: e.target.value })}
              className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 text-sm"
              placeholder="e.g. 2.5"
            />
          </div>
          <button
            type="submit" disabled={loading}
            className="w-full bg-green-600 hover:bg-green-700 disabled:bg-green-400 text-white font-semibold py-3 rounded-xl transition mt-2"
          >
            {loading ? "Creating farm..." : "Create Farm & Start Monitoring"}
          </button>
        </form>
      </div>
    </div>
  );
}
