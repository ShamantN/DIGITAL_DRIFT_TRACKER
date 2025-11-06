# Testing Instructions

This document provides instructions on how to set up and test the Digital Drift Tracker application.

## Prerequisites

- Python 3.8+
- Node.js 14+
- PostgreSQL 12+

## Backend Setup

1.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

2.  **Install Python dependencies:**
    ```bash
    pip install -r backend/requirements.txt
    ```

3.  **Set up the database:**
    - Create a PostgreSQL database named `digital_drift`.
    - Execute the schema file `database/ddt_schema.sql` to create the tables.
    - Execute the migration file `database/auth_migration.sql` to add the `hashed_password` column to the `users` table.

4.  **Run the backend server:**
    ```bash
    uvicorn backend.main:app --reload
    ```
    The backend will be running at `http://127.0.0.1:8000`.

## Frontend Setup

1.  **Install JavaScript dependencies:**
    ```bash
    cd dashboard
    npm install
    ```

2.  **Run the frontend development server:**
    ```bash
    npm start
    ```
    The dashboard will be running at `http://localhost:3000`.

## Extension Setup

1.  **Load the extension in your browser:**
    - Open Chrome and navigate to `chrome://extensions`.
    - Enable "Developer mode".
    - Click "Load unpacked" and select the `extension` directory.

## Testing Scenarios

### 1. User Authentication

1.  Open the extension popup.
2.  Click "Login or sign up for advanced analytics".
3.  Create a new account.
4.  You should see a "Advanced analytics enabled" message.
5.  Click the "Logout" button.
6.  You should be logged out.
7.  Log in with the account you created.
8.  You should be logged in again.

### 2. Dashboard Access

1.  While logged in, click "Open Dashboard" in the extension popup.
2.  The dashboard should open in a new tab.
3.  You should see your analytics data.
4.  Log out from the extension popup.
5.  Refresh the dashboard tab.
6.  You should be redirected to the authentication required page.

### 3. Data Isolation

1.  Create two different user accounts.
2.  Log in with the first user and generate some browsing data.
3.  Log out and log in with the second user.
4.  Open the dashboard.
5.  You should only see the data for the second user.

### 4. Whitelist

1.  Log in and open the dashboard.
2.  Navigate to the "Whitelist" page.
3.  Add a domain to the whitelist.
4.  The domain should appear in the list.
5.  Remove the domain from the whitelist.
6.  The domain should be removed from the list.