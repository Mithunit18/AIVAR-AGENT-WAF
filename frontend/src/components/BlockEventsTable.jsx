import { AlertCircle, CheckCircle2 } from 'lucide-react';

export function BlockEventsTable({ events, onEventClick }) {
  return (
    <div className="glass-panel p-6 overflow-hidden flex flex-col h-[500px]">
      <h3 className="text-lg font-semibold text-slate-200 mb-4">Live Event Stream</h3>
      <div className="overflow-auto flex-1 pr-2">
        <table className="w-full text-sm text-left">
          <thead className="text-xs text-slate-400 uppercase bg-slate-800/80 sticky top-0">
            <tr>
              <th className="px-4 py-3 rounded-tl-lg">Time</th>
              <th className="px-4 py-3">Agent</th>
              <th className="px-4 py-3">Tool</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3 rounded-tr-lg">Reason</th>
            </tr>
          </thead>
          <tbody>
            {events.length === 0 ? (
              <tr>
                <td colSpan="5" className="px-4 py-8 text-center text-slate-500">
                  No events yet. Waiting for traffic...
                </td>
              </tr>
            ) : (
              events.map((event, index) => {
                const isBlocked = event.final_disposition === 'BLOCK';
                const failedRule = event.rule_evaluations?.find(r => r.status === 'FAIL');

                return (
                  <tr
                    key={index}
                    onClick={() => onEventClick && onEventClick(event)}
                    className="border-b border-slate-700/50 hover:bg-slate-700/60 transition-colors cursor-pointer"
                  >
                    <td className="px-4 py-3 text-slate-400 whitespace-nowrap">
                      {new Date(event.timestamp).toLocaleTimeString()}
                    </td>
                    <td className="px-4 py-3 font-medium text-slate-300">
                      {event.agent_id}
                    </td>
                    <td className="px-4 py-3 text-sky-400 font-mono text-xs">
                      {event.tool_name}
                    </td>
                    <td className="px-4 py-3">
                      {isBlocked ? (
                        <span className="flex items-center gap-1.5 text-red-400 bg-red-400/10 px-2 py-1 rounded-md w-fit">
                          <AlertCircle size={14} /> Blocked
                        </span>
                      ) : (
                        <span className="flex items-center gap-1.5 text-emerald-400 bg-emerald-400/10 px-2 py-1 rounded-md w-fit">
                          <CheckCircle2 size={14} /> Allowed
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-slate-400 text-xs">
                      {isBlocked && failedRule ? (
                        <span title={failedRule.reason} className="line-clamp-2">
                          <span className="font-semibold text-rose-300 mr-1">[{failedRule.rule}]</span>
                          {failedRule.reason}
                        </span>
                      ) : (
                        <span className="text-slate-600">-</span>
                      )}
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
