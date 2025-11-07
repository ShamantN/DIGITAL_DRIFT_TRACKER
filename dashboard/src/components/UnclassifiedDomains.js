// dashboard/src/components/UnclassifiedDomains.js
import React from 'react';

export default function UnclassifiedDomains({ items }) {
  if (!items || items.length === 0) {
    return <p>No high-activity unclassified domains in the last 30 days.</p>;
  }

  return (
    <table width="100%">
      <thead>
        <tr>
          <th>Domain</th>
          <th>Total Time (min)</th>
        </tr>
      </thead>
      <tbody>
        {items.map((row, idx) => (
          <tr key={idx}>
            <td>{row.domain_name}</td>
            <td>{Math.round((row.total_time_seconds || 0) / 60)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
