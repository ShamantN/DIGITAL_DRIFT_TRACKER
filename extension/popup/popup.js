// extension/popup/popup.js
document.addEventListener('DOMContentLoaded', () => {

  // --- Authentication State ---
  let isAuthenticated = false;
  let authToken = null;
  let currentUserId = null;

  // --- Authentication Elements ---
  const authLink = document.getElementById('auth-link');
  const authPopup = document.getElementById('auth-popup');
  const authCloseBtn = document.getElementById('auth-close');
  const loginForm = document.getElementById('login-form');
  const signupForm = document.getElementById('signup-form');
  const loginFormElement = document.getElementById('login-form-element');
  const signupFormElement = document.getElementById('signup-form-element');
  const showSignupLink = document.getElementById('show-signup');
  const showLoginLink = document.getElementById('show-login');
  const loginError = document.getElementById('login-error');
  const signupError = document.getElementById('signup-error');

  // Check for existing authentication on load
  chrome.storage.local.get(['auth_token', 'user_id', 'user_email'], (data) => {
    if (data.auth_token && data.user_id) {
      isAuthenticated = true;
      authToken = data.auth_token;
      currentUserId = data.user_id;
      updateAuthUI();
    }
  });

  // --- 1. Handle the "View Detailed Analysis" link ---
  const link = document.getElementById('view-dashboard-link');
  if (link) {
    link.addEventListener('click', (e) => {
      e.preventDefault(); // Stop the link from trying to navigate
      
      if (!isAuthenticated) {
        // Show authentication message
        alert('Please login or sign up to view advanced analytics');
        showAuthPopup();
        return;
      }
      
      // Use the chrome.tabs API to open the new tab with authentication
      chrome.tabs.create({ 
        url: `http://localhost:3000?token=${authToken}&user_id=${currentUserId}` 
      });
    });
  }

  // --- Authentication Functions ---
  function showAuthPopup() {
    authPopup.classList.remove('hidden');
    loginError.classList.add('hidden');
    signupError.classList.add('hidden');
  }

  function hideAuthPopup() {
    authPopup.classList.add('hidden');
    loginFormElement.reset();
    signupFormElement.reset();
  }

  function showLoginForm() {
    loginForm.classList.remove('hidden');
    signupForm.classList.add('hidden');
    loginError.classList.add('hidden');
    signupError.classList.add('hidden');
  }

  function showSignupForm() {
    signupForm.classList.remove('hidden');
    loginForm.classList.add('hidden');
    loginError.classList.add('hidden');
    signupError.classList.add('hidden');
  }

  async function handleLogin(event) {
    event.preventDefault();
    const formData = new FormData(loginFormElement);
    const email = formData.get('email');
    const password = formData.get('password');

    try {
      const response = await fetch('http://127.0.0.1:8000/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (response.ok) {
        // Store authentication data
        isAuthenticated = true;
        authToken = data.access_token;
        currentUserId = data.user_id;
        
        // Store in chrome storage for persistence
        chrome.storage.local.set({
          'auth_token': authToken,
          'user_id': currentUserId,
          'user_email': data.email
        });

        hideAuthPopup();
        updateAuthUI();
      } else {
        loginError.textContent = data.detail || 'Login failed';
        loginError.classList.remove('hidden');
      }
    } catch (error) {
      console.error('Login error:', error);
      loginError.textContent = 'Network error. Please try again.';
      loginError.classList.remove('hidden');
    }
  }

  async function handleSignup(event) {
    event.preventDefault();
    const formData = new FormData(signupFormElement);
    const email = formData.get('email');
    const password = formData.get('password');
    const confirmPassword = formData.get('confirm_password');

    if (password !== confirmPassword) {
      signupError.textContent = 'Passwords do not match';
      signupError.classList.remove('hidden');
      return;
    }

    try {
      const response = await fetch('http://127.0.0.1:8000/api/auth/signup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password, confirm_password: confirmPassword }),
      });

      const data = await response.json();

      if (response.ok) {
        // Store authentication data
        isAuthenticated = true;
        authToken = data.access_token;
        currentUserId = data.user_id;
        
        // Store in chrome storage for persistence
        chrome.storage.local.set({
          'auth_token': authToken,
          'user_id': currentUserId,
          'user_email': data.email
        });

        hideAuthPopup();
        updateAuthUI();
      } else {
        signupError.textContent = data.detail || 'Signup failed';
        signupError.classList.remove('hidden');
      }
    } catch (error) {
      console.error('Signup error:', error);
      signupError.textContent = 'Network error. Please try again.';
      signupError.classList.remove('hidden');
    }
  }

  function updateAuthUI() {
    if (isAuthenticated) {
      authLink.textContent = 'Advanced analytics enabled';
      authLink.style.background = '#ecfdf5';
      authLink.style.color = '#047857';
      authLink.href = '#';
      authLink.removeEventListener('click', showAuthPopup);
    } else {
      authLink.textContent = 'Login or sign up for advanced analytics';
      authLink.style.background = '#e0f2fe';
      authLink.style.color = '#0ea5e9';
      authLink.addEventListener('click', (e) => {
        e.preventDefault();
        showAuthPopup();
      });
    }
  }

  // --- Event Listeners for Authentication ---
  if (authLink) {
    authLink.addEventListener('click', (e) => {
      e.preventDefault();
      if (!isAuthenticated) {
        showAuthPopup();
      }
    });
  }

  if (authCloseBtn) {
    authCloseBtn.addEventListener('click', hideAuthPopup);
  }

  if (showSignupLink) {
    showSignupLink.addEventListener('click', (e) => {
      e.preventDefault();
      showSignupForm();
    });
  }

  if (showLoginLink) {
    showLoginLink.addEventListener('click', (e) => {
      e.preventDefault();
      showLoginForm();
    });
  }

  if (loginFormElement) {
    loginFormElement.addEventListener('submit', handleLogin);
  }

  if (signupFormElement) {
    signupFormElement.addEventListener('submit', handleSignup);
  }

  // Close popup when clicking outside
  authPopup.addEventListener('click', (e) => {
    if (e.target === authPopup) {
      hideAuthPopup();
    }
  });

  // --- 2. Get current session ID from storage ---
  chrome.storage.local.get('sid', (data) => {
    document.getElementById('sid').textContent = data.sid || 'N/A';
  });

  // --- 3. Fetch analytics from our backend ---
  const list = document.getElementById('drift-list');
  const statusEl = document.getElementById('status');
  const totalEl = document.getElementById('stat-total');
  const minutesEl = document.getElementById('stat-minutes');
  const topEl = document.getElementById('stat-top');
  list.innerHTML = '<li class="loading">Loading...</li>'; // Clear and set loading

  // We need the user ID. For now, just hardcode it
  const MOCK_USER_ID = 1;

  fetch(`http://127.0.0.1:8000/api/dashboard/analytics?user_id=${MOCK_USER_ID}&period_days=1`)
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      list.innerHTML = ''; // Clear 'Loading...'
      if (!data.drift_events || data.drift_events.length === 0) {
        list.innerHTML = '<li class="loading">No drifts recorded today.</li>';
        totalEl.textContent = '0';
        minutesEl.textContent = '0';
        topEl.textContent = '—';
      } else {
        // Stats
        const total = data.drift_events.length;
        const totalMin = Math.round((data.drift_events.reduce((sum, d) => sum + (d.duration_seconds || 0), 0)) / 60);
        const typeCounts = data.drift_events.reduce((acc, d) => {
          const t = d.drift_type || 'Unknown';
          acc[t] = (acc[t] || 0) + 1;
          return acc;
        }, {});
        const topType = Object.keys(typeCounts).sort((a,b) => typeCounts[b]-typeCounts[a])[0];
        totalEl.textContent = String(total);
        minutesEl.textContent = String(totalMin);
        topEl.textContent = topType ? `${topType} (${typeCounts[topType]})` : '—';

        // Recent list (max 6)
        data.drift_events.slice(0, 6).forEach(drift => {
          const li = document.createElement('li');
          const duration = Math.round(drift.duration_seconds / 60);
          li.textContent = `${drift.drift_type} (${duration} min)`;
          list.appendChild(li);
        });
      }
    })
    .catch(err => {
      console.error("Popup fetch error:", err); // Log the error for debugging
      statusEl.textContent = 'Error';
      statusEl.className = 'status-pill err';
      list.innerHTML = '<li class="loading">Could not connect to server.</li>';
      totalEl.textContent = '—';
      minutesEl.textContent = '—';
      topEl.textContent = '—';
    });
});