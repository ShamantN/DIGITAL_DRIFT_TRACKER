// dashboard/src/components/DriftTimeline.js
import React, { useMemo } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function DriftTimeline({ data }) {
  // Group drifts by day and type
  const timelineData = useMemo(() => {
    if (!data || data.length === 0) return { data: [], types: [] };

    const dayMap = {};
    const driftTypes = new Set();

    data.forEach(drift => {
      const date = new Date(drift.event_start);
      const dayKey = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
      
      if (!dayMap[dayKey]) {
        dayMap[dayKey] = { date: dayKey, timestamp: date.getTime() };
      }

      const type = drift.drift_type || 'Unknown';
      driftTypes.add(type);

      // Count drifts and sum duration per type per day
      const countKey = `${type}_count`;
      const durationKey = `${type}_duration`;

      dayMap[dayKey][countKey] = (dayMap[dayKey][countKey] || 0) + 1;
      dayMap[dayKey][durationKey] = (dayMap[dayKey][durationKey] || 0) + (drift.duration_seconds || 0);
    });

    // Convert to array and sort by timestamp
    const result = Object.values(dayMap).sort((a, b) => a.timestamp - b.timestamp);
    return { data: result, types: Array.from(driftTypes) };
  }, [data]);

  if (!timelineData || timelineData.data.length === 0) {
    return <p>No drift events to display on timeline.</p>;
  }

  // Color palette for different drift types
  const colors = ['#ef4444', '#f59e0b', '#8b5cf6', '#ec4899', '#10b981', '#06b6d4'];
  const getColor = (index) => colors[index % colors.length];

  return (
    <div style={{ width: '100%', height: '400px' }}>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart
          data={timelineData.data}
          margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
        >
          <defs>
            {timelineData.types.map((type, index) => (
              <linearGradient key={type} id={`color${index}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={getColor(index)} stopOpacity={0.8}/>
                <stop offset="95%" stopColor={getColor(index)} stopOpacity={0.1}/>
              </linearGradient>
            ))}
          </defs>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis label={{ value: 'Number of Drifts', angle: -90, position: 'insideLeft' }} />
          <Tooltip />
          <Legend />
          {timelineData.types.map((type, index) => (
            <Area
              key={type}
              type="monotone"
              dataKey={`${type}_count`}
              stroke={getColor(index)}
              fill={`url(#color${index})`}
              name={type}
            />
          ))}
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
