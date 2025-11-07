// dashboard/src/components/DomainActivityChart.js
import React, { useMemo } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function DomainActivityChart({ data }) {
  // Group domain summaries by date and domain
  const chartData = useMemo(() => {
    if (!data || data.length === 0) return { data: [], domains: [] };

    const dateMap = {};
    const domainSet = new Set();

    data.forEach(item => {
      const dateStr = item.summary_date || new Date().toISOString().split('T')[0];
      const date = new Date(dateStr);
      const dayKey = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
      
      if (!dateMap[dayKey]) {
        dateMap[dayKey] = { date: dayKey, timestamp: date.getTime() };
      }

      const domainName = item.domain_name || 'Unknown';
      domainSet.add(domainName);

      const minutes = Math.round((item.total_seconds_focused || 0) / 60);
      dateMap[dayKey][domainName] = (dateMap[dayKey][domainName] || 0) + minutes;
    });

    // Convert to array and sort by timestamp
    const result = Object.values(dateMap).sort((a, b) => a.timestamp - b.timestamp);
    
    // Get top 5 domains by total time
    const domainTotals = {};
    result.forEach(day => {
      Object.keys(day).forEach(key => {
        if (key !== 'date' && key !== 'timestamp') {
          domainTotals[key] = (domainTotals[key] || 0) + (day[key] || 0);
        }
      });
    });

    const topDomains = Object.entries(domainTotals)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5)
      .map(([domain]) => domain);

    return { data: result, domains: topDomains };
  }, [data]);

  if (chartData.data.length === 0) {
    return <p>No domain activity data available.</p>;
  }

  // Color palette for different domains
  const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];
  const getColor = (index) => colors[index % colors.length];

  return (
    <div style={{ width: '100%', height: '400px' }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          data={chartData.data}
          margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis label={{ value: 'Minutes', angle: -90, position: 'insideLeft' }} />
          <Tooltip formatter={(value) => [`${value} minutes`, 'Time']} />
          <Legend />
          {chartData.domains.map((domain, index) => (
            <Line
              key={domain}
              type="monotone"
              dataKey={domain}
              stroke={getColor(index)}
              strokeWidth={2}
              dot={{ r: 3 }}
              activeDot={{ r: 5 }}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
