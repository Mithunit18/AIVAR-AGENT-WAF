import { useState, useEffect } from 'react';
import { dashboardApi } from '../api/dashboard';
import { EventDetailModal } from '../components/EventDetailModal';
import { RefreshCw, Filter, ChevronLeft, ChevronRight, ShieldAlert, CheckCircle, Shield } from 'lucide-react';

export default function EventsView({ showToast }) {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedEvent, setSelectedEvent] = useState(null);

  // Pagination & Filters
  const [skip, setSkip] = useState(0);
  const [limit] = useState(25);
  const [hasMore, setHasMore] = useState(true);
  const [filters, setFilters] = useState({
    decision: '',
    agent_id: '',
    tool_name: ''
  });

  const fetchEvents = async (reset = false) => {
    setLoading(true);
    try {
      const currentSkip = reset ? 0 : skip;
      const data = await dashboardApi.getEvents({
        skip: currentSkip,
        limit,
        ...filters
      });

      setEvents(data.events || []);
      setHasMore((data.events || []).length === limit);
      if (reset) setSkip(0);
    } catch (err) {
      showToast("Failed to fetch events", "error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEvents(true);
  }, [filters]); // Re-fetch on filter change

  const handleNext = () => {
    if (hasMore) {
      setSkip(s => s + limit);
    }
  };

  const handlePrev = () => {
    if (skip > 0) {
      setSkip(s => Math.max(0, s - limit));
    }
  };

  useEffect(() => {
    // Only fetch if it's not the initial mount since filters effect runs on mount
    if (skip > 0 || !hasMore) {
      fetchEvents();
    }
  }, [skip]);

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters(f => ({ ...f, [name]: value }));
  };

  return (
    <div className="flex flex-col gap-6 animate-in fade-in duration-300">
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-sm">

        {/* Toolbar */}
        <div className="p-4 border-b border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-2 text-slate-300 font-semibold">
            <Filter size={18} className="text-slate-500" />
            Historical Events
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <select
              name="decision"
              value={filters.decision}
              onChange={handleFilterChange}
              className="bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-sm text-slate-300 focus:outline-none focus:border-indigo-500"
            >
              <option value="">All Decisions</option>
              <option value="ALLOW">ALLOW</option>
              <option value="BLOCK">BLOCK</option>
            </select>

            <input
              type="text"
              name="agent_id"
              value={filters.agent_id}
              onChange={handleFilterChange}
              placeholder="Filter by Agent ID"
              className="bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-sm text-slate-300 focus:outline-none focus:border-indigo-500"
            />

            <input
              type="text"
              name="tool_name"
              value={filters.tool_name}
              onChange={handleFilterChange}
              placeholder="Filter by Tool"
              className="bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-sm text-slate-300 focus:outline-none focus:border-indigo-500"
            />

            <button
              onClick={() => fetchEvents(true)}
              className="p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-slate-200 rounded-md transition-colors"
              title="Refresh"
            >
              <RefreshCw size={16} className={loading ? "animate-spin" : ""} />
            </button>
          </div>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-950/50 text-xs uppercase text-slate-500 border-b border-slate-800">
              <tr>
                <th className="px-6 py-3 font-semibold">Time</th>
                <th className="px-6 py-3 font-semibold">Agent ID</th>
                <th className="px-6 py-3 font-semibold">Tool</th>
                <th className="px-6 py-3 font-semibold">Decision</th>
                <th className="px-6 py-3 font-semibold">Rule/Mode</th>
                <th className="px-6 py-3 font-semibold text-right">Latency</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50">
              {loading && events.length === 0 ? (
                <tr>
                  <td colSpan="6" className="px-6 py-8 text-center text-slate-500">
                    <RefreshCw className="animate-spin mx-auto mb-2 opacity-50" size={24} />
                    Loading events...
                  </td>
                </tr>
              ) : events.length === 0 ? (
                <tr>
                  <td colSpan="6" className="px-6 py-8 text-center text-slate-500">
                    No events found matching filters.
                  </td>
                </tr>
              ) : (
                events.map((event) => (
                  <tr
                    key={event.event_id}
                    onClick={() => setSelectedEvent(event)}
                    className="hover:bg-slate-800/50 cursor-pointer transition-colors"
                  >
                    <td className="px-6 py-3 whitespace-nowrap">
                      {new Date(event.timestamp).toLocaleTimeString([], { hour12: false })}
                    </td>
                    <td className="px-6 py-3 font-mono text-sky-400 text-xs">
                      {event.agent_id}
                    </td>
                    <td className="px-6 py-3 font-semibold">
                      {event.tool_name}
                    </td>
                    <td className="px-6 py-3">
                      {event.final_disposition === 'ALLOW' ? (
                        <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-xs font-medium bg-emerald-500/10 text-emerald-400">
                          <CheckCircle size={12} /> ALLOW
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-xs font-medium bg-rose-500/10 text-rose-400">
                          <ShieldAlert size={12} /> BLOCK
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-3">
                      {event.mode === 'SHADOW' ? (
                        <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-xs font-medium bg-amber-500/10 text-amber-400">
                          SHADOW
                        </span>
                      ) : event.final_disposition === 'BLOCK' && event.rule_evaluations ? (
                        <span className="text-rose-400 text-xs capitalize">
                          {event.rule_evaluations.find(r => r.status === 'FAIL')?.rule.replace('_', ' ') || 'Unknown'}
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1.5 text-slate-500 text-xs">
                          <Shield size={12} /> ACTIVE
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-3 text-right text-slate-400 font-mono text-xs">
                      {event.latency_ms}ms
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Footer */}
        <div className="p-4 border-t border-slate-800 flex items-center justify-between text-sm text-slate-400">
          <div>
            Showing {events.length > 0 ? skip + 1 : 0} to {skip + events.length}
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={handlePrev}
              disabled={skip === 0 || loading}
              className="p-1.5 bg-slate-800 hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-md transition-colors text-slate-300"
            >
              <ChevronLeft size={18} />
            </button>
            <button
              onClick={handleNext}
              disabled={!hasMore || loading}
              className="p-1.5 bg-slate-800 hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-md transition-colors text-slate-300"
            >
              <ChevronRight size={18} />
            </button>
          </div>
        </div>
      </div>

      {selectedEvent && (
        <EventDetailModal event={selectedEvent} onClose={() => setSelectedEvent(null)} />
      )}
    </div>
  );
}
