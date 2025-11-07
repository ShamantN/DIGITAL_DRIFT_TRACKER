// dashboard/src/pages/AdminDashboard.js
import React, { useState, useEffect } from 'react';
import { getAdminStats, getAdminUsers, deleteUser } from '../services/api';
import './AdminDashboard.css';

export default function AdminDashboard() {
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [deleteConfirm, setDeleteConfirm] = useState(null);
  const [deleteLoading, setDeleteLoading] = useState(false);

  useEffect(() => {
    loadAdminData();
  }, []);

  const loadAdminData = async () => {
    try {
      setLoading(true);
      const [statsResponse, usersResponse] = await Promise.all([
        getAdminStats(),
        getAdminUsers()
      ]);
      
      setStats(statsResponse.data);
      setUsers(usersResponse.data.users);
      setError(null);
    } catch (err) {
      console.error('Failed to load admin data:', err);
      setError('Failed to load admin data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteUser = async (userId, userEmail) => {
    setDeleteConfirm({ userId, userEmail });
  };

  const confirmDelete = async () => {
    if (!deleteConfirm) return;
    
    setDeleteLoading(true);
    try {
      await deleteUser(deleteConfirm.userId);
      // Remove the deleted user from the local state
      setUsers(users.filter(user => user.id !== deleteConfirm.userId));
      setDeleteConfirm(null);
      setDeleteLoading(false);
    } catch (err) {
      console.error('Error deleting user:', err);
      alert('Failed to delete user. Please try again.');
      setDeleteLoading(false);
    }
  };

  const cancelDelete = () => {
    setDeleteConfirm(null);
  };

  const formatDuration = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    }
    return `${minutes}m`;
  };

  if (loading) {
    return (
      <div className="admin-dashboard">
        <div className="loading">
          <h2>Loading Admin Dashboard...</h2>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="admin-dashboard">
        <div className="error">
          <h2>Error</h2>
          <p>{error}</p>
          <button onClick={loadAdminData}>Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div className="admin-dashboard">
      <div className="admin-header">
        <h1>Admin Dashboard</h1>
        <p>System-wide Digital Drift Tracker Statistics</p>
      </div>

      {/* Statistics Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <h3>Total Users</h3>
          <div className="stat-value">{stats?.total_users || 0}</div>
        </div>
        
        <div className="stat-card">
          <h3>Active Users (30 days)</h3>
          <div className="stat-value">{stats?.active_users || 0}</div>
        </div>
        
        <div className="stat-card">
          <h3>Total Sessions</h3>
          <div className="stat-value">{stats?.total_sessions || 0}</div>
        </div>
        
        <div className="stat-card">
          <h3>Total Drift Events</h3>
          <div className="stat-value">{stats?.total_drifts || 0}</div>
        </div>
        
        <div className="stat-card">
          <h3>Avg Session Duration</h3>
          <div className="stat-value">{stats?.avg_session_duration_minutes || 0} min</div>
        </div>
      </div>

      {/* Top Domains */}
      {stats?.top_domains && stats.top_domains.length > 0 && (
        <div className="admin-section">
          <h2>Top Domains (All Users)</h2>
          <div className="top-domains-table">
            <table>
              <thead>
                <tr>
                  <th>Domain</th>
                  <th>Category</th>
                  <th>Total Time</th>
                </tr>
              </thead>
              <tbody>
                {stats.top_domains.map((domain, index) => (
                  <tr key={index}>
                    <td>{domain.domain}</td>
                    <td><span className={`category-badge ${domain.category.toLowerCase()}`}>{domain.category}</span></td>
                    <td>{formatDuration(domain.total_seconds)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Users List */}
      <div className="admin-section">
        <h2>All Users</h2>
        <div className="users-table">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Email</th>
                <th>Joined</th>
                <th>Sessions</th>
                <th>Drift Events</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user) => (
                <tr key={user.id}>
                  <td>{user.id}</td>
                  <td>{user.email}</td>
                  <td>{new Date(user.created_at).toLocaleDateString()}</td>
                  <td>{user.session_count}</td>
                  <td>{user.drift_count}</td>
                  <td>
                    <button 
                      onClick={() => handleDeleteUser(user.id, user.email)}
                      className="delete-user-btn"
                      disabled={deleteLoading}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Delete Confirmation Modal */}
      {deleteConfirm && (
        <div className="delete-confirm-modal">
          <div className="delete-confirm-content">
            <h3>Confirm User Deletion</h3>
            <p>Are you sure you want to delete the user <strong>{deleteConfirm.userEmail}</strong>?</p>
            <p>This action cannot be undone and will delete all associated data.</p>
            <div className="delete-confirm-buttons">
              <button 
                onClick={cancelDelete} 
                className="cancel-btn"
                disabled={deleteLoading}
              >
                Cancel
              </button>
              <button 
                onClick={confirmDelete} 
                className="confirm-delete-btn"
                disabled={deleteLoading}
              >
                {deleteLoading ? 'Deleting...' : 'Delete User'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}