import { useState, useEffect } from "react";
import axios from "axios";

export default function SettingsPage() {
  // State för alla inställningar
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

  // 1) Hämta initvärden
  useEffect(() => {
    axios.get("http://localhost:8000/admin/settings", {
      headers: { Authorization: "Bearer dummyToken" } // tills vidare
    })
    .then(res => {
      // res.data är { key: value, … }
      setSettings(res.data);
      setLoading(false);
    })
    .catch(err => {
      console.error(err);
      setLoading(false);
    });
  }, []);

  // 2) Hantera formändringar
  const handleChange = e => {
    const { name, type, checked, value } = e.target;
    setSettings(prev => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value
    }));
  };

  // 3) Skicka POST när Save klickas
  const handleSave = () => {
    setSaving(true);
    axios.post(
      "http://localhost:8000/admin/settings",
      settings,
      { headers: { "Content-Type": "application/json", Authorization: "Bearer dummyToken" } }
    )
    .then(res => {
      setMessage("Settings saved!");
    })
    .catch(err => {
      console.error(err);
      setMessage("Save failed");
    })
    .finally(() => setSaving(false));
  };

  if (loading) return <p>Loading settings…</p>;

  return (
    <div className="p-4 max-w-xl mx-auto">
      <h1 className="text-2xl mb-4">Admin Settings</h1>
      <div className="space-y-4">
        <label>
          <input
            type="checkbox"
            name="rbac_enabled"
            checked={settings.rbac_enabled === "true" || settings.rbac_enabled === true}
            onChange={handleChange}
          /> Enable RBAC
        </label>
        <label>
          <input
            type="checkbox"
            name="oidc_enabled"
            checked={settings.oidc_enabled === "true" || settings.oidc_enabled === true}
            onChange={handleChange}
          /> Enable OIDC/AD
        </label>
        <label>
          Retention Cleanup Schedule:
          <select name="cleanup_schedule" value={settings.cleanup_schedule} onChange={handleChange}>
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
            <option value="monthly">Monthly</option>
          </select>
        </label>
        <label>
          Logo URL:
          <input
            type="text"
            name="logo_url"
            value={settings.logo_url || ""}
            onChange={handleChange}
            className="border p-1 ml-2"
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
