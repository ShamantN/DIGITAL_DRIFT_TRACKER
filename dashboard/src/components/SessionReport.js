// dashboard/src/components/SessionReport.js
import React from 'react';

export default function SessionReport({ items }) {
  if (!items || items.length === 0) {
    return <p>No completed sessions to report.</p>;
  }

  return (
    <table width="100%">
      <thead>
        <tr>
          <th>Session</th>
          <th>Start</th>
          <th>Duration (min)</th>
          <th>Tab Switches</th>
          <th>Productive (min)</th>
        </tr>
      </thead>
      <tbody>
        {items.map((s) => (
          <tr key={s.sid}>
            <td>{s.sid}</td>
            <td>{new Date(s.start_time).toLocaleString()}</td>
            <td>{s.total_minutes}</td>
            <td>{s.tab_switches}</td>
            <td>{Math.round((s.productive_seconds || 0) / 60)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
