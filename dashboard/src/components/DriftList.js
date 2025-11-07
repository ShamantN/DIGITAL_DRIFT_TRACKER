// dashboard/src/components/DriftList.js
import React from 'react';

export default function DriftList({ data }) {
  if (!data || data.length === 0) {
    return <p>No drift events found for this period.</p>;
  }

  return (
    <div>
      <table width="100%">
        <thead>
          <tr>
            <th>Type</th>
            <th>Description</th>
            <th>Duration (min)</th>
            <th>Severity</th>
            <th>When</th>
          </tr>
        </thead>
        <tbody>
          {data.map((drift, index) => (
            <tr key={index}>
              <td>{drift.drift_type}</td>
              <td>{drift.description}</td>
              <td>{Math.round(drift.duration_seconds / 60)}</td>
              <td>{drift.severity}</td>
              <td>{new Date(drift.event_start).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}