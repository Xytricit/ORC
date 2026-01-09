# ORC Web Application - Complete Build Plan

## 🎯 Overview
Build a professional, full-featured web application for ORC with:
- **Color Scheme**: Black & Green (tech/matrix theme)
- **Logo**: `orclogo.png` (exists in `assets/`)
- **Authentication**: User sign up, sign in, sign out
- **Dashboard**: Sidebar navigation with multiple features
- **API Configuration**: User-configurable AI providers
- **Index Management**: Configure and query ORC's codebase index

---

## 📋 Current State Analysis

### ✅ What Exists
- **Flask Apps**: `app.py` (dev) and `app_prod.py` (production)
- **Templates**: 5 HTML files (dashboard, complexity, graph, error, recommendations)
- **CSS**: `dashboard.css` with modern styling
- **Logo**: `assets/orclogo.png` exists
- **Static Assets**: `orc/web/static/` folder structure ready
- **API Endpoints**: Basic analysis endpoints in place

### ❌ What's Missing
- **No Authentication System**: No user accounts, login, logout
- **No User Database**: No user table or session management
- **No Professional Landing Page**: No homepage introducing ORC
- **No User Dashboard**: Current dashboard is basic, no personalization
- **No Sidebar Navigation**: No organized navigation system
- **No API Configuration UI**: Users can't configure AI providers
- **No Account Management**: No profile, settings, or preferences
- **Black & Green Theme**: Current theme is different

---

## 🏗️ Architecture Plan

### Tech Stack
```
Backend:
- Flask (existing)
- Flask-Login (authentication)
- Flask-SQLAlchemy (database ORM)
- Flask-WTF (forms with CSRF)
- Flask-Bcrypt (password hashing)

Frontend:
- HTML5 + Jinja2 templates
- CSS3 (custom black/green theme)
- Vanilla JavaScript (no heavy frameworks)
- Font Awesome (icons)

Database:
- SQLite (development)
- PostgreSQL ready (production)

Storage:
- User data: SQLite/PostgreSQL
- ORC indexes: Existing .orc/ structure
```

### Database Schema
```sql
-- Users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(120),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME,
    is_active BOOLEAN DEFAULT TRUE
);

-- User API configurations
CREATE TABLE api_configs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    provider VARCHAR(50) NOT NULL, -- ollama, groq, openai, etc.
    api_key VARCHAR(255),
    model_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- User projects (indexed codebases)
CREATE TABLE projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name VARCHAR(120) NOT NULL,
    path VARCHAR(500),
    description TEXT,
    db_path VARCHAR(500), -- path to .orc/index.db
    last_indexed DATETIME,
    file_count INTEGER,
    function_count INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Analysis history
CREATE TABLE analysis_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    project_id INTEGER,
    analysis_type VARCHAR(50), -- dead_code, complexity, security, etc.
    results JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (project_id) REFERENCES projects (id)
);
```

---

## 🎨 Design System

### Color Palette
```css
/* Primary Colors */
--primary-black: #0a0a0a;      /* Deep black background */
--primary-green: #00ff41;      /* Matrix green (primary) */
--secondary-green: #00cc33;    /* Darker green */
--accent-green: #00ff88;       /* Light green (accents) */

/* Neutral Colors */
--gray-dark: #1a1a1a;          /* Card backgrounds */
--gray-medium: #2a2a2a;        /* Borders, dividers */
--gray-light: #3a3a3a;         /* Hover states */
--text-primary: #ffffff;       /* Primary text */
--text-secondary: #b0b0b0;     /* Secondary text */

/* Status Colors */
--success: #00ff41;            /* Success messages */
--warning: #ffaa00;            /* Warnings */
--error: #ff4444;              /* Errors */
--info: #00aaff;               /* Info messages */
```

### Typography
```css
Font Family:
- Primary: 'JetBrains Mono', 'Monaco', 'Courier New', monospace
- Fallback: system-ui, -apple-system, sans-serif

Font Sizes:
- Heading 1: 2.5rem (40px)
- Heading 2: 2rem (32px)
- Heading 3: 1.5rem (24px)
- Body: 1rem (16px)
- Small: 0.875rem (14px)
```

---

## 📄 Pages to Build

### 1. Landing Page (`/`)
**Purpose**: Introduce ORC to new visitors

**Sections**:
- Hero section with logo and tagline
- "What is ORC?" explanation
- Key features showcase (4-6 cards)
- Live demo/screenshots
- Call-to-action: Sign Up / Sign In buttons
- Footer with links

**Layout**:
```
┌─────────────────────────────────────┐
│  [Logo] ORC                  Sign In│
├─────────────────────────────────────┤
│                                     │
│    Optimize & Refactor Catalyst     │
│    AI-Powered Code Intelligence     │
│         [Get Started Free]          │
│                                     │
├─────────────────────────────────────┤
│  [Feature 1] [Feature 2] [Feature 3]│
│  [Feature 4] [Feature 5] [Feature 6]│
├─────────────────────────────────────┤
│         How It Works               │
│   1. Index  2. Analyze  3. Optimize│
└─────────────────────────────────────┘
```

### 2. Sign Up Page (`/signup`)
**Fields**:
- Full Name
- Username
- Email
- Password
- Confirm Password
- [ ] Accept Terms & Conditions
- [Sign Up] button
- "Already have an account? Sign In"

### 3. Sign In Page (`/signin`)
**Fields**:
- Username or Email
- Password
- [ ] Remember Me
- [Sign In] button
- "Forgot password?"
- "Don't have an account? Sign Up"

### 4. Dashboard (`/dashboard`)
**Layout**: Sidebar + Main Content

**Sidebar** (left, always visible):
```
┌─────────────────┐
│ [Logo] ORC      │
│                 │
│ 👤 Username     │
│                 │
│ 📊 Dashboard    │
│ 📁 Projects     │
│ 🔍 Analysis     │
│ ⚙️  API Config   │
│ 📈 History      │
│ 👤 Account      │
│                 │
│ 🚪 Sign Out     │
└─────────────────┘
```

**Main Content**:
- Welcome message
- Quick stats (projects, analyses)
- Recent activity
- Quick actions

### 5. Projects Page (`/projects`)
**Features**:
- List all user's indexed projects
- [+ New Project] button
- Each project card shows:
  - Name, path, file count
  - Last indexed time
  - Actions: View, Re-index, Delete
- Click to view project details

### 6. Project Details (`/projects/<id>`)
**Tabs**:
- Overview (stats, metrics)
- Files (browse indexed files)
- Functions (search functions)
- Classes (search classes)
- Dependencies (dependency graph)
- Analysis (run analyses)

### 7. Analysis Page (`/analysis`)
**Analysis Types**:
- Dead Code Detection
- Complexity Analysis
- Security Scan
- Dependency Analysis
- Code Smells
- Performance Hotspots

**Workflow**:
1. Select project
2. Select analysis type
3. Configure parameters
4. Run analysis
5. View results
6. Export/Save

### 8. API Configuration (`/settings/api`)
**Features**:
- Add/Edit AI providers
- List of configured providers:
  - Ollama (local)
  - Groq (free tier)
  - OpenAI
  - Anthropic
  - Google Gemini
  - DeepSeek
- For each provider:
  - API Key field (masked)
  - Model selection dropdown
  - Test Connection button
  - Set as Default checkbox
  - Delete button

### 9. Account Settings (`/settings/account`)
**Sections**:
- Profile Information (name, email, username)
- Change Password
- Email Preferences
- Delete Account
- Session Management (view active sessions)

### 10. History Page (`/history`)
**Features**:
- Table of all past analyses
- Filters: date range, project, analysis type
- Each row: timestamp, project, type, results summary
- Click to view detailed results

---

## 🔐 Authentication Flow

### Sign Up Flow
```
1. User visits /signup
2. Fills form (validation on submit)
3. Server validates:
   - Username unique
   - Email unique & valid
   - Password strength (8+ chars, mix)
4. Hash password with bcrypt
5. Create user record
6. Send welcome email (optional)
7. Auto sign-in
8. Redirect to /dashboard
```

### Sign In Flow
```
1. User visits /signin
2. Enters credentials
3. Server validates:
   - User exists
   - Password correct (bcrypt verify)
4. Create session (Flask-Login)
5. Update last_login timestamp
6. Redirect to /dashboard
```

### Session Management
```
- Use Flask-Login for session handling
- Store session in secure cookie
- Set session timeout (24 hours)
- "Remember Me" extends to 30 days
- CSRF protection on all forms
```

---

## 🛠️ Implementation Plan

### Phase 1: Setup & Authentication (Priority 1)
**Files to Create/Modify**:
```
orc/web/
├── models.py              # NEW - SQLAlchemy models
├── forms.py               # NEW - WTForms
├── auth.py                # NEW - Authentication routes
├── database.py            # NEW - Database initialization
├── app.py                 # MODIFY - Add auth integration
└── templates/
    ├── base.html          # NEW - Base template with sidebar
    ├── landing.html       # NEW - Landing page
    ├── auth/
    │   ├── signup.html    # NEW
    │   ├── signin.html    # NEW
    │   └── forgot.html    # NEW (optional)
    └── dashboard/
        └── home.html      # NEW - Dashboard home
```

**Tasks**:
1. Install dependencies (Flask-Login, Flask-SQLAlchemy, Flask-Bcrypt, Flask-WTF)
2. Create database models
3. Create authentication forms
4. Build landing page
5. Build signup/signin pages
6. Implement authentication logic
7. Add session management

### Phase 2: Core Dashboard (Priority 2)
**Files to Create/Modify**:
```
orc/web/
├── static/
│   ├── css/
│   │   ├── theme.css      # NEW - Black/Green theme
│   │   ├── sidebar.css    # NEW - Sidebar styles
│   │   └── dashboard.css  # MODIFY - Update colors
│   ├── js/
│   │   ├── main.js        # NEW - Common JS
│   │   └── dashboard.js   # NEW - Dashboard interactions
│   └── images/
│       └── orclogo.png    # COPY from assets/
└── templates/
    ├── components/
    │   ├── sidebar.html   # NEW - Reusable sidebar
    │   └── navbar.html    # NEW - Top navbar
    └── dashboard/
        └── home.html      # MODIFY - Add real content
```

**Tasks**:
1. Copy logo to web/static/images/
2. Create black/green CSS theme
3. Build sidebar component
4. Build dashboard home with stats
5. Add navigation
6. Implement user menu

### Phase 3: Projects Management (Priority 3)
**Files to Create/Modify**:
```
orc/web/
├── projects.py            # NEW - Project routes
├── templates/
│   └── projects/
│       ├── list.html      # NEW - Projects list
│       ├── detail.html    # NEW - Project detail
│       ├── new.html       # NEW - New project form
│       └── components/
│           └── project_card.html  # NEW
```

**Tasks**:
1. Create project CRUD operations
2. Build project listing page
3. Build project detail page
4. Integrate with existing indexer
5. Add re-index functionality

### Phase 4: API Configuration (Priority 4)
**Files to Create/Modify**:
```
orc/web/
├── api_config.py          # NEW - API config routes
├── templates/
│   └── settings/
│       ├── api.html       # NEW - API configuration
│       └── account.html   # NEW - Account settings
```

**Tasks**:
1. Create API config model & routes
2. Build provider configuration UI
3. Add "Test Connection" functionality
4. Integrate with existing AI clients
5. Allow per-project provider selection

### Phase 5: Analysis Features (Priority 5)
**Files to Create/Modify**:
```
orc/web/
├── analysis.py            # NEW - Analysis routes
├── templates/
│   └── analysis/
│       ├── run.html       # NEW - Run analysis
│       ├── results.html   # NEW - View results
│       └── history.html   # NEW - Analysis history
```

**Tasks**:
1. Create analysis UI workflow
2. Integrate with existing analyzers
3. Add real-time progress updates
4. Build results visualization
5. Add export functionality

### Phase 6: Polish & Features (Priority 6)
**Additional Features**:
- User preferences
- Dark/light mode toggle (already dark!)
- Email notifications
- Export reports (PDF/JSON)
- Keyboard shortcuts
- Search functionality
- Activity feed
- Collaboration features (share projects)

---

## 📦 New Dependencies

Add to `requirements.txt`:
```
Flask-Login>=0.6.2
Flask-SQLAlchemy>=3.0.5
Flask-Bcrypt>=1.0.1
Flask-WTF>=1.1.1
WTForms>=3.0.1
email-validator>=2.0.0
```

Add to `setup.py` extras:
```python
extras_require={
    'web': [
        'flask>=2.0.0',
        'gunicorn>=20.1.0',
        'flask-login>=0.6.2',
        'flask-sqlalchemy>=3.0.5',
        'flask-bcrypt>=1.0.1',
        'flask-wtf>=1.1.1',
        'email-validator>=2.0.0',
    ],
}
```

---

## 🎯 Features Summary

### Core Features
- ✅ User authentication (signup, signin, logout)
- ✅ User dashboard with sidebar navigation
- ✅ Project management (create, index, view, delete)
- ✅ API provider configuration (multiple AI providers)
- ✅ Analysis execution (dead code, complexity, etc.)
- ✅ Analysis history & results viewing
- ✅ Account settings & preferences
- ✅ Professional landing page

### Design Features
- ✅ Black & green color scheme
- ✅ ORC logo integration
- ✅ Responsive design
- ✅ Modern, clean UI
- ✅ Sidebar navigation
- ✅ Professional typography

### Security Features
- ✅ Password hashing (bcrypt)
- ✅ CSRF protection
- ✅ Session management
- ✅ Secure cookie handling
- ✅ API key encryption (stored masked)
- ✅ Input validation

---

## 📐 File Structure (Final)

```
orc/web/
├── __init__.py
├── app.py                 # Main Flask app
├── app_prod.py            # Production app
├── models.py              # Database models
├── forms.py               # WTForms
├── auth.py                # Authentication routes
├── projects.py            # Project routes
├── analysis.py            # Analysis routes
├── api_config.py          # API configuration routes
├── database.py            # Database initialization
│
├── static/
│   ├── css/
│   │   ├── theme.css      # Black/green theme
│   │   ├── sidebar.css    # Sidebar styles
│   │   ├── forms.css      # Form styles
│   │   └── dashboard.css  # Dashboard styles
│   ├── js/
│   │   ├── main.js        # Common functionality
│   │   ├── dashboard.js   # Dashboard interactions
│   │   └── analysis.js    # Analysis page logic
│   └── images/
│       ├── orclogo.png    # Main logo
│       ├── favicon.svg    # Favicon
│       └── patterns/      # Background patterns
│
└── templates/
    ├── base.html          # Base template
    ├── landing.html       # Landing page
    │
    ├── auth/
    │   ├── signup.html
    │   ├── signin.html
    │   └── forgot.html
    │
    ├── dashboard/
    │   └── home.html      # Dashboard home
    │
    ├── projects/
    │   ├── list.html      # Projects list
    │   ├── detail.html    # Project details
    │   └── new.html       # New project
    │
    ├── analysis/
    │   ├── run.html       # Run analysis
    │   ├── results.html   # Results viewer
    │   └── history.html   # Analysis history
    │
    ├── settings/
    │   ├── api.html       # API configuration
    │   └── account.html   # Account settings
    │
    └── components/
        ├── sidebar.html   # Reusable sidebar
        ├── navbar.html    # Top navbar
        └── cards/         # Reusable card components
```

---

## 🚀 Quick Start Commands

After building:
```bash
# Install dependencies
pip install -e ".[web]"

# Initialize database
python -c "from orc.web.database import init_db; init_db()"

# Run development server
python orc/web/app.py

# Or run production server
gunicorn -w 4 -b 0.0.0.0:8000 orc.web.app_prod:app
```

---

## ✅ Success Criteria

### Functional Requirements
- [ ] Users can sign up with email/username/password
- [ ] Users can sign in and sign out
- [ ] Users see a personalized dashboard
- [ ] Users can create and manage projects
- [ ] Users can configure AI API providers
- [ ] Users can run code analyses
- [ ] Users can view analysis results and history
- [ ] Users can update account settings

### Design Requirements
- [ ] Black background (#0a0a0a) throughout
- [ ] Green accents (#00ff41) for primary actions
- [ ] ORC logo visible on all pages
- [ ] Sidebar navigation on dashboard pages
- [ ] Responsive design (desktop focus, mobile friendly)
- [ ] Professional, modern look
- [ ] Smooth transitions and hover effects

### Technical Requirements
- [ ] Secure authentication (bcrypt, sessions)
- [ ] CSRF protection on all forms
- [ ] Input validation and sanitization
- [ ] API keys stored securely
- [ ] Database migrations supported
- [ ] Error handling and user feedback
- [ ] Production-ready configuration

---

## 📊 Estimated Timeline

**Phase 1** (Auth & Landing): 3-4 hours  
**Phase 2** (Dashboard): 2-3 hours  
**Phase 3** (Projects): 2-3 hours  
**Phase 4** (API Config): 1-2 hours  
**Phase 5** (Analysis): 2-3 hours  
**Phase 6** (Polish): 1-2 hours  

**Total**: 11-17 hours of focused development

---

## 🎨 Design Preview

### Color Usage
```
Background:      #0a0a0a (black)
Cards/Panels:    #1a1a1a (dark gray)
Primary Button:  #00ff41 (green)
Hover State:     #00cc33 (darker green)
Text:            #ffffff (white)
Secondary Text:  #b0b0b0 (gray)
Links:           #00ff88 (light green)
```

### Sample Component (Button)
```css
.btn-primary {
    background: #00ff41;
    color: #0a0a0a;
    border: none;
    padding: 12px 24px;
    font-weight: 600;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.3s ease;
}

.btn-primary:hover {
    background: #00cc33;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 255, 65, 0.3);
}
```

---

## ❓ Questions for Clarification

1. **User Roles**: Do you want admin/user roles, or single role for all?
2. **Email Verification**: Should users verify email after signup?
3. **Password Reset**: Implement forgot password functionality?
4. **Project Sharing**: Can users share projects with other users?
5. **Payment/Tiers**: Free only, or paid tiers with limits?
6. **API Rate Limiting**: Limit analysis runs per user?
7. **Data Retention**: How long to keep analysis history?
8. **Export Formats**: What formats for exporting results (PDF, JSON, CSV)?

---

**Ready to Build?** Let me know if you approve this plan and I'll start implementation! 🚀
