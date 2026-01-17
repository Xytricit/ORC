# Using AI Chat with ORC

Learn how to use ORC's AI-powered chat to understand and improve your codebase.

## Prerequisites

- ORC installed and indexed project
- AI API key (Groq, OpenAI, Anthropic, or DeepSeek)
- Indexed codebase (`orc index`)

## Setup AI Provider

### Option 1: Environment Variables

Create or edit `.env` file in your project:

```bash
# Choose one or more providers
GROQ_API_KEY=gsk_your_key_here
OPENAI_API_KEY=sk-your_key_here
ANTHROPIC_API_KEY=sk-ant-your_key_here
DEEPSEEK_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
```

### Option 2: Web Interface

1. Start web interface: `orc web`
2. Go to Settings → API Configuration
3. Add your API key(s)
4. Select default provider and model
5. Click Save

### Option 3: Config File

Edit `.orc/config.yaml`:

```yaml
ai:
  provider: groq  # or openai, anthropic, deepseek
  model: mixtral-8x7b-32768
  api_key: ${GROQ_API_KEY}  # or set directly (not recommended)
  max_context_tokens: 8000
  temperature: 0.7
```

## Getting API Keys

### Groq (Recommended - Fast & Free)

1. Visit: https://console.groq.com
2. Sign up for free account
3. Go to API Keys section
4. Create new API key
5. Copy and save it

**Models available:**
- `mixtral-8x7b-32768` - Best for code
- `llama-3.1-70b-versatile` - Most powerful
- `gemma-7b-it` - Lightweight

### OpenAI

1. Visit: https://platform.openai.com
2. Sign up and add payment method
3. Go to API Keys
4. Create new key

**Models:**
- `gpt-4` - Most capable (expensive)
- `gpt-3.5-turbo` - Fast and affordable

### Anthropic

1. Visit: https://console.anthropic.com
2. Sign up for account
3. Request API access
4. Create API key

**Models:**
- `claude-3-opus` - Most capable
- `claude-3-sonnet` - Balanced
- `claude-3-haiku` - Fast

## Starting Chat (CLI)

### Interactive Mode

```bash
orc chat
```

You'll enter an interactive session:

```
🤖 ORC AI Assistant
💡 Ask me anything about your codebase!
📊 Context: 543 functions, 89 classes indexed

You: 
```

### One-off Query

```bash
orc chat "Explain what the authentication system does"
```

## Starting Chat (Web)

1. Open web interface: `orc web`
2. Click "AI Assistant" in sidebar
3. Select project from dropdown
4. Type your question
5. Press Enter

## Example Questions

### Understanding Code

```
You: What does the User model do?

🤖: The User model is defined in src/models/user.py and represents 
a user in the system. It includes:

- Fields: username, email, password_hash, created_at
- Methods: check_password(), set_password(), to_dict()
- Relationships: one-to-many with Posts

It's used for authentication and storing user data.
```

### Finding Functionality

```
You: Find all database queries

🤖: I found 15 database queries in your codebase:

1. src/database/users.py:23
   SELECT * FROM users WHERE id = ?
   
2. src/database/posts.py:45
   INSERT INTO posts (title, content) VALUES (?, ?)
   
[... more results ...]
```

### Getting Recommendations

```
You: How can I optimize the process_data function?

🤖: The process_data function in src/utils.py could be optimized:

Current issues:
- Uses nested loops (O(n²) complexity)
- Loads entire dataset into memory
- No caching

Recommendations:
1. Use list comprehension instead of nested loops
2. Process data in chunks
3. Add LRU cache decorator

Here's an optimized version:
[code example]
```

### Architecture Questions

```
You: Explain the authentication flow

🤖: The authentication flow works as follows:

1. User submits credentials (login.py:45)
2. Credentials validated against database (auth.py:89)
3. JWT token generated (jwt_utils.py:23)
4. Token stored in session (session.py:67)
5. Protected routes check token (middleware.py:34)

Key files:
- src/auth/login.py - Login handling
- src/auth/jwt_utils.py - Token management
- src/middleware/auth.py - Protection middleware
```

### Debugging Help

```
You: Why is the API response slow?

🤖: I identified several performance issues in your API:

1. N+1 query problem in get_users (api/users.py:45)
   - Makes separate queries for each user's posts
   - Fix: Use JOIN or prefetch_related

2. No caching on frequent endpoint (api/stats.py:23)
   - Stats recalculated on every request
   - Fix: Add Redis caching

3. Large JSON payloads (api/responses.py:67)
   - Returns unnecessary fields
   - Fix: Use pagination and field selection

[Detailed examples for each fix...]
```

## Interactive Chat Commands

### `/help`

Show available commands:

```
You: /help

Available commands:
  /help       - Show this help
  /clear      - Clear conversation history
  /context    - Show current context size
  /model      - Change AI model
  /exit       - Exit chat
```

### `/clear`

Clear conversation history:

```
You: /clear
🗑️  Conversation cleared
```

### `/context`

Show context information:

```
You: /context

📊 Current Context:
  - Tokens used: 2,345 / 8,000
  - Files in context: 23
  - Functions in context: 127
  - Classes in context: 18
```

### `/model`

Change AI model:

```
You: /model gpt-4
✅ Switched to model: gpt-4
```

### `/exit`

Exit chat:

```
You: /exit
👋 Goodbye!
```

## Advanced Usage

### Custom Context Size

Reduce context for faster responses:

```bash
orc chat --context-size 4000
```

### Specific Model

Use a specific model:

```bash
orc chat --model gpt-4 --provider openai
```

### Focus on Specific Files

```bash
# Chat about specific module
orc chat "Explain the auth module" --focus src/auth/
```

## Tips for Better Results

### 1. Be Specific

❌ Bad: "Fix my code"
✅ Good: "Optimize the process_data function for large datasets"

### 2. Provide Context

❌ Bad: "Why is it slow?"
✅ Good: "Why is the /api/users endpoint slow when fetching 1000+ users?"

### 3. Ask Follow-up Questions

```
You: Explain the database schema
🤖: [Explains schema]

You: How are users and posts related?
🤖: [Detailed explanation of relationship]

You: Show me an example query
🤖: [Provides SQL example]
```

### 4. Request Code Examples

```
You: Show me how to add caching to the API
🤖: [Provides code example]

You: Can you show the same thing using Redis instead?
🤖: [Provides Redis example]
```

### 5. Use for Learning

```
You: I'm new to this codebase. What should I know?

🤖: Here's an overview of the key components:

1. Architecture: MVC pattern
2. Main modules:
   - auth: User authentication
   - api: REST API endpoints
   - database: DB models and queries
3. Key flows:
   - User registration: ...
   - Data processing: ...
[...]
```

## Common Use Cases

### Code Review

```
You: Review the changes in src/api/users.py
```

### Refactoring Advice

```
You: This function is too complex. How can I refactor it?
```

### Testing Help

```
You: Write unit tests for the authenticate function
```

### Documentation

```
You: Generate docstrings for the User class
```

### Security Review

```
You: Check for security issues in the authentication code
```

## Web Interface Chat Features

### Conversation History

- View past conversations
- Resume previous chats
- Search through history

### Code Highlighting

- Automatic syntax highlighting
- Copy code button
- Expandable code blocks

### Project Context

- Select specific project
- Switch between projects mid-conversation
- Project-specific context

### Export Conversations

- Export to Markdown
- Export to PDF
- Share with team

## Troubleshooting

### "API key not found"

**Solution:**
```bash
# Check environment variable
echo $GROQ_API_KEY

# Set it if missing
export GROQ_API_KEY=your_key_here

# Or add to .env file
```

### "Context too large"

**Solution:**
```bash
# Reduce context size
orc chat --context-size 4000

# Or exclude files in .orcignore
```

### "Slow responses"

**Solution:**
```bash
# Use faster model
orc chat --model mixtral-8x7b-32768 --provider groq

# Or reduce context
orc chat --context-size 2000
```

### "Inaccurate answers"

**Possible causes:**
1. Codebase not indexed: Run `orc index`
2. Old index: Run `orc index --rebuild`
3. Model not suitable: Try different model

## Best Practices

1. **Index First** - Always index before chatting
2. **Keep Index Updated** - Reindex after major changes
3. **Start Broad** - Ask overview questions first
4. **Then Narrow** - Follow up with specific questions
5. **Verify Code** - Always review AI-generated code
6. **Use Context Commands** - Monitor token usage
7. **Save Important Answers** - Export conversations

## Privacy & Security

- **Local Analysis** - Code analysis runs locally
- **API Calls** - Only chat queries sent to AI providers
- **No Training** - Your code isn't used to train models (check provider TOS)
- **Encryption** - API keys encrypted in database

## Cost Management

### Free Options

- **Groq** - Free tier with generous limits
- **OpenAI** - $5 free credit for new users

### Cost-Effective Strategies

1. Use free tier (Groq) for development
2. Switch to paid (GPT-4) for production
3. Reduce context size to save tokens
4. Cache common queries (web interface does this)

## Next Steps

- [Finding Dead Code](dead_code.md) - Use AI to identify dead code
- [Performance Optimization](performance.md) - AI-powered optimization
- [Configuration](../configuration.md) - Configure AI settings

## Summary

You've learned to:
- ✅ Set up AI providers
- ✅ Use interactive chat (CLI & Web)
- ✅ Ask effective questions
- ✅ Use chat commands
- ✅ Get code recommendations
- ✅ Troubleshoot issues

Happy chatting! 🤖
