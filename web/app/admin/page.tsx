"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import DashboardLayout from "@/components/layout/DashboardLayout";
import api from "@/lib/api";

const ROLES = ["admin", "farmer", "agronomist"];

const roleColor: Record<string, string> = {
  admin: "bg-purple-100 text-purple-700",
  farmer: "bg-green-100 text-green-700",
  agronomist: "bg-blue-100 text-blue-700",
};

const roleIcon: Record<string, string> = {
  admin: "⚙️",
  farmer: "👨‍🌾",
  agronomist: "🔬",
};

export default function AdminPage() {
  const router = useRouter();
  const [stats, setStats] = useState<any>(null);
  const [users, setUsers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({ full_name: "", email: "", phone: "", password: "", role: "admin" });
  const [formError, setFormError] = useState("");
  const [formLoading, setFormLoading] = useState(false);
  const [success, setSuccess] = useState("");

  useEffect(() => {
    const user = JSON.parse(localStorage.getItem("user") || "{}");
    if (user?.role !== "admin") {
      router.push("/dashboard");
      return;
    }
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [statsRes, usersRes] = await Promise.all([
        api.get("/admin/stats"),
        api.get("/admin/users"),
      ]);
      setStats(statsRes.data);
      setUsers(usersRes.data.users);
    } catch {
      router.push("/dashboard");
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError("");
    if (form.password.length < 6) { setFormError("Password must be at least 6 characters"); return; }
    setFormLoading(true);
    try {
      await api.post("/admin/users", form);
      setSuccess(`${form.role} account created for ${form.full_name}`);
      setShowCreate(false);
      setForm({ full_name: "", email: "", phone: "", password: "", role: "admin" });
      fetchData();
      setTimeout(() => setSuccess(""), 4000);
    } catch (err: any) {
      setFormError(err?.response?.data?.detail || "Failed to create user");
    } finally {
      setFormLoading(false);
    }
  };

  const handleDeactivate = async (userId: string, name: string) => {
    if (!confirm(`Deactivate ${name}? They will not be able to log in.`)) return;
    try {
      await api.put(`/admin/users/${userId}/deactivate`);
      setSuccess(`${name} has been deactivated`);
      fetchData();
      setTimeout(() => setSuccess(""), 4000);
    } catch (err: any) {
      alert(err?.response?.data?.detail || "Failed to deactivate user");
    }
  };

  const handleReactivate = async (userId: string, name: string) => {
    try {
      await api.put(`/admin/users/${userId}/reactivate`);
      setSuccess(`${name} has been reactivated`);
      fetchData();
      setTimeout(() => setSuccess(""), 4000);
    } catch {
      alert("Failed to reactivate user");
    }
  };

  const handleRoleChange = async (userId: string, newRole: string, name: string) => {
    if (!confirm(`Change ${name}'s role to ${newRole}?`)) return;
    try {
      await api.put(`/admin/users/${userId}/role`, { role: newRole });
      setSuccess(`${name}'s role changed to ${newRole}`);
      fetchData();
      setTimeout(() => setSuccess(""), 4000);
    } catch {
      alert("Failed to change role");
    }
  };

  const handleDelete = async (userId: string, name: string) => {
    if (!confirm(`PERMANENTLY delete ${name}? This cannot be undone.`)) return;
    try {
      await api.delete(`/admin/users/${userId}`);
      setSuccess(`${name} has been deleted`);
      fetchData();
      setTimeout(() => setSuccess(""), 4000);
    } catch (err: any) {
      alert(err?.response?.data?.detail || "Failed to delete user");
    }
  };

  if (loading) return (
    <DashboardLayout title="Admin Panel">
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
          <p className="text-gray-500">Loading admin panel...</p>
        </div>
      </div>
    </DashboardLayout>
  );

  return (
    <DashboardLayout title="Admin Panel">
      {/* Success Toast */}
      {success && (
        <div className="fixed top-6 right-6 bg-green-600 text-white px-5 py-3 rounded-xl shadow-lg z-50 flex items-center gap-2">
          <span>✓</span> {success}
        </div>
      )}

      {/* System Stats */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        {[
          { label: "Total Users", value: stats?.total_users ?? 0, icon: "👥", color: "text-purple-600", bg: "bg-purple-50" },
          { label: "Farmers", value: stats?.total_farmers ?? 0, icon: "👨‍🌾", color: "text-green-600", bg: "bg-green-50" },
          { label: "Agronomists", value: stats?.total_agronomists ?? 0, icon: "🔬", color: "text-blue-600", bg: "bg-blue-50" },
          { label: "Admins", value: stats?.total_admins ?? 0, icon: "⚙️", color: "text-orange-600", bg: "bg-orange-50" },
        ].map((s) => (
          <div key={s.label} className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
            <div className={`w-12 h-12 ${s.bg} rounded-xl flex items-center justify-center text-2xl mb-3`}>{s.icon}</div>
            <p className="text-sm text-gray-500">{s.label}</p>
            <p className={`text-3xl font-bold ${s.color}`}>{s.value}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-3 gap-5">
        {/* Users Table */}
        <div className="col-span-2">
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
            <div className="flex items-center justify-between p-5 border-b border-gray-100">
              <h3 className="font-semibold text-gray-700 flex items-center gap-2">
                <span>👥</span> All Users ({users.length})
              </h3>
              <button
                onClick={() => { setShowCreate(true); setFormError(""); }}
                className="bg-purple-600 hover:bg-purple-700 text-white text-sm font-medium px-4 py-2 rounded-xl transition"
              >
                + Create User
              </button>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="text-left text-xs text-gray-400 font-medium px-5 py-3">User</th>
                    <th className="text-left text-xs text-gray-400 font-medium px-3 py-3">Role</th>
                    <th className="text-left text-xs text-gray-400 font-medium px-3 py-3">Status</th>
                    <th className="text-left text-xs text-gray-400 font-medium px-3 py-3">Joined</th>
                    <th className="text-right text-xs text-gray-400 font-medium px-5 py-3">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-50">
                  {users.map((u: any) => (
                    <tr key={u.id} className="hover:bg-gray-50 transition">
                      <td className="px-5 py-3">
                        <div className="flex items-center gap-3">
                          <div className="w-9 h-9 bg-gradient-to-br from-green-400 to-green-600 rounded-full flex items-center justify-center text-white font-bold text-sm">
                            {u.full_name?.charAt(0).toUpperCase()}
                          </div>
                          <div>
                            <p className="font-medium text-gray-800 text-sm">{u.full_name}</p>
                            <p className="text-xs text-gray-400">{u.email}</p>
                          </div>
                        </div>
                      </td>
                      <td className="px-3 py-3">
                        <select
                          value={u.role}
                          onChange={(e) => handleRoleChange(u.id, e.target.value, u.full_name)}
                          className={`text-xs font-medium px-2 py-1 rounded-full border-0 cursor-pointer ${roleColor[u.role] || "bg-gray-100 text-gray-600"}`}
                        >
                          {ROLES.map(r => (
                            <option key={r} value={r}>{roleIcon[r]} {r}</option>
                          ))}
                        </select>
                      </td>
                      <td className="px-3 py-3">
                        <span className={`text-xs px-2 py-1 rounded-full font-medium ${u.is_active ? "bg-green-100 text-green-700" : "bg-red-100 text-red-600"}`}>
                          {u.is_active ? "Active" : "Inactive"}
                        </span>
                      </td>
                      <td className="px-3 py-3 text-xs text-gray-400">
                        {new Date(u.created_at).toLocaleDateString("en-RW", { day: "numeric", month: "short", year: "numeric" })}
                      </td>
                      <td className="px-5 py-3">
                        <div className="flex items-center justify-end gap-2">
                          {u.is_active ? (
                            <button
                              onClick={() => handleDeactivate(u.id, u.full_name)}
                              className="text-xs text-orange-500 hover:text-orange-700 border border-orange-200 hover:border-orange-400 px-2 py-1 rounded-lg transition"
                            >
                              Deactivate
                            </button>
                          ) : (
                            <button
                              onClick={() => handleReactivate(u.id, u.full_name)}
                              className="text-xs text-green-600 hover:text-green-700 border border-green-200 hover:border-green-400 px-2 py-1 rounded-lg transition"
                            >
                              Reactivate
                            </button>
                          )}
                          <button
                            onClick={() => handleDelete(u.id, u.full_name)}
                            className="text-xs text-red-500 hover:text-red-700 border border-red-200 hover:border-red-400 px-2 py-1 rounded-lg transition"
                          >
                            Delete
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Right Panel — Stats + Create Form */}
        <div className="space-y-4">
          {/* System Overview */}
          <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
            <h3 className="font-semibold text-gray-700 mb-4 flex items-center gap-2">
              <span>📊</span> System Overview
            </h3>
            <div className="space-y-3">
              {[
                { label: "Total Farms", value: stats?.total_farms ?? 0, icon: "🌿" },
                { label: "Total Detections", value: stats?.total_detections ?? 0, icon: "🔬" },
                { label: "Active Diseases", value: stats?.active_detections ?? 0, icon: "🦠" },
                { label: "Unread Alerts", value: stats?.unread_alerts ?? 0, icon: "🔔" },
                { label: "Active Users", value: stats?.active_users ?? 0, icon: "✅" },
                { label: "Inactive Users", value: stats?.inactive_users ?? 0, icon: "🚫" },
              ].map((s) => (
                <div key={s.label} className="flex items-center justify-between text-sm">
                  <span className="text-gray-500 flex items-center gap-2">
                    <span>{s.icon}</span>{s.label}
                  </span>
                  <span className="font-semibold text-gray-800">{s.value}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Role Guide */}
          <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
            <h3 className="font-semibold text-gray-700 mb-3 flex items-center gap-2">
              <span>🔐</span> Role Permissions
            </h3>
            <div className="space-y-3">
              {[
                { role: "admin", icon: "⚙️", color: "bg-purple-50 border-purple-200", perms: "Full system access, manage all users" },
                { role: "agronomist", icon: "🔬", color: "bg-blue-50 border-blue-200", perms: "View farms, analyse disease data, advise farmers" },
                { role: "farmer", icon: "👨‍🌾", color: "bg-green-50 border-green-200", perms: "View own farm, sensors, alerts, detections" },
              ].map((r) => (
                <div key={r.role} className={`rounded-xl p-3 border ${r.color}`}>
                  <p className="font-semibold text-sm capitalize">{r.icon} {r.role}</p>
                  <p className="text-xs text-gray-500 mt-0.5">{r.perms}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Create User Modal */}
      {showCreate && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-6">
            <div className="flex items-center justify-between mb-5">
              <h3 className="text-lg font-bold text-gray-800">Create New User</h3>
              <button onClick={() => setShowCreate(false)} className="text-gray-400 hover:text-gray-600 text-xl">✕</button>
            </div>

            {formError && (
              <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg mb-4 text-sm">
                {formError}
              </div>
            )}

            <form onSubmit={handleCreate} className="space-y-3">
              {/* Role selector at top */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Role</label>
                <div className="grid grid-cols-3 gap-2">
                  {ROLES.map((r) => (
                    <button
                      key={r}
                      type="button"
                      onClick={() => setForm({ ...form, role: r })}
                      className={`py-2 rounded-xl border-2 text-sm font-medium capitalize transition-all ${
                        form.role === r ? "border-purple-500 bg-purple-50 text-purple-700" : "border-gray-200 text-gray-600 hover:border-gray-300"
                      }`}
                    >
                      {roleIcon[r]} {r}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
                <input
                  type="text" required value={form.full_name}
                  onChange={(e) => setForm({ ...form, full_name: e.target.value })}
                  className="w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 text-sm"
                  placeholder="John Doe"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                <input
                  type="email" required value={form.email}
                  onChange={(e) => setForm({ ...form, email: e.target.value })}
                  className="w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 text-sm"
                  placeholder="john@example.com"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
                <input
                  type="tel" required value={form.phone}
                  onChange={(e) => setForm({ ...form, phone: e.target.value })}
                  className="w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 text-sm"
                  placeholder="+250 7XX XXX XXX"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
                <input
                  type="password" required value={form.password}
                  onChange={(e) => setForm({ ...form, password: e.target.value })}
                  className="w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 text-sm"
                  placeholder="Min 6 characters"
                />
              </div>

              <div className="flex gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowCreate(false)}
                  className="flex-1 border border-gray-300 text-gray-600 py-2.5 rounded-xl text-sm font-medium hover:bg-gray-50 transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={formLoading}
                  className="flex-1 bg-purple-600 hover:bg-purple-700 disabled:bg-purple-400 text-white py-2.5 rounded-xl text-sm font-medium transition"
                >
                  {formLoading ? "Creating..." : `Create ${form.role}`}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </DashboardLayout>
  );
}
