// dashboard/src/components/DriftiestHour.js
import React from 'react';

export default function DriftiestHour({ items }) {
  if (!items || items.length === 0) {
    return <p>No drift activity recorded yet.</p>;
  }

  return (
    <table width="100%">
      <thead>
        <tr>
          <th>Hour</th>
          <th>Total Drifts</th>
          <th>Most Common Type</th>
        </tr>
      </thead>
      <tbody>
        {items.map((row, idx) => (
          <tr key={idx}>
            <td>{String(row.drift_hour).padStart(2, '0')}:00</td>
            <td>{row.total_drifts}</td>
            <td>{row.most_common_drift_type}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
