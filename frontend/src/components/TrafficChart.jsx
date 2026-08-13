import { useMemo } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export function TrafficChart({ events }) {
  // Aggregate events by minute
  const chartData = useMemo(() => {
    const timeMap = new Map();

    // Initialize last 30 minutes with 0
    const now = new Date();
    for (let i = 29; i >= 0; i--) {
      const d = new Date(now.getTime() - i * 60000);
      const timeKey = d.toISOString().substring(11, 16); // HH:mm
      timeMap.set(timeKey, { time: timeKey, allow: 0, block: 0 });
    }

    // Fill with actual data
    events.forEach(event => {
      const timeKey = new Date(event.timestamp).toISOString().substring(11, 16);
      if (timeMap.has(timeKey)) {
        const current = timeMap.get(timeKey);
        if (event.final_disposition === 'ALLOW') {
          current.allow += 1;
        } else {
          current.block += 1;
        }
      }
    });

    return Array.from(timeMap.values());
  }, [events]);

  return (
    <div className="glass-panel p-6 h-96">
      <h3 className="text-lg font-semibold text-slate-200 mb-4">Traffic Overview</h3>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="colorAllow" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="colorBlock" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
            </linearGradient>
          </defs>
          <XAxis dataKey="time" stroke="#64748b" fontSize={12} tickMargin={10} />
          <YAxis stroke="#64748b" fontSize={12} tickMargin={10} />
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
          <Tooltip
            contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', borderRadius: '0.5rem' }}
            itemStyle={{ fontSize: '14px' }}
          />
          <Area type="monotone" dataKey="allow" stroke="#10b981" fillOpacity={1} fill="url(#colorAllow)" name="Allowed" />
          <Area type="monotone" dataKey="block" stroke="#ef4444" fillOpacity={1} fill="url(#colorBlock)" name="Blocked" />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
