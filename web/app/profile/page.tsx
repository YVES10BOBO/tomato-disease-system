"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import DashboardLayout from "@/components/layout/DashboardLayout";
import api from "@/lib/api";

export default function ProfilePage() {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const [infoForm, setInfoForm] = useState({ full_name: "", phone: "" });
  const [savingInfo, setSavingInfo] = useState(false);
  const [infoSuccess, setInfoSuccess] = useState("");
  const [infoError, setInfoError] = useState("");

  const [pwForm, setPwForm] = useState({ current_password: "", new_password: "", confirm_password: "" });
  const [savingPw, setSavingPw] = useState(false);
  const [pwSuccess, setPwSuccess] = useState("");
  const [pwError, setPwError] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) { router.push("/login"); return; }
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const res = await api.get("/auth/me");
      setUser(res.data);
      setInfoForm({ full_name: res.data.full_name, phone: res.data.phone });
    } catch { router.push("/login"); }
    finally { setLoading(false); }
  };

  const saveInfo = async (e: React.FormEvent) => {
    e.preventDefault();
    setInfoError(""); setInfoSuccess("");
    setSavingInfo(true);
    try {
      await api.put("/auth/profile", infoForm);
      const updated = { ...user, ...infoForm };
      setUser(updated);
      localStorage.setItem("user", JSON.stringify(updated));
      setInfoSuccess("Profile updated successfully");
      setTimeout(() => setInfoSuccess(""), 3000);
    } catch (err: any) {
      setInfoError(err?.response?.data?.detail || "Failed to update profile");
    } finally { setSavingInfo(false); }
  };

  const changePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setPwError(""); setPwSuccess("");
    if (pwForm.new_password.length < 6) { setPwError("New password must be at least 6 characters"); return; }
    if (pwForm.new_password !== pwForm.confirm_password) { setPwError("Passwords do not match"); return; }
    setSavingPw(true);
    try {
      await api.put("/auth/change-password", {
        current_password: pwForm.current_password,
        new_password: pwForm.new_password,
      });
      setPwSuccess("Password changed successfully");
      setPwForm({ current_password: "", new_password: "", confirm_password: "" });
      setTimeout(() => setPwSuccess(""), 3000);
    } catch (err: any) {
      setPwError(err?.response?.data?.detail || "Failed to change password");
    } finally { setSavingPw(false); }
  };

  if (loading) return (
    <DashboardLayout title="My Profile">
      <div className="flex items-center justify-center h-64">
        <div className="w-12 h-12 border-4 border-green-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
      </div>
    </DashboardLayout>
  );

  const roleColor: Record<string, string> = {
    admin: "bg-purple-100 text-purple-700",
    farmer: "bg-green-100 text-green-700",
    agronomist: "bg-blue-100 text-blue-700",
  };

  return (
    <DashboardLayout title="My Profile">
      <div className="max-w-2xl mx-auto space-y-5">
        {/* Profile Header */}
        <div className="bg-gradient-to-r from-green-800 to-green-700 rounded-2xl p-6 text-white flex items-center gap-5">
          <div className="w-20 h-20 bg-white/20 rounded-2xl flex items-center justify-center text-4xl font-bold">
            {user?.full_name?.charAt(0).toUpperCase()}
          </div>
          <div>
            <h2 className="text-2xl font-bold">{user?.full_name}</h2>
            <p className="text-green-200 text-sm">{user?.email}</p>
            <span className={`inline-block mt-2 text-xs font-medium px-3 py-1 rounded-full ${roleColor[user?.role] || "bg-gray-100 text-gray-600"}`}>
              {user?.role === "admin" ? "⚙️" : user?.role === "farmer" ? "👨‍🌾" : "🔬"} {user?.role}
            </span>
          </div>
        </div>

        {/* Edit Info */}
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
          <h3 className="font-semibold text-gray-700 mb-4 flex items-center gap-2">
            <span>✏️</span> Edit Profile
          </h3>
          {infoSuccess && <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-2 rounded-lg mb-4 text-sm">{infoSuccess}</div>}
          {infoError && <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-2 rounded-lg mb-4 text-sm">{infoError}</div>}
          <form onSubmit={saveInfo} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
              <input type="text" required value={infoForm.full_name}
                onChange={(e) => setInfoForm({ ...infoForm, full_name: e.target.value })}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 text-sm"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Phone Number</label>
              <input type="tel" required value={infoForm.phone}
                onChange={(e) => setInfoForm({ ...infoForm, phone: e.target.value })}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 text-sm"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Email Address</label>
              <input type="email" disabled value={user?.email}
                className="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-sm bg-gray-50 text-gray-400 cursor-not-allowed"
              />
              <p className="text-xs text-gray-400 mt-1">Email cannot be changed</p>
            </div>
            <button type="submit" disabled={savingInfo}
              className="bg-green-600 hover:bg-green-700 disabled:bg-green-400 text-white font-medium px-6 py-2.5 rounded-xl text-sm transition">
              {savingInfo ? "Saving..." : "Save Changes"}
            </button>
          </form>
        </div>

        {/* Change Password */}
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
          <h3 className="font-semibold text-gray-700 mb-4 flex items-center gap-2">
            <span>🔒</span> Change Password
          </h3>
          {pwSuccess && <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-2 rounded-lg mb-4 text-sm">{pwSuccess}</div>}
          {pwError && <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-2 rounded-lg mb-4 text-sm">{pwError}</div>}
          <form onSubmit={changePassword} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Current Password</label>
              <input type="password" required value={pwForm.current_password}
                onChange={(e) => setPwForm({ ...pwForm, current_password: e.target.value })}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 text-sm"
                placeholder="Enter current password"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">New Password</label>
              <input type="password" required value={pwForm.new_password}
                onChange={(e) => setPwForm({ ...pwForm, new_password: e.target.value })}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 text-sm"
                placeholder="At least 6 characters"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Confirm New Password</label>
              <input type="password" required value={pwForm.confirm_password}
                onChange={(e) => setPwForm({ ...pwForm, confirm_password: e.target.value })}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 text-sm"
                placeholder="Repeat new password"
              />
              {pwForm.confirm_password && (
                <p className={`text-xs mt-1 ${pwForm.new_password === pwForm.confirm_password ? "text-green-500" : "text-red-400"}`}>
                  {pwForm.new_password === pwForm.confirm_password ? "✓ Passwords match" : "✗ Passwords do not match"}
                </p>
              )}
            </div>
            <button type="submit" disabled={savingPw}
              className="bg-orange-500 hover:bg-orange-600 disabled:bg-orange-300 text-white font-medium px-6 py-2.5 rounded-xl text-sm transition">
              {savingPw ? "Changing..." : "Change Password"}
            </button>
          </form>
        </div>

        {/* Account Info */}
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
          <h3 className="font-semibold text-gray-700 mb-3 flex items-center gap-2">
            <span>ℹ️</span> Account Info
          </h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-500">Account ID</span>
              <span className="font-mono text-xs text-gray-400">{user?.id?.slice(0, 16)}...</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Member Since</span>
              <span className="text-gray-700">{new Date(user?.created_at).toLocaleDateString("en-RW", { day: "numeric", month: "long", year: "numeric" })}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Account Status</span>
              <span className="text-green-600 font-medium">Active</span>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
