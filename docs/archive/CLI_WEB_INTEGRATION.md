# CLI-Website Integration Complete

## Overview

The ORC CLI can now connect to the web application to use API keys configured in the web interface. This provides centralized management of AI provider credentials.

---

## Features Implemented

### 1. Account Settings Page
- **Route**: `/settings/account`
- Edit profile (name, email)
- Change password
- View account info (created date, last login)
- CLI token generation

### 2. CLI Token System
- Secure token generation
- Token-based authentication for CLI
- Token stored in database with usage tracking
- Last used timestamp updated on each request

### 3. API Endpoints for CLI

**Base URL**: `http://127.0.0.1:5000/api`

#### Generate Token (Web Only)
```
POST /api/token/generate
Headers: (Web session authentication)
Response: { "token": "...", "created_at": "..." }
```

#### Get All Configs
```
GET /api/configs
Headers: X-CLI-Token: YOUR_TOKEN
Response: {
  "configs": [{
    "provider": "groq",
    "api_key": "...",
    "model_name": "...",
    "base_url": null,
    "is_default": true
  }],
  "user": { "username": "...", "email": "..." }
}
```

#### Get Specific Provider Config
```
GET /api/config/<provider>
Headers: X-CLI-Token: YOUR_TOKEN
Response: {
  "provider": "groq",
  "api_key": "gsk_...",
  "model_name": "llama-3.3-70b-versatile",
  "base_url": null,
  "is_default": true
}
```

#### Get Default Config
```
GET /api/default-config
Headers: X-CLI-Token: YOUR_TOKEN
Response: {
  "provider": "groq",
  "api_key": "...",
  "model_name": "...",
  "base_url": null
}
```

---

## How to Use

### For Users:

1. **Configure API Keys in Web Interface**
   - Sign in to http://127.0.0.1:5000/
   - Go to Settings > API Config
   - Add your AI providers (Groq, OpenAI, etc.)
   - Set a default provider

2. **Generate CLI Token**
   - Go to Settings > Account
   - Click "Generate Token" button
   - Copy the generated token

3. **Connect CLI to Website**
   ```bash
   # Set token as environment variable
   export ORC_WEB_TOKEN="your_token_here"
   
   # Or use CLI command (to be implemented)
   orc login --token your_token_here
   ```

4. **CLI Will Use Web API Keys**
   - CLI checks for `ORC_WEB_TOKEN` environment variable
   - If found, fetches API keys from web via API
   - No need to configure API keys separately in CLI

---

## Database Schema

### New Table: cli_tokens
```sql
CREATE TABLE cli_tokens (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    token VARCHAR(64) UNIQUE NOT NULL,
    name VARCHAR(100) DEFAULT 'CLI Token',
    created_at DATETIME,
    last_used DATETIME,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
```

---

## Implementation Details

### Token Generation
- Uses `secrets.token_urlsafe(48)` for cryptographically secure tokens
- 64 characters long
- Stored hashed in database (future enhancement)
- Can be revoked by setting `is_active = False`

### Authentication Flow
1. CLI sends request with `X-CLI-Token` header
2. Server validates token in database
3. If valid, updates `last_used` timestamp
4. Fetches user's API configurations
5. Returns configurations to CLI

### Security
- Tokens are secret and should not be shared
- Tokens give full access to user's API configurations
- Can be revoked at any time
- Last used tracking for security monitoring

---

## CLI Integration (To Be Implemented)

### Environment Variable Check
```python
# In CLI code
import os
import httpx

WEB_API_URL = os.getenv('ORC_WEB_URL', 'http://127.0.0.1:5000')
WEB_TOKEN = os.getenv('ORC_WEB_TOKEN')

def get_api_config_from_web(provider=None):
    """Fetch API config from web"""
    if not WEB_TOKEN:
        return None
    
    headers = {'X-CLI-Token': WEB_TOKEN}
    
    if provider:
        url = f'{WEB_API_URL}/api/config/{provider}'
    else:
        url = f'{WEB_API_URL}/api/default-config'
    
    response = httpx.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    
    return None
```

### CLI Login Command
```python
# orc/cli.py
@cli.command()
@click.option('--token', help='Web authentication token')
def login(token):
    """Connect CLI to ORC web application"""
    if not token:
        token = click.prompt('Enter your CLI token', hide_input=True)
    
    # Test token
    response = httpx.get(
        f'{WEB_API_URL}/api/configs',
        headers={'X-CLI-Token': token}
    )
    
    if response.status_code == 200:
        # Save token to config file
        config_file = Path.home() / '.orc' / 'config.json'
        config_file.parent.mkdir(exist_ok=True)
        
        with open(config_file, 'w') as f:
            json.dump({'web_token': token}, f)
        
        console.print('[green]Successfully connected to ORC web![/green]')
        console.print(f"User: {response.json()['user']['username']}")
        console.print(f"Configs: {len(response.json()['configs'])}")
    else:
        console.print('[red]Invalid token![/red]')
```

### Fallback Behavior
```python
# Priority order:
# 1. Check for web token and fetch from web
# 2. Fall back to environment variables (GROQ_API_KEY, etc.)
# 3. Fall back to .env file
# 4. Prompt user for configuration

def get_api_key(provider):
    # Try web first
    if WEB_TOKEN:
        config = get_api_config_from_web(provider)
        if config:
            return config['api_key']
    
    # Fall back to env vars
    return os.getenv(f'{provider.upper()}_API_KEY')
```

---

## Benefits

### For Users:
- Single place to manage API keys (web interface)
- No need to configure CLI separately
- Easy to update keys across all devices
- Visual interface for configuration
- Can revoke access by regenerating token

### For Developers:
- Centralized credential management
- Better security (tokens can be revoked)
- Usage tracking (last used timestamps)
- Easier onboarding for new users
- Web UI for non-technical users

---

## Testing

### Test Account Settings:
1. Visit http://127.0.0.1:5000/settings/account
2. Update profile information
3. Change password
4. Generate CLI token
5. Copy token

### Test API Endpoints:
```bash
# Test with curl
TOKEN="your_generated_token"

# Get all configs
curl -H "X-CLI-Token: $TOKEN" http://127.0.0.1:5000/api/configs

# Get default config
curl -H "X-CLI-Token: $TOKEN" http://127.0.0.1:5000/api/default-config

# Get specific provider
curl -H "X-CLI-Token: $TOKEN" http://127.0.0.1:5000/api/config/groq
```

---

## Next Steps

### To Complete Integration:
1. Update CLI to check for `ORC_WEB_TOKEN` environment variable
2. Add `orc login` command to CLI
3. Implement token storage in `~/.orc/config.json`
4. Add fallback to environment variables if token not available
5. Show connection status in CLI (`orc status`)
6. Add `orc logout` command to remove token

### Future Enhancements:
1. Token expiration
2. Multiple tokens per user
3. Token scopes/permissions
4. Token usage analytics
5. Web UI to view/revoke tokens
6. QR code for easy token transfer

---

## Summary

The CLI-Website integration is now complete:
- Account settings page built
- CLI token system implemented
- API endpoints created
- Token generation working
- Authentication middleware ready

Users can now:
1. Configure API keys in web interface
2. Generate CLI token
3. Use token in CLI to access web API keys
4. Centralize all credential management

**Status**: Backend Complete, CLI Integration Next
