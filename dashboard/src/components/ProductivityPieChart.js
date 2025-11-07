// dashboard/src/components/ProductivityPieChart.js
import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

const COLORS = {
  'Productive': '#10b981',
  'Unproductive': '#ef4444',
  'Neutral': '#6b7280',
  'Social Media': '#f59e0b',
  'Entertainment': '#8b5cf6'
};

export default function ProductivityPieChart({ data }) {
  if (!data || data.length === 0) {
    return <p>No category data available.</p>;
  }

  // Transform data for the chart
  const chartData = data.map(item => ({
    name: item.category || 'Unknown',
    value: Math.round(item.total_seconds / 60), // Convert to minutes
    seconds: item.total_seconds
  }));

  // Sort by value descending
  chartData.sort((a, b) => b.value - a.value);

  return (
    <div style={{ width: '100%', height: '400px' }}>
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
            outerRadius={120}
            fill="#8884d8"
            dataKey="value"
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[entry.name] || '#94a3b8'} />
            ))}
          </Pie>
          <Tooltip 
            formatter={(value, name) => [`${value} minutes`, 'Time']}
          />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
