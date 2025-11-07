// dashboard/src/components/AdminLoginPopup.js
import React, { useState } from 'react';
import { login } from '../services/api';
import './LoginPopup.css';

export default function AdminLoginPopup({ onClose, onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // Handle admin login
      let loginUsername = username;
      let loginPassword = password;
      
      if (username === 'admin' && password === 'admin123') {
        loginUsername = 'admin';
        loginPassword = 'admin123';
      }
      
      const response = await login(loginUsername, loginPassword);
      const { access_token, user_id, email: userEmail } = response.data;
      
      // Store token
      localStorage.setItem('auth_token', access_token);
      
      // Decode token to get role
      const payload = JSON.parse(atob(access_token.split('.')[1]));
      
      // Call parent callback
      onLogin({
        user_id,
        email: userEmail,
        role: payload.role || 'user'
      });
      
      // Close popup
      onClose();
      
    } catch (err) {
      setError('Invalid admin credentials. Please try again.');
      console.error('Admin login failed:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleOverlayClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div className="login-popup-overlay" onClick={handleOverlayClick}>
      <div className="login-popup">
        <div className="login-popup-header">
          <h2>Admin Login</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="admin-username">Username:</label>
            <input
              type="text"
              id="admin-username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              placeholder="Enter username 'admin'"
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="admin-password">Password:</label>
            <input
              type="password"
              id="admin-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              placeholder="Enter password 'admin123'"
            />
          </div>
          
          {error && <div className="error-message">{error}</div>}
          
          <button type="submit" disabled={loading} className="login-btn">
            {loading ? 'Logging in...' : 'Admin Login'}
          </button>
        </form>
        
        <div className="login-hint">
          <p><strong>Admin Credentials:</strong> Username: admin, Password: admin123</p>
        </div>
      </div>
    </div>
  );
}