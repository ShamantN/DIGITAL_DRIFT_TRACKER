// dashboard/src/App.js
import React, { useState, useEffect } from 'react';
import { getAnalytics } from './services/api';
import ProductivityPieChart from './components/ProductivityPieChart';
import TopDomainsBarChart from './components/TopDomainsBarChart';
import DriftTimeline from './components/DriftTimeline';
import DomainActivityChart from './components/DomainActivityChart';
import DriftList from './components/DriftList';
import WhitelistManager from './components/WhitelistManager';
import InsightsPage from './pages/InsightsPage';
import AdminDashboard from './pages/AdminDashboard';
import UserLoginPopup from './components/UserLoginPopup';
import AdminLoginPopup from './components/AdminLoginPopup';
import './App.css';
import './components/LoginForm.css';
import './components/LoginPopup.css';



function App() {
  const [currentPage, setCurrentPage] = useState('dashboard'); // 'dashboard' | 'whitelist' | 'insights' | 'admin'
  const [loading, setLoading] = useState(true);
  const [analyticsData, setAnalyticsData] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [authLoading, setAuthLoading] = useState(true);
  const [userRole, setUserRole] = useState('user'); // 'user' or 'admin'
  const [showUserLoginPopup, setShowUserLoginPopup] = useState(false);
  const [showAdminLoginPopup, setShowAdminLoginPopup] = useState(false);

  useEffect(() => {
    // Check for authentication token in URL or localStorage
    checkAuthentication();
  }, []);

  useEffect(() => {
    if (currentPage === 'dashboard' && isAuthenticated) {
      loadDashboard();
    }
  }, [currentPage, isAuthenticated]);

  const checkAuthentication = () => {
    // Check URL parameters first (from extension popup)
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');

    if (token) {
      // Authentication from extension popup
      setIsAuthenticated(true);
      localStorage.setItem('auth_token', token);
      
      // Decode token to get role
      try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        setUserRole(payload.role || 'user');
      } catch (e) {
        setUserRole('user');
      }
      
      setAuthLoading(false);
    } else {
      // Check localStorage for existing session
      const storedToken = localStorage.getItem('auth_token');
      
      if (storedToken) {
        setIsAuthenticated(true);
        
        // Decode token to get role
        try {
          const payload = JSON.parse(atob(storedToken.split('.')[1]));
          setUserRole(payload.role || 'user');
        } catch (e) {
          setUserRole('user');
        }
      }
      setAuthLoading(false);
    }
  };

  const loadDashboard = () => {
    setLoading(true);
    getAnalytics(7) // Get last 7 days
      .then(response => {
        setAnalyticsData(response.data);
        setLoading(false);
      })
      .catch(error => {
        console.error("Failed to fetch analytics:", error);
        setLoading(false);
      });
  };

  const handleLogout = () => {
    // Clear authentication state
    setIsAuthenticated(false);
    setUserRole('user');
    
    // Clear localStorage
    localStorage.removeItem('auth_token');
    
    // Reset to dashboard page
    setCurrentPage('dashboard');
  };

  const handleLogin = (userData) => {
    setIsAuthenticated(true);
    setUserRole(userData.role);
    
    // If admin, redirect to admin dashboard
    if (userData.role === 'admin') {
      setCurrentPage('admin');
    }
  };

  if (authLoading) {
    return (
      <div className="App">
        <div className="auth-container">
          <div className="auth-loading">
            <h2>Loading...</h2>
          </div>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="App">
        <header className="App-header">
          <h1>Digital Drift Dashboard</h1>
          <nav className="main-nav">
            <div className="nav-left">
              {/* Empty nav-left for unauthenticated users */}
            </div>
            <div className="nav-right">
              <button 
                className="login-popup-btn" 
                onClick={() => setShowUserLoginPopup(true)}
              >
                Login or sign up for advanced analytics
              </button>
              <button 
                className="admin-login-btn" 
                onClick={() => setShowAdminLoginPopup(true)}
              >
                Admin Login
              </button>
            </div>
          </nav>
        </header>
        <main>
          <div className="auth-message-container">
            <div className="auth-message">
              <h2>Welcome to Digital Drift Tracker</h2>
              <p>Monitor your browsing habits and improve productivity</p>
              <div className="auth-instructions">
                <h3>Get Started</h3>
                <div className="auth-steps">
                  <div className="auth-step">
                    <div className="step-number">1</div>
                    <div>
                      <strong>Install Extension</strong>
                      <p>Add the browser extension to start tracking</p>
                    </div>
                  </div>
                  <div className="auth-step">
                    <div className="step-number">2</div>
                    <div>
                      <strong>Login</strong>
                      <p>Use your email or admin credentials</p>
                    </div>
                  </div>
                  <div className="auth-step">
                    <div className="step-number">3</div>
                    <div>
                      <strong>Track & Analyze</strong>
                      <p>View insights and improve productivity</p>
                    </div>
                  </div>
                </div>
              </div>
              <div className="auth-buttons">
                <button 
                  className="primary-login-btn" 
                  onClick={() => setShowUserLoginPopup(true)}
                >
                  Login or sign up for advanced analytics
                </button>
                <button 
                  className="admin-login-btn-main" 
                  onClick={() => setShowAdminLoginPopup(true)}
                >
                  Admin Login
                </button>
              </div>
            </div>
          </div>
        </main>
        {showUserLoginPopup && (
          <UserLoginPopup 
            onLogin={handleLogin} 
            onClose={() => setShowUserLoginPopup(false)} 
          />
        )}
        
        {showAdminLoginPopup && (
          <AdminLoginPopup 
            onClose={() => setShowAdminLoginPopup(false)} 
            onLogin={handleLogin}
          />
        )}
      </div>
    );
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>Digital Drift Dashboard</h1>
        <nav className="main-nav">
          <div className="nav-left">
            {userRole !== 'admin' && (
              <>
                <button 
                  className={currentPage === 'dashboard' ? 'nav-btn active' : 'nav-btn'}
                  onClick={() => setCurrentPage('dashboard')}
                >
                  Dashboard
                </button>
                <button 
                  className={currentPage === 'whitelist' ? 'nav-btn active' : 'nav-btn'}
                  onClick={() => setCurrentPage('whitelist')}
                >
                  Whitelist
                </button>
                <button 
                  className={currentPage === 'insights' ? 'nav-btn active' : 'nav-btn'}
                  onClick={() => setCurrentPage('insights')}
                >
                  Insights
                </button>
              </>
            )}
            {userRole === 'admin' && (
              <button 
                className={currentPage === 'admin' ? 'nav-btn active' : 'nav-btn'}
                onClick={() => setCurrentPage('admin')}
              >
                Admin Dashboard
              </button>
            )}
          </div>
          <div className="nav-right">
            <button className="logout-btn" onClick={handleLogout}>
              Logout
            </button>
          </div>
        </nav>
      </header>
      <main>
        {userRole !== 'admin' && currentPage === 'dashboard' && (
          <>
            {loading && <p>Loading analytics...</p>}
            {!loading && analyticsData && (
              <div className="dashboard-grid">
                {/* Category Breakdown - Pie Chart */}
                {analyticsData.category_totals && analyticsData.category_totals.length > 0 && (
                  <div className="dashboard-card">
                    <h2>Productivity Breakdown</h2>
                    <ProductivityPieChart data={analyticsData.category_totals} />
                  </div>
                )}

                {/* Top Domains - Bar Chart */}
                {analyticsData.domain_summaries && analyticsData.domain_summaries.length > 0 && (
                  <div className="dashboard-card">
                    <h2>Top Domains by Time Spent</h2>
                    <TopDomainsBarChart data={analyticsData.domain_summaries} />
                  </div>
                )}

                {/* Drift Timeline - Area Chart */}
                {analyticsData.drift_events && analyticsData.drift_events.length > 0 && (
                  <div className="dashboard-card">
                    <h2>Drift Events Timeline</h2>
                    <DriftTimeline data={analyticsData.drift_events} />
                  </div>
                )}

                {/* Daily Domain Activity - Line Chart */}
                {analyticsData.domain_summaries && analyticsData.domain_summaries.length > 0 && (
                  <div className="dashboard-card">
                    <h2>Daily Domain Activity</h2>
                    <DomainActivityChart data={analyticsData.domain_summaries} />
                  </div>
                )}

                {/* Drift Events Table */}
                <div className="dashboard-card full-width">
                  <h2>Recent Drift Events</h2>
                  <div className="scroll-panel">
                    <DriftList data={analyticsData.drift_events} />
                  </div>
                </div>
              </div>
            )}
            {!loading && !analyticsData && (
              <p>No analytics data available. Make sure the backend is running and try generating some test data.</p>
            )}
          </>
        )}
        
        {userRole !== 'admin' && currentPage === 'whitelist' && (
          <WhitelistManager />
        )}
        {userRole !== 'admin' && currentPage === 'insights' && (
          <InsightsPage />
        )}
        {currentPage === 'admin' && userRole === 'admin' && (
          <AdminDashboard />
        )}
      </main>
    </div>
  );
}

export default App;