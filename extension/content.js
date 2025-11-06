// extension/content.js

// --- Throttling functions ---
// We can't send every mouse move, so we "throttle" it
let lastMousePost = 0;
let lastScrollPost = 0;
const throttleDelay = 1000; // 1 second

// --- Mouse Listener ---
document.addEventListener('mousemove', (e) => {
  const now = Date.now();
  if (now - lastMousePost < throttleDelay) return; // Throttled
  lastMousePost = now;

  chrome.runtime.sendMessage({
    type: 'ACTIVITY_EVENT',
    data: {
      event_type: 'MOUSE_MOVE',
      mouse_x: e.clientX,
      mouse_y: e.clientY,
      target_element_id: e.target.id || null,
      url: window.location.href,
    },
  }).catch(err => {
    // Silently fail if extension context is invalidated
    console.debug('Failed to send mouse event:', err);
  });
});

// --- Scroll Listener ---
document.addEventListener('scroll', (e) => {
  const now = Date.now();
  if (now - lastScrollPost < throttleDelay) return; // Throttled
  lastScrollPost = now;

  const scrollHeight = document.documentElement.scrollHeight - window.innerHeight;
  const scrollPercent = scrollHeight > 0 ? (window.scrollY / scrollHeight) * 100 : 0;
  
  chrome.runtime.sendMessage({
    type: 'ACTIVITY_EVENT',
    data: {
      event_type: 'SCROLL',
      scroll_y_pixels: Math.round(window.scrollY),
      scroll_y_percent: parseFloat(scrollPercent.toFixed(2)),
      url: window.location.href,
    },
  }).catch(err => {
    // Silently fail if extension context is invalidated
    console.debug('Failed to send scroll event:', err);
  });
});

// --- Click Listener ---
document.addEventListener('click', (e) => {
  chrome.runtime.sendMessage({
    type: 'ACTIVITY_EVENT',
    data: {
      event_type: 'CLICK',
      mouse_x: e.clientX,
      mouse_y: e.clientY,
      target_element_id: e.target.id || e.target.className || e.target.tagName,
      url: window.location.href,
    },
  }).catch(err => {
    // Silently fail if extension context is invalidated
    console.debug('Failed to send click event:', err);
  });
});