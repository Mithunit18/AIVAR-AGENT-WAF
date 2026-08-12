import { useState, useEffect } from 'react';
import { Save, RefreshCw, AlertTriangle, Play, Pause, Eye, Shield, CheckCircle } from 'lucide-react';

export function PolicyManager({ apiUrl, agentId }) {
  const [policy, setPolicy] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);

  // For simplicity, we just use a JSON string editor for the policy configuration.
  const [jsonText, setJsonText] = useState("");

  const fetchPolicy = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${apiUrl}/api/v1/policies/${agentId}`);
      if (!res.ok) {
        if (res.status === 404) {
          // No policy exists yet, we could seed a default
          setPolicy(null);
          setJsonText(JSON.stringify({
            enabled: true,
            shadow_mode: false,
            rate_limit: { enabled: true, max_calls: 5, window_seconds: 60 },
            parameter_validation: { enabled: true, blocked_values: ["delete"], max_parameter_size: 10000 },
            data_scope: { enabled: true, allowed_scopes: { "customer_id": ["C101"] } },
            sequence_rules: { enabled: true, rules: [] }
          }, null, 2));
        } else {
          throw new Error('Failed to fetch policy');
        }
      } else {
        const data = await res.json();
        setPolicy(data);
        const { _id, agent_id, version, created_at, updated_at, ...editableFields } = data;
        setJsonText(JSON.stringify(editableFields, null, 2));
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPolicy();
  }, [apiUrl, agentId]);

  const handleSave = async () => {
    setSaving(true);
    setError(null);
    setSuccessMsg(null);
    try {
      let parsed;
      try {
        parsed = JSON.parse(jsonText);
      } catch(e) {
        throw new Error("Invalid JSON format");
      }

      const method = policy ? 'PUT' : 'POST';
      const payload = policy ? parsed : { agent_id: agentId, ...parsed };

      const res = await fetch(`${apiUrl}/api/v1/policies${policy ? `/${agentId}` : ''}`, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail?.message || "Failed to save policy");
      }

      setSuccessMsg("Policy saved successfully!");
      fetchPolicy(); // refresh
      
      setTimeout(() => setSuccessMsg(null), 3000);
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <div className="p-6 text-slate-400 flex items-center gap-2"><RefreshCw className="animate-spin" /> Loading policy...</div>;
  }

  return (
    <div className="glass-panel p-6 flex flex-col h-full gap-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-slate-200">Policy Configuration</h3>
          <p className="text-sm text-slate-400">Agent: <span className="font-mono text-sky-400">{agentId}</span></p>
        </div>
        {policy && (
          <div className="flex items-center gap-4 text-sm">
            <span className="text-slate-500">Version: {policy.version}</span>
            {policy.shadow_mode ? (
              <span className="flex items-center gap-1.5 px-2 py-1 bg-amber-500/20 text-amber-400 rounded-md">
                <Eye size={14} /> Shadow Mode
              </span>
            ) : (
              <span className="flex items-center gap-1.5 px-2 py-1 bg-indigo-500/20 text-indigo-400 rounded-md">
                <Shield size={14} /> Enforcing
              </span>
            )}
            {policy.enabled ? (
              <span className="flex items-center gap-1.5 px-2 py-1 bg-emerald-500/20 text-emerald-400 rounded-md">
                <Play size={14} /> Active
              </span>
            ) : (
              <span className="flex items-center gap-1.5 px-2 py-1 bg-slate-700 text-slate-300 rounded-md">
                <Pause size={14} /> Disabled
              </span>
            )}
          </div>
        )}
      </div>

      {error && (
        <div className="p-3 bg-rose-500/10 border border-rose-500/20 text-rose-400 rounded-lg flex items-center gap-2 text-sm">
          <AlertTriangle size={16} /> {error}
        </div>
      )}
      
      {successMsg && (
        <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 rounded-lg flex items-center gap-2 text-sm">
          <CheckCircle size={16} /> {successMsg}
        </div>
      )}

      <div className="flex-1 min-h-[300px]">
        <textarea 
          value={jsonText}
          onChange={(e) => setJsonText(e.target.value)}
          className="w-full h-full bg-slate-950/80 border border-slate-700 rounded-lg p-4 font-mono text-sm text-sky-200 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors"
          spellCheck="false"
        />
      </div>

      <div className="flex justify-end">
        <button 
          onClick={handleSave}
          disabled={saving}
          className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg font-medium transition-colors disabled:opacity-50"
        >
          {saving ? <RefreshCw size={18} className="animate-spin" /> : <Save size={18} />}
          {saving ? 'Saving...' : 'Save Policy'}
        </button>
      </div>
    </div>
  );
}
