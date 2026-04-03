"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import api from "@/lib/api";

const ROLES = [
  {
    value: "farmer",
    label: "Farmer",
    icon: "👨‍🌾",
    description: "I own or manage a tomato farm",
  },
  {
    value: "agronomist",
    label: "Agronomist",
    icon: "🔬",
    description: "I am an agricultural expert / consultant",
  },
];

export default function RegisterPage() {
  const router = useRouter();
  const [step, setStep] = useState<1 | 2>(1);
  const [form, setForm] = useState({
    full_name: "",
    email: "",
    phone: "",
    password: "",
    confirm_password: "",
    role: "farmer",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleNext = (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (!form.full_name.trim()) { setError("Full name is required"); return; }
    if (!form.email.trim()) { setError("Email is required"); return; }
    if (!form.phone.trim()) { setError("Phone number is required"); return; }
    setStep(2);
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (form.password.length < 6) { setError("Password must be at least 6 characters"); return; }
    if (form.password !== form.confirm_password) { setError("Passwords do not match"); return; }

    setLoading(true);
    try {
      const res = await api.post("/auth/register", {
        full_name: form.full_name,
        email: form.email,
        phone: form.phone,
        password: form.password,
        role: form.role,
      });
      localStorage.setItem("token", res.data.access_token);
      localStorage.setItem("user", JSON.stringify(res.data.user));
      router.push("/dashboard");
    } catch (err: any) {
      const msg = err?.response?.data?.detail;
      setError(msg || "Registration failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-900 via-green-800 to-emerald-900 py-10">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-green-500 rounded-2xl mb-4 shadow-lg">
            <span className="text-4xl">🍅</span>
          </div>
          <h1 className="text-3xl font-bold text-white">TomatoGuard</h1>
          <p className="text-green-300 mt-1">AI & IoT Disease Detection System</p>
        </div>

        {/* Card */}
        <div className="bg-white rounded-2xl shadow-2xl p-8">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-xl font-semibold text-gray-800">Create your account</h2>
              <p className="text-sm text-gray-400 mt-0.5">
                Step {step} of 2 — {step === 1 ? "Your details" : "Password & role"}
              </p>
            </div>
            {/* Step dots */}
            <div className="flex gap-2">
              <span className={`w-3 h-3 rounded-full ${step >= 1 ? "bg-green-500" : "bg-gray-200"}`}></span>
              <span className={`w-3 h-3 rounded-full ${step >= 2 ? "bg-green-500" : "bg-gray-200"}`}></span>
            </div>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg mb-4 text-sm">
              {error}
            </div>
          )}

          {/* Step 1 — Personal Info */}
          {step === 1 && (
            <form onSubmit={handleNext} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
                <input
                  type="text"
                  required
                  value={form.full_name}
                  onChange={(e) => setForm({ ...form, full_name: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  placeholder="Rutembeza Yves"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email Address</label>
                <input
                  type="email"
                  required
                  value={form.email}
                  onChange={(e) => setForm({ ...form, email: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  placeholder="you@example.com"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Phone Number</label>
                <input
                  type="tel"
                  required
                  value={form.phone}
                  onChange={(e) => setForm({ ...form, phone: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  placeholder="+250 7XX XXX XXX"
                />
              </div>

              <button
                type="submit"
                className="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-3 rounded-lg transition-colors duration-200"
              >
                Continue →
              </button>
            </form>
          )}

          {/* Step 2 — Role & Password */}
          {step === 2 && (
            <form onSubmit={handleRegister} className="space-y-4">
              {/* Role Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">I am a...</label>
                <div className="grid grid-cols-2 gap-3">
                  {ROLES.map((r) => (
                    <button
                      key={r.value}
                      type="button"
                      onClick={() => setForm({ ...form, role: r.value })}
                      className={`p-3 rounded-xl border-2 text-left transition-all ${
                        form.role === r.value
                          ? "border-green-500 bg-green-50"
                          : "border-gray-200 hover:border-gray-300"
                      }`}
                    >
                      <span className="text-2xl">{r.icon}</span>
                      <p className={`font-semibold text-sm mt-1 ${form.role === r.value ? "text-green-700" : "text-gray-700"}`}>
                        {r.label}
                      </p>
                      <p className="text-xs text-gray-400 mt-0.5 leading-tight">{r.description}</p>
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
                <input
                  type="password"
                  required
                  value={form.password}
                  onChange={(e) => setForm({ ...form, password: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  placeholder="At least 6 characters"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Confirm Password</label>
                <input
                  type="password"
                  required
                  value={form.confirm_password}
                  onChange={(e) => setForm({ ...form, confirm_password: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  placeholder="Repeat your password"
                />
                {/* Password match indicator */}
                {form.confirm_password && (
                  <p className={`text-xs mt-1 ${form.password === form.confirm_password ? "text-green-500" : "text-red-400"}`}>
                    {form.password === form.confirm_password ? "✓ Passwords match" : "✗ Passwords do not match"}
                  </p>
                )}
              </div>

              {/* Summary */}
              <div className="bg-gray-50 rounded-xl p-3 text-sm text-gray-600">
                <p className="font-medium text-gray-700 mb-1">Account summary</p>
                <p>Name: <span className="font-medium">{form.full_name}</span></p>
                <p>Email: <span className="font-medium">{form.email}</span></p>
                <p>Role: <span className={`font-medium ${form.role === "farmer" ? "text-green-600" : "text-blue-600"}`}>
                  {ROLES.find(r => r.value === form.role)?.icon} {ROLES.find(r => r.value === form.role)?.label}
                </span></p>
              </div>

              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={() => { setStep(1); setError(""); }}
                  className="flex-1 border border-gray-300 text-gray-600 hover:bg-gray-50 font-semibold py-3 rounded-lg transition-colors duration-200"
                >
                  ← Back
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 bg-green-600 hover:bg-green-700 disabled:bg-green-400 text-white font-semibold py-3 rounded-lg transition-colors duration-200"
                >
                  {loading ? "Creating account..." : "Create Account"}
                </button>
              </div>
            </form>
          )}

          {/* Link to login */}
          <p className="text-center text-sm text-gray-500 mt-6">
            Already have an account?{" "}
            <Link href="/login" className="text-green-600 hover:text-green-700 font-medium">
              Sign in
            </Link>
          </p>
        </div>

        <p className="text-center text-green-300 text-sm mt-4">
          University of Rwanda — Final Year Project 2026
        </p>
      </div>
    </div>
  );
}
