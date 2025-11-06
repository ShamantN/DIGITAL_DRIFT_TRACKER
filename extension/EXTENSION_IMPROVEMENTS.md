# Extension Improvements Needed

## ✅ Currently Working
- Session start/close
- Tab tracking with ID mapping
- Event batching (30s or 20 events)
- Content script event capture (mouse, scroll, click)
- Popup analytics display

## 🔧 Suggested Improvements

### 1. Filter Chrome/Extension Pages
Only track `http://` and `https://` URLs, not `chrome://`, `edge://`, or extension pages.

### 2. Better Tab Creation Handling
Handle cases where tabs don't have URLs immediately when created.

### 3. Error Handling
Add better error handling for API failures and network issues.

### 4. Idle Detection
The extension has `idle` permission but doesn't use it. Could implement idle detection.

### 5. Response Handling
The `onMessage` listener should return `true` for async operations.

## 🐛 Known Limitations

1. **Chrome Extension Pages**: Cannot inject content scripts into `chrome://` pages
2. **Private/Incognito**: May not work in incognito mode by default
3. **Network Errors**: If backend is down, events are silently lost

## ✅ Overall Assessment

The extension is **functionally correct** and should work for tracking regular web browsing activity. The main improvements would be:
- Better URL filtering
- Improved error handling
- Handling edge cases (new tabs, chrome:// pages)
