# ORC Premium CLI Interface - Redesign Plan

Based on research from Claude CLI, Gemini CLI, and Qwen CLI

## Current Status
- ✅ Chevron (›) already added to banner
- ✅ Tool execution has nice formatting (┌─ └─ borders)
- ⏳ Need better message display formatting
- ⏳ Need syntax highlighting for code blocks
- ⏳ Need new slash commands
- ⏳ Need streaming response improvements
- ⏳ Need session save/load

---

## Key Changes to Implement

### 1. Enhanced Message Display (PRIORITY 1)

**Current:** Basic console.print for messages
**New:** Premium formatting with clear visual separators

```python
# User message display
┌─ You
│ What does login() do?
└─

# AI response display
┌─ ORC
│ The login() function authenticates user credentials...
│ 
│ ```python
│ def login(email, password):
│     ...
│ ```
└─ [tokens: 150 | time: 1.2s]
```

**Implementation:**
- Add `display_user_message()` function
- Add `display_ai_message()` function with streaming
- Add syntax highlighting using Rich's Syntax class
- Add metadata footer (tokens, time)

---

### 2. Syntax Highlighting (PRIORITY 1)

**Current:** Code blocks shown as plain text
**New:** Syntax-highlighted code blocks

```python
from rich.syntax import Syntax

def display_code_block(code, language="python"):
    syntax = Syntax(code, language, theme="monokai", line_numbers=True)
    console.print(syntax)
```

**Implementation:**
- Detect code blocks in markdown (```language)
- Apply syntax highlighting
- Support multiple languages (python, javascript, typescript, etc.)

---

### 3. New Slash Commands (PRIORITY 2)

Add these commands to match Claude/Gemini CLI:

```
/save [name]       - Save current conversation
/load [name]       - Load saved conversation
/export [format]   - Export to markdown/json
/copy              - Copy last code block to clipboard
/tokens            - Show token usage this session
/cost              - Show estimated cost
/context           - Show context window usage
/models            - List available models for current provider
/clear             - Clear screen (keep conversation)
/reset             - Reset conversation (new session)
/compact           - Toggle compact mode
/stream            - Toggle streaming mode
```

**Implementation:**
- Add handler methods in `ORCChatSession` class
- Add to slash command list
- Implement conversation persistence (JSON files in .orc/sessions/)
- Implement token tracking
- Implement clipboard functionality

---

### 4. Streaming Response Improvements (PRIORITY 2)

**Current:** Loading spinner during entire response
**New:** Real-time streaming with typewriter effect

```python
def stream_response(response_generator):
    """Display AI response as it streams in"""
    console.print("┌─ ORC")
    console.print("│ ", end="")
    
    for chunk in response_generator:
        console.print(chunk, end="", flush=True)
    
    console.print("\n└─")
```

**Implementation:**
- Modify AI client to support streaming
- Display tokens as they arrive
- Show cursor indicator during streaming
- Calculate and display speed (tokens/sec)

---

### 5. Status Bar (PRIORITY 3)

**Add permanent status bar at top:**

```
[ORC v2.0] Model: groq/llama-3.1-70b | Context: 1.2k/32k | Session: 12 msgs | Cost: $0.003
──────────────────────────────────────────────────────────────────────────────────────
```

**Implementation:**
- Add `StatusBar` class
- Update after each message
- Show: model, context usage, message count, estimated cost
- Use Rich's Live for dynamic updates

---

### 6. Session Management (PRIORITY 2)

**Save/Load Conversations:**

```
.orc/sessions/
├── 2026-01-12_auth-refactor.json
├── 2026-01-12_bug-investigation.json
└── latest.json (auto-saved)
```

**Format:**
```json
{
  "session_id": "uuid",
  "created_at": "2026-01-12T18:00:00",
  "title": "Auth Refactor Discussion",
  "provider": "groq",
  "model": "llama-3.1-70b",
  "messages": [
    {"role": "user", "content": "...", "timestamp": "..."},
    {"role": "assistant", "content": "...", "tokens": 150}
  ],
  "total_tokens": 1250,
  "total_cost": 0.003
}
```

**Implementation:**
- Add `SessionManager` class
- Auto-save after each exchange
- /save with optional name
- /load with autocomplete from saved sessions

---

### 7. Token & Cost Tracking (PRIORITY 3)

**Track usage per session:**

```python
class TokenTracker:
    def __init__(self):
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0
    
    def add_exchange(self, input_tokens, output_tokens, model):
        # Calculate cost based on model pricing
        pass
    
    def get_summary(self):
        return {
            "input": self.total_input_tokens,
            "output": self.total_output_tokens,
            "total": self.total_input_tokens + self.total_output_tokens,
            "cost": self.total_cost
        }
```

**Pricing Database:**
```python
MODEL_PRICING = {
    "groq/llama-3.1-70b": {"input": 0.0, "output": 0.0},  # Free
    "openai/gpt-4": {"input": 0.03, "output": 0.06},  # per 1k tokens
    "anthropic/claude-3": {"input": 0.015, "output": 0.075},
}
```

---

### 8. Copy Code Functionality (PRIORITY 3)

**Implementation:**
```python
import pyperclip  # Add to requirements

def copy_last_code_block():
    """Copy last code block to clipboard"""
    # Find last code block in conversation
    for msg in reversed(conversation_history):
        if msg["role"] == "assistant":
            code_blocks = extract_code_blocks(msg["content"])
            if code_blocks:
                pyperclip.copy(code_blocks[0])
                console.print("[green]✓ Code copied to clipboard[/green]")
                return
    
    console.print("[yellow]No code blocks found[/yellow]")
```

---

### 9. Enhanced Help Command (PRIORITY 3)

**Make /help beautiful:**

```
┌─ ORC Commands
│
│ Conversation:
│   /save [name]     Save this conversation
│   /load [name]     Load a saved conversation
│   /export [fmt]    Export conversation (md/json)
│   /reset           Start new conversation
│   /clear           Clear screen
│   /history         Show message history
│
│ Configuration:
│   /provider <name> Switch AI provider
│   /model <name>    Switch model
│   /summarizer      Configure code summarizer
│   /compact         Toggle compact mode
│
│ Code Tools:
│   /copy            Copy last code block
│   /tokens          Show token usage
│   /cost            Show estimated cost
│   /context         Show context window
│
│ Help:
│   /help            Show this help
│   /models          List available models
│   /exit            Exit ORC
│
└─ Tip: Press Escape twice to navigate message history
```

---

### 10. Improved Error Handling (PRIORITY 3)

**Current:** Basic error messages
**New:** Beautiful error panels

```python
from rich.panel import Panel

def show_error_panel(title, message, suggestion=None):
    content = f"[red]{message}[/red]"
    if suggestion:
        content += f"\n\n[dim]Suggestion: {suggestion}[/dim]"
    
    panel = Panel(
        content,
        title=f"[red]✗ {title}[/red]",
        border_style="red",
        padding=(1, 2)
    )
    console.print(panel)
```

---

## Implementation Order

### Phase 1: Visual Improvements (Session 1)
1. ✅ Add chevron to banner (DONE)
2. Enhanced message display with borders
3. Syntax highlighting for code blocks
4. Improved error panels

### Phase 2: Core Features (Session 2)
5. Session save/load functionality
6. New slash commands (/save, /load, /export, /copy)
7. Token tracking system
8. Cost estimation

### Phase 3: Advanced Features (Session 3)
9. Streaming improvements
10. Status bar
11. Enhanced help
12. Context window management

---

## Files to Modify

1. **`orc/cli_loop.py`** (MAIN FILE)
   - Add display functions
   - Add slash command handlers
   - Add session management
   - Add token tracking

2. **`orc/ui_components.py`** (NEW HELPER)
   - Message display functions
   - Code block formatting
   - Error panels
   - Status bar component

3. **`orc/session_manager.py`** (NEW)
   - Save/load conversations
   - Session metadata
   - Auto-save functionality

4. **`orc/token_tracker.py`** (NEW)
   - Track token usage
   - Calculate costs
   - Generate usage reports

5. **`orc/banner.py`** (MINOR)
   - ✅ Already has chevron

---

## Testing Plan

1. Visual test - Verify formatting looks good
2. Functional test - Save/load conversations
3. Token tracking test - Verify counts are accurate
4. Copy test - Verify clipboard functionality
5. Streaming test - Verify smooth display
6. Error test - Verify error handling

---

## Dependencies to Add

```txt
# requirements.txt additions
pyperclip>=1.8.2          # Clipboard functionality
```

---

## Next Session Goals

1. Implement Phase 1 (Visual Improvements)
2. Test on real conversations
3. Get user feedback
4. Iterate and refine

---

## Reference Examples

### Claude Code Style:
- Minimalist, clean
- Clear borders
- Monochromatic + accents
- Streaming responses

### Gemini CLI Style:
- Rich formatting
- Export functionality
- Multi-turn memory

### Qwen CLI Style:
- Fast streaming (<200ms)
- Performance metrics
- Clean separators

### ORC Style (Our Goal):
- Best of all three
- Add code intelligence
- Keep quirky personality
- Premium + powerful
