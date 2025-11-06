# Digital Drift Tracker

A comprehensive productivity tracking system that helps users monitor and analyze their digital habits through browser activity tracking, data visualization, and intelligent insights.

## 🚀 Project Overview

Digital Drift Tracker is a full-stack application consisting of:
- **Chrome Browser Extension**: Tracks user browsing activity in real-time
- **FastAPI Backend**: Processes and analyzes activity data
- **React Dashboard**: Provides interactive data visualizations and insights
- **MySQL Database**: Stores user sessions, activity events, and analytics

## 📊 Key Features

### 🔍 Activity Tracking
- **Real-time Browser Monitoring**: Tracks tab openings, URL changes, and time spent on websites
- **User Interaction Capture**: Records mouse movements, clicks, and scroll events
- **Session Management**: Automatically manages user browsing sessions
- **Domain Categorization**: Classifies websites as Productive, Unproductive, or Neutral

### 📈 Analytics & Insights
- **Productivity Breakdown**: Visualize time spent across different categories
- **Top Domains Analysis**: See which websites consume most of your time
- **Drift Event Detection**: Identifies when users lose focus or get distracted
- **Daily Activity Summaries**: Track productivity trends over time
- **Whitelist Management**: Customize domain categories to match your needs

### 🎯 Smart Features
- **Drift Analysis**: Identifies patterns leading to productivity loss
- **Unclassified Domain Detection**: Highlights frequently visited neutral sites
- **Session Productivity Metrics**: Measures focus efficiency per browsing session
- **Interactive Charts**: Multiple visualization types including pie charts, bar charts, timelines, and area charts

## 🏗️ Architecture

### Backend (FastAPI)
- **RESTful API**: Comprehensive endpoints for data management
- **JWT Authentication**: Secure user authentication system
- **Database Integration**: MySQL with proper schema design
- **CORS Support**: Enables cross-origin communication
- **Background Jobs**: Automated analysis and summary generation

### Frontend (React)
- **Modern React**: Hooks-based functional components
- **Interactive Dashboards**: Multiple chart types using Recharts
- **Responsive Design**: Mobile-friendly interface
- **Authentication Integration**: Seamless login/logout flow

### Browser Extension
- **Manifest V3**: Modern Chrome extension architecture
- **Background Service Worker**: Efficient event processing
- **Content Script Injection**: Page-level activity monitoring
- **Event Batching**: Optimized data transmission
- **Storage Integration**: Local session management

### Database (MySQL)
- **Normalized Schema**: Efficient data organization
- **Foreign Key Constraints**: Data integrity enforcement
- **Stored Procedures**: Complex business logic encapsulation
- **Indexes**: Optimized query performance

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern, fast web framework
- **MySQL**: Relational database management
- **JWT**: JSON Web Token authentication
- **Pydantic**: Data validation and serialization
- **python-jose**: JWT token handling
- **passlib**: Password hashing

### Frontend
- **React**: UI library
- **Recharts**: Charting and visualization
- **Axios**: HTTP client
- **CSS3**: Styling and layout

### Extension
- **JavaScript ES6+**: Modern JavaScript features
- **Chrome Extension APIs**: Browser integration
- **Event-driven Architecture**: Efficient event handling

## 📁 Project Structure

```
digital-drift-tracker/
├── backend/                    # FastAPI backend
│   ├── main.py              # Main application file
│   ├── database.py          # Database connection
│   ├── models.py            # Pydantic models
│   ├── requirements.txt     # Python dependencies
│   └── jobs/                # Background analysis scripts
│       ├── run_drift_analysis.py
│       └── run_daily_summary.py
├── dashboard/               # React frontend
│   ├── src/
│   │   ├── App.js          # Main application
│   │   ├── components/     # Reusable UI components
│   │   ├── pages/          # Page components
│   │   └── services/       # API service functions
│   └── package.json        # Node.js dependencies
├── extension/              # Chrome extension
│   ├── manifest.json       # Extension configuration
│   ├── background.js       # Background service worker
│   ├── content.js        # Content script
│   └── popup/            # Extension popup UI
├── database/              # SQL schema and migrations
│   └── ddt_schema.sql     # Database schema
└── venv/                  # Python virtual environment
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 14+
- MySQL Server
- Chrome Browser

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Setup
```bash
cd dashboard
npm install
npm start
```

### Database Setup
```sql
CREATE DATABASE ddt;
USE ddt;
SOURCE database/ddt_schema.sql;
```

### Extension Setup
1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked" and select the `extension` folder

## 📊 API Endpoints

### Session Management
- `POST /api/session/start` - Start a new browsing session
- `POST /api/session/close` - Close current session

### Activity Tracking
- `POST /api/tab/open` - Record tab opening
- `POST /api/tab/close` - Record tab closing
- `POST /api/events/batch` - Submit activity events

### Analytics
- `GET /api/dashboard/analytics` - Get analytics data
- `GET /api/dashboard/insights` - Get insights and recommendations

### Domain Management
- `GET /api/whitelist` - Get whitelisted domains
- `POST /api/whitelist` - Add domain to whitelist
- `DELETE /api/whitelist` - Remove domain from whitelist

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the backend directory:
```
DB_HOST=localhost
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=ddt
SECRET_KEY=your_secret_key
```

### Extension Configuration
Modify `extension/manifest.json` for production deployment:
- Update API URLs
- Configure permissions appropriately
- Set proper extension icons

## 📈 Data Analysis Features

### Drift Detection
The system identifies "drift events" when users lose focus, characterized by:
- Rapid tab switching
- Extended time on unproductive sites
- Pattern analysis of browsing behavior

### Productivity Metrics
- **Category Distribution**: Time spent across productive/unproductive categories
- **Session Efficiency**: Focus duration vs. distraction frequency
- **Domain Analysis**: Most visited sites and their impact
- **Temporal Patterns**: Productivity variations throughout the day

### Insights Generation
- **Unclassified Domain Detection**: Identifies frequently visited neutral sites
- **Drift Trigger Analysis**: Finds patterns leading to productivity loss
- **Whitelist Recommendations**: Suggests domains to categorize as productive

## 🔒 Privacy & Security

- **Local Data Processing**: Activity data processed locally before transmission
- **Secure Authentication**: JWT-based authentication system
- **Data Minimization**: Only essential browsing data is collected
- **User Control**: Users can manage their data and whitelist preferences

## 🐛 Troubleshooting

### Common Issues
1. **Extension Not Loading**: Check Chrome extension permissions
2. **Database Connection Errors**: Verify MySQL credentials and server status
3. **CORS Issues**: Ensure backend CORS configuration is correct
4. **Data Not Appearing**: Check API endpoints and network connectivity

### Debug Mode
Enable debug logging in the extension by modifying `background.js`:
```javascript
const DEBUG_MODE = true;
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- FastAPI team for the excellent web framework
- React community for the powerful UI library
- Chrome Extension team for the browser APIs
- Contributors and testers who helped improve this project

---

**Digital Drift Tracker** - Helping you stay focused in the digital age! 🎯