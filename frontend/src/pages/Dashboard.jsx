import { useState, useEffect, useRef } from 'react';
import { dashboardApi } from '../api/dashboard';
import { TrafficChart } from '../components/TrafficChart';
import { BlockBreakdown } from '../components/BlockBreakdown';
import { BlockEventsTable } from '../components/BlockEventsTable';
import { EventDetailModal } from '../components/EventDetailModal';

export default function DashboardView({ sseEvents, setSseEvents, showToast }) {
  const [stats, setStats] = useState({ total: 0, blocked: 0, allowed: 0, block_rate: 0, by_rule: {} });
  const [selectedEvent, setSelectedEvent] = useState(null);
  const initialFetchDone = useRef(false);

  useEffect(() => {
    if (initialFetchDone.current) return;
    initialFetchDone.current = true;
    
    // Fetch initial summary from backend
    dashboardApi.getSummary()
      .then(data => setStats(data))
      .catch(err => showToast("Failed to fetch dashboard summary", "error"));
      
    // Fetch initial events stream seed
    dashboardApi.getEvents({ limit: 50 })
      .then(data => {
        if (data.events && Array.isArray(data.events)) {
          setSseEvents(data.events);
        }
      })
      .catch(err => showToast("Failed to fetch initial events", "error"));
  }, [setSseEvents, showToast]);

  // Update stats incrementally when new SSE events arrive to save API calls
  useEffect(() => {
    if (sseEvents.length > 0 && stats.total > 0) {
      // Recompute slightly based on active local feed
      const total = sseEvents.length;
      const blocked = sseEvents.filter(e => e.final_disposition === 'BLOCK').length;
      
      const by_rule = {};
      sseEvents.forEach(e => {
        if (e.final_disposition === 'BLOCK' && e.rule_evaluations) {
          const failedRule = e.rule_evaluations.find(r => r.status === 'FAIL');
          if (failedRule) {
            by_rule[failedRule.rule] = (by_rule[failedRule.rule] || 0) + 1;
          }
        }
      });

      // Prefer real backend numbers but merge real-time if backend data is stale
      setStats(prev => ({ 
        ...prev,
        total: Math.max(prev.total, total), 
        blocked: Math.max(prev.blocked, blocked), 
        allowed: Math.max(prev.allowed, total - blocked), 
        block_rate: prev.total > 0 ? ((prev.blocked/prev.total)*100).toFixed(1) : 0,
        by_rule: Object.keys(by_rule).length > 0 ? by_rule : prev.by_rule 
      }));
    }
  }, [sseEvents]);

  return (
    <div className="flex flex-col gap-6 animate-in fade-in duration-300">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-slate-900 border border-slate-800 shadow-sm rounded-xl p-6 flex flex-col gap-2">
          <span className="text-slate-400 text-xs font-semibold uppercase tracking-wider">Total Calls</span>
          <span className="text-3xl font-bold text-slate-100">{stats.total}</span>
        </div>
        <div className="bg-emerald-950/30 border border-emerald-900/50 shadow-sm rounded-xl p-6 flex flex-col gap-2">
          <span className="text-emerald-400/80 text-xs font-semibold uppercase tracking-wider">Allowed</span>
          <span className="text-3xl font-bold text-emerald-400">{stats.allowed}</span>
        </div>
        <div className="bg-rose-950/30 border border-rose-900/50 shadow-sm rounded-xl p-6 flex flex-col gap-2">
          <span className="text-rose-400/80 text-xs font-semibold uppercase tracking-wider">Blocked</span>
          <span className="text-3xl font-bold text-rose-500">{stats.blocked}</span>
        </div>
        <div className="bg-amber-950/30 border border-amber-900/50 shadow-sm rounded-xl p-6 flex flex-col gap-2">
          <span className="text-amber-400/80 text-xs font-semibold uppercase tracking-wider">Block Rate</span>
          <span className="text-3xl font-bold text-amber-500">{stats.block_rate}%</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
          <div className="p-4 border-b border-slate-800">
            <h3 className="text-sm font-semibold text-slate-300">Traffic Overview</h3>
          </div>
          <div className="p-4">
            <TrafficChart events={sseEvents} />
          </div>
        </div>
        <div className="lg:col-span-1 bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
          <div className="p-4 border-b border-slate-800">
            <h3 className="text-sm font-semibold text-slate-300">Block Reasons</h3>
          </div>
          <div className="p-4">
            <BlockBreakdown stats={stats} />
          </div>
        </div>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
        <div className="p-4 border-b border-slate-800">
          <h3 className="text-sm font-semibold text-slate-300 flex items-center gap-2">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-rose-500"></span>
            </span>
            Live Event Stream
          </h3>
        </div>
        <BlockEventsTable events={sseEvents} onEventClick={(e) => setSelectedEvent(e)} />
      </div>

      {selectedEvent && (
        <EventDetailModal event={selectedEvent} onClose={() => setSelectedEvent(null)} />
      )}
    </div>
  );
}
