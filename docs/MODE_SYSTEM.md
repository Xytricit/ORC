# ORC Mode System

The mode system allows ORC to intelligently switch between chat-only mode (fast, no tools) and work mode (full tool access), or let you control it manually.

## Overview

ORC has three operational modes:

1. **Auto Mode** (default) - AI automatically decides when to use tools
2. **Chat Mode** - Fast responses without codebase tools
3. **Work Mode** - Full access to all codebase analysis tools

## Usage

### View Current Mode
```
/mode
```

Shows your current mode and how it's being used.

### Switch Modes
```
/mode auto    - Let AI decide automatically
/mode chat    - Chat only (no tools)
/mode work    - Full tool access
```

## How Auto Mode Works

When in auto mode, ORC intelligently detects whether your question needs codebase tools:

### Uses Work Mode (with tools) for:
- Questions about specific code/files
- Analysis requests (complexity, dead code, etc.)
- Searching or finding things
- Keywords like: analyze, find, show me, check, scan
- File references: `file.py`, `function:`, `class:`

### Uses Chat Mode (no tools) for:
- General questions after context is established
- Follow-up questions about previous answers
- Conceptual or how-to questions
- Keywords like: what is, how do, explain, why
- Casual conversation: thanks, ok, got it

### Smart Prompts

When in auto mode, ORC will ask before switching:
```
Switch to chat mode (faster, no tools)? (yes/no, or set /mode):
```

You can:
- Say "yes" to switch for this session
- Say "no" to keep current mode
- Use `/mode chat` or `/mode work` to set it permanently

## Examples

### Example 1: Working on Code
```
You: analyze my codebase
ORC: [work mode - uses tools to analyze]

You: what did you find?
ORC: [work mode - still discussing analysis]

You: thanks, that helps
ORC: Switch to chat mode (faster, no tools)?
You: yes
ORC: [chat mode - faster responses without tools]

You: how should I refactor this?
ORC: [chat mode - gives advice based on previous context]
```

### Example 2: Manual Control
```
You: /mode chat
ORC: Mode changed: auto -> chat

You: explain design patterns
ORC: [chat mode - fast response]

You: find complex functions
ORC: [chat mode - can't use tools, suggests switching]

You: /mode work
ORC: Mode changed: chat -> work

You: find complex functions
ORC: [work mode - uses complexity analysis tool]
```

### Example 3: Auto Mode Intelligence
```
You: show me the most complex functions
ORC: [detects "show me" + "functions" = needs work mode]
     [uses get_complexity tool]

You: what's the average complexity?
ORC: [still work mode, discussing analysis results]

You: great! what is cyclomatic complexity anyway?
ORC: [detects conceptual question]
     Switch to chat mode (faster, no tools)?
```

## Benefits

### Auto Mode Benefits
- **Efficient**: Only uses tools when needed
- **Fast**: Switches to chat mode for quick questions
- **Cost-effective**: No unnecessary tool calls
- **Smart**: Learns from conversation context

### Chat Mode Benefits
- **Speed**: No tool overhead
- **Cheaper**: Fewer tokens, no tool processing
- **Good for**: Discussion, explanation, advice

### Work Mode Benefits
- **Powerful**: Full tool access
- **Accurate**: Direct codebase analysis
- **Complete**: All features available
- **Good for**: Deep analysis, searching, metrics

## Status Information

Use `/status` to see current mode along with other info:
```
AI Provider: groq
Model: llama-3.3-70b-versatile
Project: my-project
Messages: 10
Active Agent: Main ORC
Mode: auto (currently using work mode)
```

## Mode Detection Logic

The mode manager uses these indicators:

### Tool Indicators (→ work mode)
- analyze, find, search, show me, what's in
- list, get, check, scan, look for
- functions, classes, files, modules
- complexity, dead code, dependencies
- file:, function:, class:, .py, .js
- codebase, project, repository

### Chat Indicators (→ chat mode)
- what is, how do, explain, tell me about
- why, what does, help me understand
- thanks, thank you, ok, got it
- what do you think, should i

### Context Factors
- Messages since last tool use
- Recent tool usage pattern
- Conversation flow

## Tips

1. **Start with auto mode** - Let ORC optimize for you
2. **Use chat mode** for long discussions after analysis
3. **Use work mode** when doing deep code investigation
4. **Switch freely** - No penalty for changing modes
5. **Trust the prompts** - Auto mode suggestions are smart

## Advanced Usage

### For Maximum Speed
```
/mode chat
[Ask all your conceptual questions]
[Fast responses, no tool overhead]
```

### For Deep Analysis
```
/mode work
[Do all your codebase analysis]
[Use all tools without prompts]
```

### For Best of Both
```
/mode auto
[Let ORC decide based on your questions]
[Optimal balance of speed and power]
```

## Technical Details

The mode system:
- Tracks messages since last tool use
- Analyzes question content for keywords
- Considers conversation context
- Suggests mode changes proactively
- Never switches without asking (in auto mode)
- Respects manual overrides

## FAQ

**Q: What's the default mode?**  
A: Auto mode - ORC decides when to use tools.

**Q: Will I be charged more in work mode?**  
A: Only when tools are actually used. Chat mode never uses tools.

**Q: Can I force tool usage in chat mode?**  
A: No. Switch to work mode or auto mode first.

**Q: Does mode affect subagents?**  
A: Each agent respects the current mode setting.

**Q: Will auto mode always ask before switching?**  
A: Yes, except for the first message in a session.

**Q: Can I see mode in the prompt?**  
A: Not yet, but it's shown in `/status` and `/mode`.

---

The mode system makes ORC smarter and more efficient!
