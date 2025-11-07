// dashboard/src/components/LoginForm.js
import React, { useState } from 'react';
import { login } from '../services/api';

export default function LoginForm({ onLogin }) {
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
      
    } catch (err) {
      setError('Invalid credentials. Please try again.');
      console.error('Login failed:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-form">
      <h2>Login</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="email">Email:</label>
          <input
            type="text"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            placeholder="Enter email or 'admin'"
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="password">Password:</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            placeholder="Enter password or 'admin123'"
          />
        </div>
        
        {error && <div className="error-message">{error}</div>}
        
        <button type="submit" disabled={loading} className="login-btn">
          {loading ? 'Logging in...' : 'Login'}
        </button>
      </form>
      
      <div className="login-hint">
        <p><strong>Admin Login:</strong> Use username 'admin' and password 'admin123'</p>
      </div>
    </div>
  );
}