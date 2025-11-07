// dashboard/src/components/TopDomainsBarChart.js
import React, { useMemo } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function TopDomainsBarChart({ data }) {
  // Group and aggregate domain summaries
  const domainData = useMemo(() => {
    if (!data || data.length === 0) return [];

    const domainMap = {};
    
    data.forEach(item => {
      const domainName = item.domain_name || 'Unknown';
      if (!domainMap[domainName]) {
        domainMap[domainName] = {
          domain: domainName,
          totalMinutes: 0,
          category: item.category || 'Neutral',
          totalEvents: 0
        };
      }
      domainMap[domainName].totalMinutes += Math.round((item.total_seconds_focused || 0) / 60);
      domainMap[domainName].totalEvents += item.total_events || 0;
    });

    // Convert to array and sort by totalMinutes
    return Object.values(domainMap)
      .sort((a, b) => b.totalMinutes - a.totalMinutes)
      .slice(0, 10); // Top 10 domains
  }, [data]);

  if (domainData.length === 0) {
    return <p>No domain activity data available.</p>;
  }

  return (
    <div style={{ width: '100%', height: '400px' }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={domainData}
          layout="vertical"
          margin={{ top: 20, right: 30, left: 100, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis type="number" label={{ value: 'Minutes', position: 'insideBottom', offset: -5 }} />
          <YAxis 
            type="category" 
            dataKey="domain" 
            width={90}
            tick={{ fontSize: 12 }}
          />
          <Tooltip 
            formatter={(value, name) => {
              if (name === 'totalMinutes') return [`${value} minutes`, 'Time Spent'];
              return [value, 'Events'];
            }}
          />
          <Legend />
          <Bar dataKey="totalMinutes" fill="#3b82f6" name="Time (minutes)" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
