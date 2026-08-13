import { useState, useEffect } from 'react';
import { CheckCircle, AlertTriangle, XCircle } from 'lucide-react';
import { healthApi } from '../api/health';

export function SystemStatus() {
  const [status, setStatus] = useState('loading'); // loading, ok, degraded, down

  useEffect(() => {
    let mounted = true;

    const checkHealth = async () => {
      try {
        await healthApi.getReady();
        if (mounted) setStatus('ok');
      } catch (err) {
        if (mounted) setStatus('degraded');
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 30000); // check every 30s
    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, []);

  if (status === 'loading') {
    return (
      <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-slate-800/50 border border-slate-700 text-xs text-slate-400">
        <span className="w-2 h-2 rounded-full bg-slate-500 animate-pulse"></span>
        Checking System...
      </div>
    );
  }

  if (status === 'ok') {
    return (
      <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-xs text-emerald-400 font-medium">
        <span className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.8)]"></span>
        System Operational
      </div>
    );
  }

  return (
    <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-rose-500/10 border border-rose-500/20 text-xs text-rose-400 font-medium">
      <span className="w-2 h-2 rounded-full bg-rose-500 shadow-[0_0_8px_rgba(244,63,94,0.8)]"></span>
      System Degraded
    </div>
  );
}
