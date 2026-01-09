# ORC Authentication Model - Updated

## New Authentication Model

The authentication system has been updated to be **optional** - users can use basic ORC features without logging in, and only need authentication for AI-powered features.

---

## Commands by Authentication Level

### No Authentication Required ✓

These commands work **immediately** without any login:

```bash
# Indexing
orc index .              # Index your codebase
orc stats                # View statistics

# Analysis
orc dead                 # Find dead code
orc complexity           # Complexity analysis
orc query pattern        # Search code
orc hotspots             # Find complexity hotspots
orc analyze              # Full analysis

# Configuration
orc init                 # Initialize ORC
orc config show          # Show config
orc ignore pattern       # Add ignore patterns
```

**These use local analysis only** - no AI, no web connection needed.

### Authentication Required 🔒

These commands require login because they use AI providers:

```bash
# AI Features
orc chat                 # AI assistant (uses configured AI provider)

# Authentication Management
orc login                # Connect to web
orc logout               # Sign out
orc status               # Check auth status
```

---

## Why This Model?

### Benefits:

1. **Immediate Use** - Users can start using ORC right away
2. **Privacy** - Basic analysis is 100% local, no account needed
3. **Flexible** - Only create account when you want AI features
4. **Gradual Onboarding** - Try ORC first, sign up later
5. **Offline Capable** - Basic features work without internet

### When to Login:

Create an account and login when you want to:
- Use the **AI chat assistant** for code questions
- Get **AI-powered suggestions** and recommendations
- Manage **API keys centrally** in the web interface
- Access your data from **both CLI and web**
- **Sync projects** across devices (future feature)

---

## User Flows

### Flow 1: Quick Start (No Account)

```bash
# User wants to analyze code quickly
orc index .
orc dead
orc complexity

# All works immediately!
# No signup, no login, no waiting
```

### Flow 2: AI-Powered Analysis (With Account)

```bash
# User wants AI assistance
orc chat
# Shows: Authentication Required

# User creates account
# 1. Visit http://127.0.0.1:5000/
# 2. Sign up
# 3. Configure AI provider (e.g., Groq)
# 4. Generate CLI token
# 5. Run: orc login

# Now AI features work
orc chat
# AI assistant starts!
```

---

## Technical Implementation

### Basic Commands
- Check for local `.orc/index.db`
- Perform analysis using local tools
- No API calls, no authentication checks
- Fast and private

### AI Commands
- Check for authentication token in `~/.orc/config.json`
- If not found, show login prompt with instructions
- If found, validate token with web API
- Fetch AI provider configuration from web
- Use configured AI provider

---

## Authentication Check Logic

```python
# Basic command (no auth)
def index(path):
    # No authentication check
    # Works immediately
    index_directory(path)

# AI command (requires auth)
def chat():
    # Check authentication
    require_auth()  # Shows login prompt if not authenticated
    # Continue with AI features
    start_ai_chat()
```

---

## User Experience

### New User Experience:
1. Install ORC: `pip install orc-cli`
2. Run: `orc index .`
3. Immediate results! No barriers.
4. When ready for AI: `orc login`

### Existing User Experience:
- Already logged in
- All commands work seamlessly
- No change in workflow

---

## Commands Summary

| Command | Auth Required | Purpose |
|---------|--------------|---------|
| `orc index` | ❌ No | Index codebase |
| `orc stats` | ❌ No | Show statistics |
| `orc dead` | ❌ No | Find dead code |
| `orc complexity` | ❌ No | Complexity analysis |
| `orc query` | ❌ No | Search code |
| `orc hotspots` | ❌ No | Find hotspots |
| `orc analyze` | ❌ No | Full analysis |
| `orc chat` | ✅ Yes | AI assistant |
| `orc login` | ❌ No | Connect to web |
| `orc logout` | ❌ No | Sign out |
| `orc status` | ❌ No | Check auth |

---

## Testing

### Test Without Authentication:
```bash
# Make sure not logged in
orc logout

# Test basic commands
orc index .
# Should work ✓

orc stats
# Should work ✓

orc dead
# Should work ✓

orc chat
# Should show: Authentication Required ✓
```

### Test With Authentication:
```bash
# Login
orc login

# Test AI commands
orc chat
# Should work ✓
```

---

## Migration Notes

### For Existing Users:
- Already logged in users see no change
- All commands continue to work
- Token still valid

### For New Users:
- Can use ORC immediately
- No account needed for basic features
- Optional signup for AI features

---

## Future Enhancements

### Potential Features:
1. **Offline AI** - Use local Ollama without web account
2. **Hybrid Mode** - Some AI features work without account
3. **Guest Mode** - Limited AI usage without signup
4. **Trial Credits** - Free AI queries before signup
5. **Anonymous Usage** - Basic stats tracking without account

---

## Comparison

### Before (Full Auth):
```
User: orc index .
ORC: Authentication Required. Please login.
User: *has to create account first*
```

### After (Optional Auth):
```
User: orc index .
ORC: *indexes immediately*
User: orc chat
ORC: Authentication Required for AI features.
```

**Much better UX!** Users can try ORC without commitment.

---

## Status

**Implementation:** COMPLETE  
**Testing:** VERIFIED  
**User Experience:** IMPROVED  
**Flexibility:** MAXIMUM  

---

The authentication model is now **flexible and user-friendly** - immediate access to core features, optional account for AI enhancements.
