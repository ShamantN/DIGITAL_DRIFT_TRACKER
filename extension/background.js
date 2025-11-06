// extension/background.js

const API_URL = 'http://127.0.0.1:8000';
let eventBatch = [];
let batchTimer;

// In a real app, you'd get this after a login.
let currentSessionId = null;

// A map to store the 'tid' we get from the backend
const chromeTabToDbIdMap = new Map();

// --- Core API Functions ---
async function apiPost(endpoint, body) {
  try {
    const { auth_token } = await chrome.storage.local.get(['auth_token']);
    const headers = { 'Content-Type': 'application/json' };
    if (auth_token) {
      headers['Authorization'] = `Bearer ${auth_token}`;
    }

    const response = await fetch(`${API_URL}${endpoint}`, {
      method: 'POST',
      headers: headers,
      body: JSON.stringify(body),
    });
    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error(`Failed to post to ${endpoint}:`, error);
  }
}

async function startSession() {
  const { auth_token } = await chrome.storage.local.get(['auth_token']);
  if (!auth_token) {
    console.log("No auth token, skipping session start");
    return;
  }
  const sessionData = {
    browser_name: "Chrome", // Simplified
    browser_version: "110", // Simplified
    platform: "Windows", // Simplified
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
  };
  const response = await apiPost('/api/session/start', sessionData);
  if (response && response.sid) {
    currentSessionId = response.sid;
    console.log('Session started:', currentSessionId);
    chrome.storage.local.set({ sid: currentSessionId });
  }
}

async function closeSession() {
  if (currentSessionId) {
    await apiPost('/api/session/close', { sid: currentSessionId });
    console.log('Session closed:', currentSessionId);
    currentSessionId = null;
    chrome.storage.local.remove('sid');
  }
}

// --- Event Batching ---
function queueEvent(event) {
  if (!currentSessionId) return; // Don't track if session isn't on

  const eventWithContext = {
    ...event,
    timestamp: new Date().toISOString(),
  };
  eventBatch.push(eventWithContext);

  // Clear existing timer
  if (batchTimer) clearTimeout(batchTimer);

  // Send batch if it's big enough or after 30s
  if (eventBatch.length >= 20) {
    sendBatch();
  } else {
    batchTimer = setTimeout(sendBatch, 30000); // 30 seconds
  }
}

async function sendBatch() {
  if (eventBatch.length === 0) return;

  const batchToSend = [...eventBatch];
  eventBatch = [];
  
  await apiPost('/api/events/batch', {
    session_id: currentSessionId,
    events: batchToSend,
  });
  console.log(`Sent batch of ${batchToSend.length} events`);
}

// --- Browser Event Listeners ---
chrome.runtime.onStartup.addListener(startSession);
chrome.windows.onRemoved.addListener(closeSession); // When browser closes
chrome.runtime.onInstalled.addListener(startSession); // On first install

// When a tab is created
chrome.tabs.onCreated.addListener(async (tab) => {
  if (!currentSessionId) {
    await startSession();
  }
  
  // Wait a bit for tab URL to be available, then check if it's trackable
  setTimeout(async () => {
    try {
      const tabInfo = await chrome.tabs.get(tab.id);
      const url = tabInfo.url || '';
      
      // Only track http/https URLs, not chrome://, edge://, or extension pages
      if (url.startsWith('http://') || url.startsWith('https://')) {
        const payload = {
          session_id: currentSessionId,
          url: url,
          title: tabInfo.title || 'New Tab',
          // user_id is not needed - backend gets it from JWT token
        };
        
        const response = await apiPost('/api/tab/open', payload);
        if (response && response.tid) {
          chromeTabToDbIdMap.set(tab.id, response.tid);
        }
      }
    } catch (error) {
      // Tab might have been closed already
      console.debug('Error tracking new tab:', error);
    }
  }, 200);
});

// When a tab is closed
chrome.tabs.onRemoved.addListener(async (chromeTabId, removeInfo) => {
  const tid = chromeTabToDbIdMap.get(chromeTabId);
  if (tid) {
    await apiPost('/api/tab/close', { tid });
    chromeTabToDbIdMap.delete(chromeTabId);
  }
});

// When the user switches TO a different tab
chrome.tabs.onActivated.addListener((activeInfo) => {
  const tid = chromeTabToDbIdMap.get(activeInfo.tabId);
  if (tid) {
    queueEvent({
      tab_id: tid,
      event_type: 'TAB_FOCUS',
      url: null, // We'll get this on the 'onUpdated' event
    });
  }
});

// When a tab's URL changes or is updated
chrome.tabs.onUpdated.addListener(async (chromeTabId, changeInfo, tab) => {
  const url = changeInfo.url || tab.url;
  
  // Handle new tabs that get URLs after creation
  if (changeInfo.status === 'loading' && url && !chromeTabToDbIdMap.has(chromeTabId)) {
    if (!currentSessionId) {
      await startSession();
    }
    
    // Only track http/https URLs
    if (url.startsWith('http://') || url.startsWith('https://')) {
      const payload = {
        session_id: currentSessionId,
        url: url,
        title: tab.title || 'New Tab',
      };
      const response = await apiPost('/api/tab/open', payload);
      if (response && response.tid) {
        chromeTabToDbIdMap.set(chromeTabId, response.tid);
      }
    }
  }
  
  // Handle URL changes for existing tracked tabs
  const tid = chromeTabToDbIdMap.get(chromeTabId);
  if (tid && url && (url.startsWith('http://') || url.startsWith('https://'))) {
    queueEvent({
      tab_id: tid,
      event_type: 'URL_CHANGE',
      url: url,
    });
  }
  
  // Remove tracking if tab navigated to non-http page
  if (tid && url && !url.startsWith('http://') && !url.startsWith('https://')) {
    chromeTabToDbIdMap.delete(chromeTabId);
  }
});

// Listen for messages from content.js
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'ACTIVITY_EVENT') {
    const chromeTabId = sender.tab?.id;
    if (!chromeTabId) {
      sendResponse({ success: false, error: 'No tab ID' });
      return true;
    }
    
    const tid = chromeTabToDbIdMap.get(chromeTabId);
    if (tid) {
      message.data.tab_id = tid;
      queueEvent(message.data);
      sendResponse({ success: true });
    } else {
      sendResponse({ success: false, error: 'Tab not tracked' });
    }
  }
  return true; // Keep message channel open for async response
});

// Initialize session on load
chrome.storage.local.get('sid', (data) => {
  if (data.sid) {
    currentSessionId = data.sid;
    console.log('Rejoined session:', currentSessionId);
  } else {
    // Check for auth token before starting a session
    chrome.storage.local.get('auth_token', (data) => {
        if(data.auth_token) {
            startSession();
        }
    });
  }
});