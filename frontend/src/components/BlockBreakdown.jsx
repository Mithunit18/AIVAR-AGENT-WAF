import { useMemo } from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import { ShieldX } from 'lucide-react';

const COLORS = {
  'rate_limit': '#8b5cf6', // purple
  'parameter_validation': '#f43f5e', // rose
  'data_scope': '#06b6d4', // cyan
  'sequence': '#f59e0b', // amber
};

const LABELS = {
  'rate_limit': 'Rate Limit',
  'parameter_validation': 'Param Validation',
  'data_scope': 'Data Scope',
  'sequence': 'Sequence Rule',
};

export function BlockBreakdown({ stats }) {
  const data = useMemo(() => {
    if (!stats?.by_rule) return [];
    return Object.entries(stats.by_rule).map(([rule, count]) => ({
      name: LABELS[rule] || rule,
      ruleKey: rule,
      value: count
    })).sort((a, b) => b.value - a.value);
  }, [stats]);

  if (data.length === 0) {
    return (
      <div className="glass-panel p-6 flex flex-col items-center justify-center h-full text-slate-500 gap-3 min-h-[300px]">
        <ShieldX size={48} className="opacity-50" />
        <p>No block events recorded yet</p>
      </div>
    );
  }

  return (
    <div className="glass-panel p-6 h-full flex flex-col min-h-[300px]">
      <h3 className="text-lg font-semibold text-slate-200 mb-4">Block Reasons Breakdown</h3>
      <div className="flex-1 relative">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={80}
              paddingAngle={5}
              dataKey="value"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[entry.ruleKey] || '#64748b'} />
              ))}
            </Pie>
            <Tooltip 
              contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', borderRadius: '0.5rem' }}
              itemStyle={{ color: '#e2e8f0' }}
            />
            <Legend 
              verticalAlign="bottom" 
              height={36} 
              formatter={(value) => <span className="text-slate-300 text-xs ml-1">{value}</span>}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
