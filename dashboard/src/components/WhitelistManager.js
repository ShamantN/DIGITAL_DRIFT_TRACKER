// dashboard/src/components/WhitelistManager.js
import React, { useState, useEffect } from 'react';
import { getWhitelist, addToWhitelist, removeFromWhitelist } from '../services/api';
import './WhitelistManager.css';

export default function WhitelistManager() {
  const [whitelist, setWhitelist] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newDomain, setNewDomain] = useState('');
  const [newReason, setNewReason] = useState('');
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  useEffect(() => {
    loadWhitelist();
  }, []);

  const loadWhitelist = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await getWhitelist();
      setWhitelist(response.data.whitelist || []);
    } catch (err) {
      setError('Failed to load whitelist: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const handleAddDomain = async (e) => {
    e.preventDefault();
    if (!newDomain.trim()) {
      setError('Please enter a domain name');
      return;
    }

    setError(null);
    setSuccess(null);

    try {
      // Clean domain name (remove http://, https://, www., trailing slashes)
      let cleanDomain = newDomain.trim()
        .replace(/^https?:\/\//, '')
        .replace(/^www\./, '')
        .replace(/\/$/, '')
        .split('/')[0]; // Get just the domain part

      await addToWhitelist(cleanDomain, newReason.trim());
      setSuccess(`Domain "${cleanDomain}" added to whitelist successfully!`);
      setNewDomain('');
      setNewReason('');
      loadWhitelist(); // Reload the list
    } catch (err) {
      setError('Failed to add domain: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleRemoveDomain = async (domainId, domainName) => {
    if (!window.confirm(`Remove "${domainName}" from whitelist?`)) {
      return;
    }

    setError(null);
    setSuccess(null);

    try {
      await removeFromWhitelist(domainId);
      setSuccess(`Domain removed from whitelist successfully!`);
      loadWhitelist(); // Reload the list
    } catch (err) {
      setError('Failed to remove domain: ' + (err.response?.data?.detail || err.message));
    }
  };

  if (loading) {
    return <div className="whitelist-container">Loading whitelist...</div>;
  }

  return (
    <div className="whitelist-container">
      <div className="whitelist-header">
        <h2>Domain Whitelist Management</h2>
        <p className="whitelist-description">
          Domains in the whitelist are automatically marked as <strong>Productive</strong>.
          Domains you've visited but aren't whitelisted are marked as <strong>Unproductive</strong>.
          New domains are marked as <strong>Neutral</strong> until visited.
        </p>
      </div>

      {/* Add Domain Form */}
      <div className="whitelist-card">
        <h3>Add Domain to Whitelist</h3>
        <form onSubmit={handleAddDomain} className="whitelist-form">
          <div className="form-group">
            <label htmlFor="domain-name">Domain Name:</label>
            <input
              type="text"
              id="domain-name"
              value={newDomain}
              onChange={(e) => setNewDomain(e.target.value)}
              placeholder="e.g., github.com or stackoverflow.com"
              required
            />
            <small>Enter domain name (e.g., github.com). You can include http:// or www. - it will be cleaned automatically.</small>
          </div>
          
          <div className="form-group">
            <label htmlFor="domain-reason">Reason (Optional):</label>
            <input
              type="text"
              id="domain-reason"
              value={newReason}
              onChange={(e) => setNewReason(e.target.value)}
              placeholder="e.g., Work-related, Learning, etc."
            />
          </div>

          <button type="submit" className="btn-add">Add to Whitelist</button>
        </form>
      </div>

      {/* Messages */}
      {error && (
        <div className="message message-error">
          {error}
        </div>
      )}
      {success && (
        <div className="message message-success">
          {success}
        </div>
      )}

      {/* Whitelist Table */}
      <div className="whitelist-card">
        <h3>Whitelisted Domains ({whitelist.length})</h3>
        {whitelist.length === 0 ? (
          <p className="no-items">No domains in whitelist yet. Add domains above to mark them as productive.</p>
        ) : (
          <table className="whitelist-table">
            <thead>
              <tr>
                <th>Domain Name</th>
                <th>Category</th>
                <th>Reason</th>
                <th>Added</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {whitelist.map((item) => (
                <tr key={item.wid}>
                  <td><strong>{item.domain_name}</strong></td>
                  <td>
                    <span className="category-badge category-productive">{item.category || 'Productive'}</span>
                  </td>
                  <td>{item.user_reason || <em>No reason provided</em>}</td>
                  <td>{new Date(item.created_at).toLocaleDateString()}</td>
                  <td>
                    <button
                      className="btn-remove"
                      onClick={() => handleRemoveDomain(item.domain_id, item.domain_name)}
                    >
                      Remove
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}


