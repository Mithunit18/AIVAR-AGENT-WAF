import { useState, useEffect } from 'react';
import { policiesApi } from '../api/policies';
import { RefreshCw, Plus, Edit2, Trash2, Eye, Shield, Play, Pause, ChevronLeft } from 'lucide-react';
import PolicyForm from '../components/PolicyForm';
import { ConfirmModal } from '../components/Modal';

export default function PoliciesView({ showToast }) {
  const [policies, setPolicies] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activeView, setActiveView] = useState('list'); // 'list', 'create', 'edit'
  const [selectedPolicy, setSelectedPolicy] = useState(null);
  const [deleteTarget, setDeleteTarget] = useState(null);

  const fetchPolicies = async () => {
    setLoading(true);
    try {
      const data = await policiesApi.getAll();
      setPolicies(data.policies || []);
    } catch (err) {
      showToast("Failed to fetch policies", "error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPolicies();
  }, []);

  const handleDeleteConfirm = async () => {
    const agentId = deleteTarget;
    setDeleteTarget(null);
    try {
      await policiesApi.delete(agentId);
      showToast("Policy deleted successfully", "success");
      fetchPolicies();
    } catch (err) {
      showToast(`Failed to delete policy: ${err.message}`, "error");
    }
  };

  const handleEdit = (policy) => {
    setSelectedPolicy(policy);
    setActiveView('edit');
  };

  const handleCreate = () => {
    setSelectedPolicy(null);
    setActiveView('create');
  };

  const handleBack = () => {
    setActiveView('list');
    setSelectedPolicy(null);
    fetchPolicies();
  };

  if (activeView === 'create' || activeView === 'edit') {
    return (
      <div className="flex flex-col gap-6 animate-in fade-in duration-300">
        <div className="flex items-center gap-4">
          <button 
            onClick={handleBack}
            className="flex items-center gap-2 text-slate-400 hover:text-slate-200 transition-colors"
          >
            <ChevronLeft size={20} /> Back to Policies
          </button>
        </div>
        <PolicyForm 
          initialData={selectedPolicy} 
          isEdit={activeView === 'edit'} 
          onSuccess={handleBack}
          showToast={showToast}
        />
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6 animate-in fade-in duration-300">
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
        
        {/* Toolbar */}
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-200">Active Policies</h2>
          <div className="flex items-center gap-3">
            <button 
              onClick={fetchPolicies}
              className="p-2 bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-slate-200 rounded-lg transition-colors"
              title="Refresh"
            >
              <RefreshCw size={16} className={loading ? "animate-spin" : ""} />
            </button>
            <button 
              onClick={handleCreate}
              className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
            >
              <Plus size={18} /> New Policy
            </button>
          </div>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-950/50 text-xs uppercase text-slate-500 border-b border-slate-800">
              <tr>
                <th className="px-6 py-3 font-semibold">Agent ID</th>
                <th className="px-6 py-3 font-semibold">Status</th>
                <th className="px-6 py-3 font-semibold">Version</th>
                <th className="px-6 py-3 font-semibold">Rate Limit</th>
                <th className="px-6 py-3 font-semibold">Scope Count</th>
                <th className="px-6 py-3 font-semibold">Mode</th>
                <th className="px-6 py-3 font-semibold text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50">
              {loading && policies.length === 0 ? (
                <tr>
                  <td colSpan="7" className="px-6 py-8 text-center text-slate-500">
                    <RefreshCw className="animate-spin mx-auto mb-2 opacity-50" size={24} />
                    Loading policies...
                  </td>
                </tr>
              ) : policies.length === 0 ? (
                <tr>
                  <td colSpan="7" className="px-6 py-12 text-center text-slate-400">
                    <Shield size={32} className="mx-auto mb-3 opacity-20" />
                    <p className="text-base font-medium">No policies configured.</p>
                    <p className="text-sm mt-1 opacity-70">Create your first Agent WAF policy to begin securing agent traffic.</p>
                  </td>
                </tr>
              ) : (
                policies.map((policy) => {
                  const scopeCount = policy.data_scope?.allowed_scopes ? Object.keys(policy.data_scope.allowed_scopes).length : 0;
                  
                  return (
                    <tr key={policy.agent_id} className="hover:bg-slate-800/50 transition-colors">
                      <td className="px-6 py-4 font-mono text-sky-400 font-medium">
                        {policy.agent_id}
                      </td>
                      <td className="px-6 py-4">
                        {policy.enabled ? (
                          <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-xs font-medium bg-emerald-500/10 text-emerald-400">
                            <Play size={12} /> Active
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-xs font-medium bg-slate-800 text-slate-400 border border-slate-700">
                            <Pause size={12} /> Disabled
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4 font-mono text-xs">
                        v{policy.version}
                      </td>
                      <td className="px-6 py-4 text-slate-400 text-xs">
                        {policy.rate_limit?.enabled 
                          ? `${policy.rate_limit.max_calls} / ${policy.rate_limit.window_seconds}s` 
                          : 'Disabled'}
                      </td>
                      <td className="px-6 py-4 text-slate-400 text-xs">
                        {policy.data_scope?.enabled ? `${scopeCount} keys` : 'Disabled'}
                      </td>
                      <td className="px-6 py-4">
                        {policy.shadow_mode ? (
                          <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-xs font-medium bg-amber-500/10 text-amber-400 border border-amber-500/20">
                            <Eye size={12} /> Shadow
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-xs font-medium bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                            <Shield size={12} /> Enforce
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4 text-right">
                        <div className="flex items-center justify-end gap-2">
                          <button 
                            onClick={() => handleEdit(policy)}
                            className="p-1.5 text-slate-400 hover:text-sky-400 hover:bg-sky-500/10 rounded transition-colors"
                            title="Edit Policy"
                          >
                            <Edit2 size={16} />
                          </button>
                          <button 
                            onClick={() => setDeleteTarget(policy.agent_id)}
                            className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 rounded transition-colors"
                            title="Delete Policy"
                          >
                            <Trash2 size={16} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Delete Confirmation Modal */}
      <ConfirmModal
        open={!!deleteTarget}
        title="Delete Policy"
        message={`Are you sure you want to delete the policy for agent "${deleteTarget}"? This will remove all WAF rules controlling this agent's tool invocations. This action cannot be undone.`}
        confirmLabel="Delete Policy"
        confirmVariant="danger"
        onConfirm={handleDeleteConfirm}
        onCancel={() => setDeleteTarget(null)}
      />
    </div>
  );
}
