import { useState, useEffect } from 'react';
import { useSSE } from './hooks/useSSE';
import { SystemStatus } from './components/SystemStatus';
import { Toast } from './components/Toast';
import { dashboardApi } from './api/dashboard';
import { API_BASE_URL } from './api/client';
import { Shield, Activity, LayoutDashboard, Settings, List } from 'lucide-react';

// Lazy loading views conceptually via simple tabs
import DashboardView from './pages/Dashboard';
import EventsView from './pages/Events';
import PoliciesView from './pages/Policies';

export default function App() {
  const { events: sseEvents, isConnected, setEvents: setSseEvents } = useSSE(`${API_BASE_URL}/api/v1/dashboard/stream`);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [toast, setToast] = useState(null);

  const showToast = (message, type = 'info') => {
    setToast({ message, type });
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200 p-6 md:p-8 flex flex-col gap-8 max-w-[1600px] mx-auto">
      {/* Header */}
      <header className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="p-3 bg-indigo-500/20 rounded-xl border border-indigo-500/30 text-indigo-400">
            <Shield size={28} />
          </div>
          <div>
            <h1 className="text-2xl font-bold bg-gradient-to-r from-indigo-400 to-cyan-400 bg-clip-text text-transparent">
              Agent WAF Console
            </h1>
            <p className="text-sm text-slate-400">Real-time AI Security & Observability</p>
          </div>
        </div>

        <div className="flex flex-col sm:flex-row items-center gap-4">
          {/* Main Navigation Tabs */}
          <div className="flex bg-slate-900 p-1 rounded-lg border border-slate-800 shadow-sm">
            <button
              onClick={() => setActiveTab('dashboard')}
              className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all ${activeTab === 'dashboard' ? 'bg-slate-800 text-sky-400 shadow-sm' : 'text-slate-400 hover:text-slate-200'}`}
            >
              <LayoutDashboard size={16} /> Dashboard
            </button>
            <button
              onClick={() => setActiveTab('events')}
              className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all ${activeTab === 'events' ? 'bg-slate-800 text-sky-400 shadow-sm' : 'text-slate-400 hover:text-slate-200'}`}
            >
              <List size={16} /> Events
            </button>
            <button
              onClick={() => setActiveTab('policies')}
              className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all ${activeTab === 'policies' ? 'bg-slate-800 text-sky-400 shadow-sm' : 'text-slate-400 hover:text-slate-200'}`}
            >
              <Settings size={16} /> Policies
            </button>
          </div>

          {/* Status Indicators */}
          <div className="flex items-center gap-3">
            <SystemStatus />
            <div className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full border text-xs font-medium transition-colors ${isConnected ? "bg-indigo-500/10 border-indigo-500/20 text-indigo-400" : "bg-slate-800/50 border-slate-700 text-slate-400"}`}>
              <Activity size={14} className={isConnected ? "animate-pulse" : ""} />
              {isConnected ? "Live" : "Reconnecting..."}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1">
        {activeTab === 'dashboard' && <DashboardView sseEvents={sseEvents} setSseEvents={setSseEvents} showToast={showToast} />}
        {activeTab === 'events' && <EventsView showToast={showToast} />}
        {activeTab === 'policies' && <PoliciesView showToast={showToast} />}
      </main>

      {/* Global Notifications */}
      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}
    </div>
  );
}
