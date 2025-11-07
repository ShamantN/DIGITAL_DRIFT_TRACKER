// dashboard/src/components/StickiestDistractions.js
import React from 'react';

export default function StickiestDistractions({ items }) {
  if (!items || items.length === 0) {
    return <p>No unproductive domains with measurable stickiness.</p>;
  }

  return (
    <table width="100%">
      <thead>
        <tr>
          <th>Domain</th>
          <th>Avg Focus (min)</th>
        </tr>
      </thead>
      <tbody>
        {items.map((row, idx) => (
          <tr key={idx}>
            <td>{row.domain_name}</td>
            <td>{(row.avg_duration_seconds / 60).toFixed(1)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
