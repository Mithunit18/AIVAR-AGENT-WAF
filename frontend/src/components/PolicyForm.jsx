import { useState } from 'react';
import { policiesApi } from '../api/policies';
import { Save, ShieldAlert, Plus, Trash2, Shield, Eye, RefreshCw, X } from 'lucide-react';
import { InputModal } from './Modal';

const DEFAULT_POLICY = {
  agent_id: '',
  enabled: true,
  shadow_mode: false,
  rate_limit: { enabled: true, max_calls: 5, window_seconds: 60 },
  parameter_validation: { enabled: true, blocked_values: ["delete", "DROP TABLE", "rm -rf"], max_parameter_size: 10000 },
  data_scope: { enabled: true, allowed_scopes: { "customer_id": [] } },
  sequence_rules: { enabled: true, rules: [] },
  tool_permissions: { "crm_delete": { enabled: false } }
};

export default function PolicyForm({ initialData, isEdit, onSuccess, showToast }) {
  const [formData, setFormData] = useState(() => initialData ? JSON.parse(JSON.stringify(initialData)) : JSON.parse(JSON.stringify(DEFAULT_POLICY)));
  const [saving, setSaving] = useState(false);
  const [toolModal, setToolModal] = useState(false);
  const [scopeModal, setScopeModal] = useState(false);

  // Simple nested state updater
  const updateNested = (path, value) => {
    setFormData(prev => {
      const next = { ...prev };
      let current = next;
      for (let i = 0; i < path.length - 1; i++) {
        if (!current[path[i]]) current[path[i]] = {};
        current = current[path[i]];
      }
      current[path[path.length - 1]] = value;
      return next;
    });
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      if (isEdit) {
        await policiesApi.update(initialData.agent_id, formData);
        showToast(`Policy updated successfully. V${(initialData.version || 0) + 1}`, "success");
      } else {
        await policiesApi.create(formData);
        showToast("Policy created successfully.", "success");
      }
      onSuccess();
    } catch (err) {
      showToast(err.message || "Failed to save policy", "error");
    } finally {
      setSaving(false);
    }
  };

  return (
    <form onSubmit={handleSave} className="flex flex-col gap-6">

      {/* Header Info */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-sm">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-lg font-bold text-slate-100">{isEdit ? 'Edit Policy' : 'Create New Policy'}</h2>
            <p className="text-sm text-slate-400">Configure WAF rules for an agent</p>
          </div>
          <div className="flex items-center gap-4">
            <label className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer select-none bg-slate-800/50 px-3 py-1.5 rounded-lg border border-slate-700">
              <input type="checkbox" checked={formData.shadow_mode} onChange={(e) => updateNested(['shadow_mode'], e.target.checked)} className="rounded bg-slate-950 border-slate-700 text-amber-500 focus:ring-amber-500" />
              <Eye size={16} className={formData.shadow_mode ? "text-amber-400" : "text-slate-500"} />
              Shadow Mode
            </label>
            <label className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer select-none bg-slate-800/50 px-3 py-1.5 rounded-lg border border-slate-700">
              <input type="checkbox" checked={formData.enabled} onChange={(e) => updateNested(['enabled'], e.target.checked)} className="rounded bg-slate-950 border-slate-700 text-emerald-500 focus:ring-emerald-500" />
              <Shield size={16} className={formData.enabled ? "text-emerald-400" : "text-slate-500"} />
              Enabled
            </label>
          </div>
        </div>

        <div className="max-w-md">
          <label className="block text-sm font-medium text-slate-400 mb-1">Agent ID</label>
          <input
            type="text"
            required
            disabled={isEdit}
            value={formData.agent_id}
            onChange={(e) => setFormData({ ...formData, agent_id: e.target.value })}
            placeholder="e.g. support-agent-01"
            className="w-full bg-slate-950 border border-slate-700 rounded-lg px-4 py-2 text-slate-200 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 disabled:opacity-50 disabled:bg-slate-900"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        {/* Rate Limiting */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-md font-semibold text-slate-200">Rate Limiting</h3>
            <input type="checkbox" checked={formData.rate_limit?.enabled} onChange={(e) => updateNested(['rate_limit', 'enabled'], e.target.checked)} className="rounded bg-slate-950 border-slate-700 text-indigo-500 focus:ring-indigo-500" />
          </div>
          <div className={`space-y-4 ${!formData.rate_limit?.enabled ? 'opacity-40 pointer-events-none' : ''}`}>
            <div>
              <label className="block text-sm text-slate-400 mb-1">Maximum Calls</label>
              <input type="number" min="1" value={formData.rate_limit?.max_calls || 1} onChange={(e) => updateNested(['rate_limit', 'max_calls'], parseInt(e.target.value))} className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-slate-200 focus:outline-none focus:border-indigo-500" />
            </div>
            <div>
              <label className="block text-sm text-slate-400 mb-1">Window Seconds</label>
              <input type="number" min="1" value={formData.rate_limit?.window_seconds || 60} onChange={(e) => updateNested(['rate_limit', 'window_seconds'], parseInt(e.target.value))} className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-slate-200 focus:outline-none focus:border-indigo-500" />
            </div>
          </div>
        </div>

        {/* Parameter Validation */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-md font-semibold text-slate-200">Parameter Validation</h3>
            <input type="checkbox" checked={formData.parameter_validation?.enabled} onChange={(e) => updateNested(['parameter_validation', 'enabled'], e.target.checked)} className="rounded bg-slate-950 border-slate-700 text-indigo-500 focus:ring-indigo-500" />
          </div>
          <div className={`space-y-4 ${!formData.parameter_validation?.enabled ? 'opacity-40 pointer-events-none' : ''}`}>
            <div>
              <label className="block text-sm text-slate-400 mb-1">Max Parameter Size (bytes)</label>
              <input type="number" value={formData.parameter_validation?.max_parameter_size || 10000} onChange={(e) => updateNested(['parameter_validation', 'max_parameter_size'], parseInt(e.target.value))} className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-slate-200 focus:outline-none focus:border-indigo-500" />
            </div>
            <div>
              <label className="block text-sm text-slate-400 mb-1 flex items-center justify-between">
                Blocked Values (comma separated)
              </label>
              <textarea
                rows="2"
                value={(formData.parameter_validation?.blocked_values || []).join(', ')}
                onChange={(e) => updateNested(['parameter_validation', 'blocked_values'], e.target.value.split(',').map(s => s.trim()).filter(Boolean))}
                className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-slate-200 focus:outline-none focus:border-indigo-500 text-sm font-mono"
              />
            </div>
          </div>
        </div>

        {/* Tool Permissions */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-sm">
          <h3 className="text-md font-semibold text-slate-200 mb-4">Tool Permissions</h3>
          <p className="text-xs text-slate-400 mb-4">Tools not listed here are implicitly allowed. Add a tool and uncheck to explicitly block it.</p>

          <div className="space-y-3">
            {Object.entries(formData.tool_permissions || {}).map(([toolName, perm]) => (
              <div key={toolName} className="flex items-center justify-between bg-slate-950/50 p-2 px-3 rounded-lg border border-slate-800">
                <span className="text-sm font-mono text-slate-300">{toolName}</span>
                <div className="flex items-center gap-4">
                  <label className="flex items-center gap-2 text-sm text-slate-400 cursor-pointer">
                    <input type="checkbox" checked={perm.enabled} onChange={(e) => updateNested(['tool_permissions', toolName, 'enabled'], e.target.checked)} className="rounded bg-slate-900 border-slate-600 text-indigo-500" />
                    Allowed
                  </label>
                  <button type="button" onClick={() => {
                    const next = { ...formData };
                    delete next.tool_permissions[toolName];
                    setFormData(next);
                  }} className="text-slate-500 hover:text-rose-400"><X size={16} /></button>
                </div>
              </div>
            ))}

            <button type="button" onClick={() => setToolModal(true)} className="flex items-center gap-2 text-sm text-indigo-400 hover:text-indigo-300 transition-colors py-1">
              <Plus size={16} /> Add Tool Permission
            </button>
          </div>
        </div>

        {/* Data Scope */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-md font-semibold text-slate-200">Data Scope</h3>
            <input type="checkbox" checked={formData.data_scope?.enabled} onChange={(e) => updateNested(['data_scope', 'enabled'], e.target.checked)} className="rounded bg-slate-950 border-slate-700 text-indigo-500 focus:ring-indigo-500" />
          </div>

          <div className={`space-y-4 ${!formData.data_scope?.enabled ? 'opacity-40 pointer-events-none' : ''}`}>
            {Object.entries(formData.data_scope?.allowed_scopes || {}).map(([key, values]) => (
              <div key={key} className="bg-slate-950/50 p-3 rounded-lg border border-slate-800">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-mono text-sky-400">{key}</span>
                  <button type="button" onClick={() => {
                    const next = { ...formData };
                    delete next.data_scope.allowed_scopes[key];
                    setFormData(next);
                  }} className="text-slate-500 hover:text-rose-400"><Trash2 size={14} /></button>
                </div>
                <textarea
                  rows="2"
                  placeholder="Comma separated values"
                  value={values.join(', ')}
                  onChange={(e) => updateNested(['data_scope', 'allowed_scopes', key], e.target.value.split(',').map(s => s.trim()).filter(Boolean))}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-slate-200 focus:outline-none focus:border-indigo-500 text-sm font-mono"
                />
              </div>
            ))}

            <button type="button" onClick={() => setScopeModal(true)} className="flex items-center gap-2 text-sm text-indigo-400 hover:text-indigo-300 transition-colors py-1">
              <Plus size={16} /> Add Scope Constraint
            </button>
          </div>
        </div>
      </div>

      <div className="flex justify-end pt-4">
        <button
          type="submit"
          disabled={saving}
          className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2.5 rounded-lg font-medium transition-all shadow shadow-indigo-900/20 disabled:opacity-50"
        >
          {saving ? <RefreshCw size={18} className="animate-spin" /> : <Save size={18} />}
          {saving ? 'Saving...' : 'Save Policy'}
        </button>
      </div>

      {/* Add Tool Permission Modal */}
      <InputModal
        open={toolModal}
        title="Add Tool Permission"
        description="Enter the name of the tool to configure access control for. Tools not listed are implicitly allowed."
        placeholder="e.g. crm_delete"
        submitLabel="Add Tool"
        onSubmit={(name) => {
          updateNested(['tool_permissions', name], { enabled: false });
          setToolModal(false);
        }}
        onCancel={() => setToolModal(false)}
      />

      {/* Add Data Scope Key Modal */}
      <InputModal
        open={scopeModal}
        title="Add Scope Constraint"
        description="Enter the parameter key to restrict. You can then specify the allowed values for this parameter."
        placeholder="e.g. customer_id"
        submitLabel="Add Constraint"
        onSubmit={(name) => {
          updateNested(['data_scope', 'allowed_scopes', name], []);
          setScopeModal(false);
        }}
        onCancel={() => setScopeModal(false)}
      />
    </form>
  );
}
