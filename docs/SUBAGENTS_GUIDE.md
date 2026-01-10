# ORC SubAgents - Build Your AI Dev Team

Create specialized AI agents that work together in your terminal. Each agent has custom training, expertise, and personality.

## 🎯 What are SubAgents?

SubAgents are specialized instances of ORC that you can create and customize for specific tasks. Think of it like hiring different developers for your team:

- **Security Auditor** - Finds vulnerabilities and security issues
- **Performance Expert** - Optimizes code for speed
- **Code Reviewer** - Reviews PRs like a senior dev
- **Documentation Writer** - Generates comprehensive docs
- **Testing Specialist** - Writes tests and finds edge cases
- **Refactoring Expert** - Improves code structure

Each agent has:
- ✅ **Custom training** - Specialized knowledge and instructions
- ✅ **Unique personality** - Professional, friendly, strict, or teacher
- ✅ **Tool access** - All tools, read-only, or custom selection
- ✅ **Persistent memory** - Each agent has `orc_<name>.md` file
- ✅ **Independent context** - Doesn't interfere with other agents

## 🚀 Quick Start

### Create Your First Agent

```bash
# Start ORC
orc

# Create a new agent
/create-agent

# Follow the interactive wizard:
# - Name: security_auditor
# - Role: Security Expert
# - Expertise: security, authentication, encryption
# - Personality: 3 (strict)
# - Custom training: Focus on OWASP Top 10...
# - Tools: All tools
# - Creativity: 0.3 (focused)
```

### Switch to Agent

```bash
# Switch to an agent
/agent security_auditor

# Now all your messages go to this agent
[security_auditor] You: audit my authentication system
```

### Mention Agent

```bash
# Mention an agent without switching
You: @security_auditor check this login function

# Works across sessions and terminals!
# Agent responds with their specialized knowledge
```

### List All Agents

```bash
/list-agents

# Output:
# 🤖 Your SubAgent Dev Team:
#
# ▶ security_auditor (active)
#   Role: Security Expert
#   Expertise: security, authentication
#   Personality: strict
#
#   code_reviewer
#   Role: Senior Code Reviewer
#   Expertise: best practices, clean code
#   Personality: professional
```

## 📝 Creating Agents

### Interactive Creation

The easiest way - just follow the prompts:

```bash
/create-agent
```

**Wizard Steps:**

1. **Agent Name**
   - Use alphanumeric, underscores, hyphens
   - Examples: `security_auditor`, `perf-expert`, `docs_writer`
   - Avoid: `main`, `orc`, `default` (reserved)

2. **Role/Title**
   - What is this agent?
   - Examples: "Security Auditor", "Performance Expert", "Code Reviewer"

3. **Expertise Areas**
   - Comma-separated specializations
   - Examples: `security,authentication,encryption` or `performance,optimization,caching`

4. **Personality**
   - **Professional** (1): Formal, detailed responses
   - **Friendly** (2): Casual, encouraging tone
   - **Strict** (3): Critical, thorough analysis
   - **Teacher** (4): Explanatory, patient guidance

5. **Custom Training**
   - Multi-line instructions for the agent
   - Define what the agent should focus on
   - Press Enter twice when done

   Example:
   ```
   You are a security expert specializing in web application security.
   Always check for:
   - SQL injection vulnerabilities
   - XSS attacks
   - CSRF protection
   - Authentication flaws
   - Authorization issues
   
   Provide specific code examples and fixes.
   Reference OWASP guidelines when relevant.
   ```

6. **Tool Access**
   - **All tools** (1): Full access
   - **Read-only** (2): Stats, search, query only
   - **Custom** (3): Specify exact tools

7. **Creativity Level**
   - 0.0 - 0.3: Focused, deterministic (good for audits)
   - 0.4 - 0.7: Balanced (good for general tasks)
   - 0.8 - 1.0: Creative (good for brainstorming)

## 🎨 Example Agents

### Security Auditor

```
Name: security_auditor
Role: Security Expert
Expertise: security, vulnerabilities, OWASP
Personality: strict
Training: |
  Focus on finding security vulnerabilities.
  Check for: SQL injection, XSS, CSRF, auth issues.
  Provide specific fixes with code examples.
  Reference OWASP Top 10.
Tools: All
Temperature: 0.3
```

**Usage:**
```bash
/agent security_auditor
You: audit my login endpoint
```

### Performance Optimizer

```
Name: perf_optimizer
Role: Performance Expert
Expertise: optimization, caching, algorithms
Personality: professional
Training: |
  Analyze code for performance bottlenecks.
  Suggest optimizations for:
  - Algorithm complexity
  - Database queries
  - Caching strategies
  - Memory usage
  Provide benchmarks when possible.
Tools: All
Temperature: 0.5
```

### Code Reviewer

```
Name: code_reviewer
Role: Senior Code Reviewer
Expertise: best practices, clean code, design patterns
Personality: strict
Training: |
  Review code like a senior developer.
  Check for:
  - Code smells
  - Design pattern violations
  - Naming conventions
  - Documentation quality
  - Test coverage
  Be constructive but thorough.
Tools: All
Temperature: 0.4
```

### Documentation Writer

```
Name: docs_writer
Role: Documentation Specialist
Expertise: documentation, technical writing, API docs
Personality: teacher
Training: |
  Generate clear, comprehensive documentation.
  Include:
  - Function/class descriptions
  - Parameter details
  - Return values
  - Usage examples
  - Edge cases
  Write for both beginners and experts.
Tools: Read-only
Temperature: 0.6
```

## 💼 Workflow Examples

### Security Review Workflow

```bash
# Start ORC
orc

# Create security agent (one time)
/create-agent
# ...setup security_auditor...

# Use it for audits
/agent security_auditor
[security_auditor] You: review my authentication system
[security_auditor] You: check for SQL injection in user_queries.py
[security_auditor] You: audit the payment processing flow
```

### Multi-Agent Code Review

```bash
# Switch between different expert agents
/agent security_auditor
You: check for security issues

/agent perf_optimizer
You: find performance bottlenecks

/agent code_reviewer
You: review overall code quality

# Or use mentions
You: @security_auditor check auth.py
You: @perf_optimizer optimize this query
You: @code_reviewer review my changes
```

### Documentation Sprint

```bash
/agent docs_writer
You: document all functions in api.py
You: create README for this module
You: write usage examples for auth system
```

## 📂 Agent Files

Each agent has two files:

### 1. Config File: `.orc/agents/<name>.json`

```json
{
  "name": "security_auditor",
  "role": "Security Expert",
  "expertise": ["security", "vulnerabilities"],
  "personality": "strict",
  "system_prompt": "Focus on security...",
  "enabled_tools": "all",
  "temperature": 0.3,
  "max_tokens": 4096,
  "created": "2026-01-09T20:00:00"
}
```

### 2. Memory File: `orc_<name>.md`

```markdown
# ORC SubAgent: security_auditor

## Agent Profile
- Role: Security Expert
- Expertise: security, vulnerabilities
- Created: 2026-01-09

## Custom Training
Focus on finding security vulnerabilities...

## Agent Memory (Auto-Updated)
### Last Active
- Date: 2026-01-09T20:15:00
- Tasks Completed: 5

### Recent Work
- [2026-01-09 20:15] Used tool: search_code
  Details: @security_auditor check auth.py
- [2026-01-09 20:10] Agent activated
  Details: Switched to this agent
```

## 🔧 Commands Reference

| Command | Description | Example |
|---------|-------------|---------|
| `/create-agent` | Create new agent | `/create-agent` |
| `/list-agents` | List all agents | `/list-agents` |
| `/agent <name>` | Switch to agent | `/agent security_auditor` |
| `/agent main` | Back to main ORC | `/agent main` |
| `/delete-agent <name>` | Delete agent | `/delete-agent old_agent` |
| `@agent_name` | Mention agent | `@security_auditor check this` |

## 💡 Pro Tips

### 1. **Specialized Agents > General Agents**
Create agents with narrow focus for better results:
```
❌ "general_helper" - Too broad
✅ "auth_specialist" - Focused on authentication
```

### 2. **Use Strict Personality for Audits**
```
Security audits → Strict personality (critical analysis)
Documentation → Teacher personality (explanatory)
```

### 3. **Adjust Temperature by Task**
```
Code reviews → 0.3-0.4 (focused)
Architecture design → 0.6-0.7 (balanced)
Brainstorming → 0.8-1.0 (creative)
```

### 4. **Memory Persists**
Each agent remembers previous interactions:
```bash
# Yesterday
/agent security_auditor
You: check auth.py for issues

# Today - agent remembers!
/agent security_auditor
You: did you find anything in auth.py?
Agent: Yes, yesterday I found...
```

### 5. **Use @ Mentions for Quick Consultation**
```bash
# No need to switch
You: implementing OAuth2... @security_auditor any concerns?
You: @perf_optimizer is this query efficient?
```

### 6. **Create a Team for Large Projects**
```
security_auditor     → Security review
perf_optimizer       → Performance optimization
test_writer         → Generate tests
docs_writer         → Documentation
refactor_expert     → Code improvements
```

## 🎯 Use Cases

### Startup Team (Limited Budget)
```
1. fullstack_dev - General development
2. code_reviewer - Quality control
3. docs_writer - Documentation
```

### Enterprise Security Team
```
1. security_auditor - OWASP compliance
2. auth_specialist - Authentication/Authorization
3. crypto_expert - Encryption/Security protocols
4. compliance_checker - Regulatory compliance
```

### Performance-Critical App
```
1. perf_optimizer - Algorithm optimization
2. db_specialist - Database query optimization
3. cache_expert - Caching strategies
4. profiler - Performance profiling
```

## 🚨 Limitations

- Each agent uses API credits (be mindful with many agents)
- Agents don't communicate with each other (yet)
- Memory is file-based (no shared knowledge base yet)
- One active agent at a time per terminal

## 🔮 Future Features (Coming Soon)

- [ ] Agent-to-agent communication
- [ ] Shared knowledge base
- [ ] Agent collaboration workflows
- [ ] Pre-built agent templates
- [ ] Agent marketplace
- [ ] Web UI for agent management

## 📚 Related Docs

- [ORC CLI Quick Start](ORC_CLI_QUICK_START.md)
- [AI Tools Documentation](NEW_AI_TOOLS.md)
- [Smart Context Strategy](SMART_CONTEXT_STRATEGY.md)

---

**Happy agent building! Build your AI dev team and 10x your productivity! 🚀**
