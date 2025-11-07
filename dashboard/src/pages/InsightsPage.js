// dashboard/src/pages/InsightsPage.js
import React, { useEffect, useState } from 'react';
import { getInsights } from '../services/api';
import UnclassifiedDomains from '../components/UnclassifiedDomains';
import SessionReport from '../components/SessionReport';
import DriftiestHour from '../components/DriftiestHour';
import StickiestDistractions from '../components/StickiestDistractions';

export default function InsightsPage({ userId = 1 }) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    getInsights(userId)
      .then(res => setData(res.data))
      .catch(err => setError(err.response?.data?.detail || err.message))
      .finally(() => setLoading(false));
  }, [userId]);

  if (loading) return <p>Loading insights...</p>;
  if (error) return <p style={{ color: '#d32f2f' }}>Failed to load insights: {error}</p>;

  return (
    <div className="dashboard-grid">
      <div className="dashboard-card">
        <h2>Unclassified Domains (Top 5)</h2>
        <UnclassifiedDomains items={data?.unclassified_domains || []} />
      </div>

      <div className="dashboard-card">
        <h2>Driftiest Hour</h2>
        <DriftiestHour items={data?.driftiest_hours || []} />
      </div>

      <div className="dashboard-card full-width">
        <h2>Session Report</h2>
        <div className="scroll-panel">
          <SessionReport items={data?.session_productivity || []} />
        </div>
      </div>

      <div className="dashboard-card">
        <h2>Stickiest Distractions</h2>
        <StickiestDistractions items={data?.stickiest_distractions || []} />
      </div>
    </div>
  );
}
