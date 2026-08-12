import { X, ShieldAlert, CheckCircle, Clock, Info } from 'lucide-react';

export function EventDetailModal({ event, onClose }) {
  if (!event) return null;

  const isBlocked = event.final_disposition === 'BLOCK';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
      <div className="bg-slate-900 border border-slate-700 w-full max-w-3xl rounded-xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-slate-800 bg-slate-800/30">
          <div className="flex items-center gap-3">
            {isBlocked ? (
              <div className="p-2 bg-rose-500/20 text-rose-400 rounded-lg">
                <ShieldAlert size={24} />
              </div>
            ) : (
              <div className="p-2 bg-emerald-500/20 text-emerald-400 rounded-lg">
                <CheckCircle size={24} />
              </div>
            )}
            <div>
              <h2 className="text-xl font-bold text-slate-100">
                {event.tool_name}
              </h2>
              <div className="text-sm text-slate-400 flex items-center gap-2">
                <span className="font-mono bg-slate-800 px-2 py-0.5 rounded text-sky-400">
                  {event.agent_id}
                </span>
                <span>•</span>
                <span>{new Date(event.timestamp).toLocaleString()}</span>
                <span>•</span>
                <span>{event.latency_ms}ms</span>
              </div>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-slate-100 hover:bg-slate-800 rounded-lg transition-colors"
          >
            <X size={20} />
          </button>
        </div>

        {/* Body */}
        <div className="p-6 overflow-y-auto flex-1 space-y-6">
          
          {/* Rules Evaluation */}
          <div>
            <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-3">Rule Evaluations</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {event.rule_evaluations?.map((rule, idx) => (
                <div 
                  key={idx} 
                  className={`p-3 rounded-lg border ${
                    rule.status === 'PASS' 
                      ? 'bg-emerald-900/10 border-emerald-500/20' 
                      : 'bg-rose-900/10 border-rose-500/20'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-semibold text-slate-200 capitalize">
                      {rule.rule.replace('_', ' ')}
                    </span>
                    <span className={`text-xs font-bold ${
                      rule.status === 'PASS' ? 'text-emerald-400' : 'text-rose-400'
                    }`}>
                      {rule.status}
                    </span>
                  </div>
                  {rule.reason && (
                    <p className="text-sm text-slate-400">{rule.reason}</p>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Parameters */}
          <div>
            <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-3">Parameters (Sanitized)</h3>
            <div className="bg-slate-950 rounded-lg p-4 border border-slate-800 overflow-x-auto">
              <pre className="text-sm text-sky-300 font-mono">
                {JSON.stringify(event.parameters, null, 2)}
              </pre>
            </div>
          </div>

          {/* Result (if allowed) */}
          {event.tool_result && (
            <div>
              <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-3">Tool Result</h3>
              <div className="bg-slate-950 rounded-lg p-4 border border-slate-800 overflow-x-auto">
                <pre className="text-sm text-emerald-300 font-mono">
                  {JSON.stringify(event.tool_result, null, 2)}
                </pre>
              </div>
            </div>
          )}

          {/* Metadata */}
          <div className="bg-slate-800/30 rounded-lg p-4 border border-slate-800 text-sm text-slate-400 flex flex-wrap gap-4">
            <div className="flex items-center gap-1.5">
              <Info size={16} className="text-slate-500"/>
              <strong>Event ID:</strong> <span className="font-mono">{event.event_id}</span>
            </div>
            <div className="flex items-center gap-1.5">
              <Clock size={16} className="text-slate-500"/>
              <strong>Session ID:</strong> <span className="font-mono">{event.session_id}</span>
            </div>
            <div className="flex items-center gap-1.5">
              <ShieldAlert size={16} className="text-slate-500"/>
              <strong>Policy V{event.policy_version}</strong>
            </div>
            <div className="flex items-center gap-1.5">
              <strong>Mode:</strong> 
              <span className={`px-2 py-0.5 rounded text-xs font-semibold ${
                event.mode === 'SHADOW' ? 'bg-amber-500/20 text-amber-400' : 'bg-indigo-500/20 text-indigo-400'
              }`}>
                {event.mode}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
