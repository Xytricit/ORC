# ORC Web Interface Guide

Complete guide to using the ORC web dashboard.

## Overview

The ORC web interface provides a visual, browser-based way to interact with your codebase analysis. It includes project management, AI chat, analysis history, and interactive visualizations.

## Starting the Web Interface

### From CLI

```bash
orc web
```

This will:
1. Start the Flask server on `http://127.0.0.1:5000`
2. Automatically open your browser
3. Create a local SQLite database for user data

### Custom Configuration

```bash
# Custom port
orc web --port 8080

# Allow external access (use with caution!)
orc web --host 0.0.0.0

# Debug mode (development only)
orc web --debug

# Don't auto-open browser
orc web --no-browser
```

### From Python Script

```python
from orc.web.app_new import app

if __name__ == '__main__':
    app.run(debug=False, host='127.0.0.1', port=5000)
```

## First Time Setup

### 1. Create Account

1. Navigate to `http://127.0.0.1:5000`
2. Click **"Sign Up"** on the landing page
3. Enter your details:
   - Username
   - Email
   - Password (minimum 8 characters)
4. Click **"Create Account"**

### 2. Sign In

1. Click **"Sign In"** on the landing page
2. Enter your username/email and password
3. Click **"Sign In"**

You'll be redirected to the dashboard.

## Features

### Dashboard Home

The main dashboard shows:

- **Quick Stats** - Total projects, files, analyses run
- **Recent Activity** - Latest analyses and actions
- **Project Overview** - Summary of all your projects
- **Quick Actions** - Common tasks and shortcuts

### Projects

#### Creating a Project

1. Click **"Projects"** in the sidebar
2. Click **"New Project"**
3. Fill in details:
   - **Name** - Project name
   - **Path** - Absolute path to your codebase
   - **Description** - Optional description
4. Click **"Create Project"**

The project will be indexed automatically.

#### Viewing Projects

- **Projects List** - Shows all your projects with stats
- **Project Detail** - Click a project to see:
  - Files, functions, classes, lines of code
  - Last indexed timestamp
  - Analysis history
  - Quick actions (reindex, analyze, delete)

#### Managing Projects

- **Reindex** - Update the project index after code changes
- **Analyze** - Run analysis on the project
- **Delete** - Remove project (doesn't delete actual code)

### Statistics

View comprehensive codebase metrics:

#### Overview Page (`/stats/`)

- **Summary Stats** - Totals across all projects
- **Projects Breakdown** - Table with metrics per project
- **Analysis Types** - Breakdown of analyses run
- **Health Indicators** - Project health scores

#### Project Detail Stats (`/stats/project/<id>`)

- **Detailed Metrics** - Files, functions, classes, LOC
- **Health Score** - 0-100% based on code quality
- **Analysis Timeline** - Last 30 days activity chart
- **Recent Analyses** - History of analyses for this project

### AI Chat

Interactive AI-powered code assistance:

1. Click **"AI Assistant"** in the sidebar
2. Select a project from the dropdown
3. Type your question in the chat box
4. Press Enter or click Send

**Example Questions:**
- "Explain the authentication flow"
- "Find all database queries"
- "How can I optimize performance?"
- "What does the User model do?"
- "Show me all API endpoints"

**Features:**
- Context-aware responses based on your codebase
- Code syntax highlighting in responses
- Conversation history
- Multiple AI provider support (Groq, OpenAI, etc.)

### Analysis

#### Running Analysis

1. Click **"Analysis"** in the sidebar
2. Select analysis type:
   - **All** - Complete analysis
   - **Dead Code** - Find unused code
   - **Complexity** - Code complexity metrics
   - **Security** - Security vulnerabilities
   - **Performance** - Performance issues
3. Select project
4. Click **"Run Analysis"**

#### Viewing Results

Analysis results show:
- **Summary** - High-level metrics
- **Issues Found** - Detailed list of problems
- **Recommendations** - Suggested fixes
- **Code Snippets** - Relevant code sections

#### Analysis History

View past analyses:
1. Click **"History"** in the sidebar
2. Browse all previous analyses
3. Click an analysis to view details
4. Filter by project or analysis type

### Settings

#### Account Settings

1. Click your username in the sidebar
2. Select **"Account"**
3. Update:
   - Email
   - Password
   - Profile information

#### API Configuration

1. Click **"Settings"** → **"API Config"**
2. Add your AI provider API keys:
   - Groq
   - OpenAI
   - Anthropic
   - DeepSeek
   - Gemini
3. Select default provider and model
4. Click **"Save"**

**Security Note:** API keys are encrypted in the database.

## User Interface

### Sidebar Navigation

- **Dashboard** - Home page
- **Projects** - Project management
- **Statistics** - Codebase metrics
- **AI Assistant** - Chat interface
- **Analysis** - Run analyses
- **History** - Past analyses
- **Settings** - Configuration
- **User Menu** - Account, sign out

### Quick Stats (Sidebar)

Shows real-time stats:
- Total files across all projects
- Total analyses run

### Theme

The interface uses a clean black and green theme:
- Dark background for reduced eye strain
- Green accents for primary actions
- High contrast for readability

## API Integration

The web interface exposes a REST API:

### Authentication

Use session cookies or API tokens (if configured).

### Endpoints

```
GET  /api/projects           - List projects
POST /api/projects           - Create project
GET  /api/projects/<id>      - Get project details
PUT  /api/projects/<id>      - Update project
DELETE /api/projects/<id>    - Delete project

GET  /api/analysis           - List analyses
POST /api/analysis/run       - Run analysis
GET  /api/analysis/<id>      - Get analysis results

POST /api/chat               - Send chat message
GET  /api/chat/history       - Get chat history

GET  /api/stats              - Get statistics
```

See [API Documentation](../api/README.md) for full details.

## Deployment

### Development

```bash
# Run in development mode
orc web --debug
```

### Production

For production deployment:

1. **Set environment variables:**
   ```bash
   export ORC_SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
   export FLASK_ENV=production
   ```

2. **Use production server (Gunicorn):**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 orc.web.app_new:app
   ```

3. **Use reverse proxy (nginx):**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

See [Deployment Guide](../DEPLOYMENT.md) for complete setup.

## Tips & Tricks

### Performance

- **Index in Background** - Large codebases may take time to index
- **Use Project Filters** - Filter by project in analysis and chat
- **Clear Old Analyses** - Delete old analysis results to save space

### Security

- **Don't Expose Publicly** - The web interface is meant for local use
- **Use Strong Passwords** - Especially if deploying to a server
- **Protect API Keys** - Never commit API keys to version control
- **Enable HTTPS** - Use SSL in production deployments

### Workflow

1. **Create Projects** for each codebase
2. **Run Initial Index** after creating project
3. **Configure AI Keys** in settings
4. **Run Analyses** regularly
5. **Use Chat** for quick questions
6. **Check Stats** to track code health

## Keyboard Shortcuts

- `Ctrl/Cmd + K` - Focus search (coming soon)
- `Ctrl/Cmd + /` - Toggle sidebar
- `Esc` - Close modals

## Browser Compatibility

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

## Troubleshooting

### Can't Access Web Interface

**Problem:** Server won't start or page won't load

**Solutions:**
1. Check port is not already in use: `lsof -i :5000` (macOS/Linux)
2. Try a different port: `orc web --port 8080`
3. Check firewall settings
4. Ensure Flask is installed: `pip install flask`

### Database Errors

**Problem:** Database locked or migration errors

**Solutions:**
1. Stop all ORC processes
2. Delete `instance/orc_web.db`
3. Restart ORC web interface (will recreate database)

### API Keys Not Working

**Problem:** AI chat returns errors

**Solutions:**
1. Verify API keys are correct in Settings
2. Check API key has sufficient credits
3. Try a different AI provider
4. Check internet connection

### Slow Performance

**Problem:** Web interface is slow

**Solutions:**
1. Reduce project size (use `.orcignore`)
2. Clear old analysis history
3. Use faster storage (SSD)
4. Increase system resources

See [Troubleshooting Guide](../TROUBLESHOOTING.md) for more issues.

## See Also

- [Getting Started](../getting_started.md)
- [CLI Reference](../cli/README.md)
- [API Documentation](../api/README.md)
- [Deployment Guide](../DEPLOYMENT.md)
