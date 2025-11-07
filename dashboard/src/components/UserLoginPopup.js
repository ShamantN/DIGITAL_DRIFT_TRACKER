// dashboard/src/components/UserLoginPopup.js
import React, { useState } from 'react';
import { login } from '../services/api';

export default function UserLoginPopup({ onLogin, onClose }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // Handle admin login
      let loginEmail = email;
      let loginPassword = password;
      
      if (email === 'admin' && password === 'admin123') {
        loginEmail = 'admin';
        loginPassword = 'admin123';
      }
      
      const response = await login(loginEmail, loginPassword);
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
      setError('Invalid credentials. Please try again.');
      console.error('Login failed:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-popup-overlay" onClick={onClose}>
      <div className="login-popup" onClick={(e) => e.stopPropagation()}>
        <div className="login-popup-header">
          <h3>User Login</h3>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>
        
        <form onSubmit={handleSubmit} className="login-popup-form">
          <div className="form-group">
            <label htmlFor="user-email">Email:</label>
            <input
              type="email"
              id="user-email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              placeholder="Enter your email"
              className="login-popup-input"
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="user-password">Password:</label>
            <input
              type="password"
              id="user-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              placeholder="Enter your password"
              className="login-popup-input"
            />
          </div>
          
          {error && <div className="login-popup-error">{error}</div>}
          
          <button type="submit" disabled={loading} className="login-popup-btn">
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>
        
        <div className="login-popup-footer">
          <p>Don't have an account? <a href="#" onClick={(e) => { e.preventDefault(); alert('Sign up functionality would be implemented here'); }}>Sign up</a></p>
        </div>
      </div>
    </div>
  );
}