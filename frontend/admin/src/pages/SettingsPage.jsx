// frontend/admin/src/pages/SettingsPage.jsx
import { useState, useEffect } from "react";
import axios from "axios";

export default function SettingsPage() {
  // 1) Initiera state för inställningar
  const [settings, setSettings] = useState({
    rbac_enabled: false,
    oidc_enabled: false,
    retention_enabled: false,
    logo_url: "",
    cleanup_schedule: "daily"
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");

  // 2) Hämta inställningar vid mount
  useEffect(() => {
    axios.get("http://localhost:8000/admin/settings", {
      headers: { Authorization: "Bearer dummyToken" }
    })
    .then(res => {
      // Konvertera eventuella strängvärden till boolean
      const data = Object.fromEntries(
        Object.entries(res.data).map(([k,v]) => [k, v === "true" ? true : v === "false" ? false : v])
      );
      setSettings(data);
    })
    .catch(console.error)
    .finally(() => setLoading(false));
  }, []);

  // 3) Hantera input-ändringar
  const handleChange = e => {
    const { name, type, checked, value } = e.target;
    setSettings(prev => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value
    }));
  };

  // 4) Spara inställningar
  const handleSave = () => {
    setSaving(true);
    axios.post("http://localhost:8000/admin/settings", settings, {
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer dummyToken"
      }
    })
    .then(() => setMessage("Settings saved!"))
    .catch(() => setMessage("Save failed"))
    .finally(() => setSaving(false));
  };

  if (loading) return <p>Loading settings…</p>;

  return (
    <div className="p-4 max-w-xl mx-auto">
      {/* Konfigurationsbanner */}
      {!settings.rbac_enabled && (
        <div className="bg-red-200 text-red-800 p-2 text-center font-semibold mb-4">
          ⚙️ Configuration Mode – alla endpoints är öppna utan autentisering
        </div>
      )}

      <h1 className="text-2xl mb-4">Admin Settings</h1>
      <div className="space-y-4">
        <label>
          <input
            type="checkbox"
            name="rbac_enabled"
            checked={settings.rbac_enabled}
            onChange={handleChange}
          /> Enable RBAC
        </label>
        <label>
          <input
            type="checkbox"
            name="oidc_enabled"
            checked={settings.oidc_enabled}
            onChange={handleChange}
          /> Enable OIDC/AD
        </label>
        <label>
          Retention Cleanup Schedule:
          <select
            name="cleanup_schedule"
            value={settings.cleanup_schedule}
            onChange={handleChange}
            className="ml-2"
          >
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
            <option value="monthly">Monthly</option>
          </select>
        </label>
        <label className="flex flex-col">
          Logo URL:
          <input
            type="text"
            name="logo_url"
            value={settings.logo_url}
            onChange={handleChange}
            className="border p-1 mt-1"
          />
        </label>
      </div>

      <button
        onClick={handleSave}
        disabled={saving}
        className="mt-6 px-4 py-2 bg-blue-600 text-white rounded"
      >
        {saving ? "Saving…" : "Save Settings"}
      </button>
      {message && <p className="mt-2">{message}</p>}
    </div>
  );
}
