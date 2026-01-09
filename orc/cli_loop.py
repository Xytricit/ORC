"""
ORC AI CLI Loop - Professional conversational interface
Uses real codebase analysis tools - no hallucinations
"""

import os
import sys
import json
import time
import random
import threading
from pathlib import Path
from typing import Optional, List, Dict, Any

# Load .env file before anything else
def _load_env():
    try:
        from dotenv import load_dotenv
        possible_paths = [
            Path(__file__).parent / '.env',
            Path.cwd() / '.env',
            Path.cwd() / 'orc' / '.env',
        ]
        for env_path in possible_paths:
            if env_path.exists():
                load_dotenv(env_path, override=True)
                return
    except ImportError:
        pass

_load_env()

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.box import ROUNDED, HEAVY, DOUBLE
from rich.table import Table
from rich.markdown import Markdown
import threading
import signal

# Try to import prompt_toolkit for better input handling
try:
    from prompt_toolkit import prompt
    from prompt_toolkit.completion import WordCompleter, Completer, Completion
    from prompt_toolkit.styles import Style
    from prompt_toolkit.formatted_text import HTML
    PROMPT_TOOLKIT_AVAILABLE = True
except ImportError:
    PROMPT_TOOLKIT_AVAILABLE = False

from orc.banner import get_orc_banner, print_startup_info
from orc.ai_client import get_ai_client, AIResponse, reset_ai_client
from orc.ai_tools import TOOL_DEFINITIONS, ORCTools
from orc.ai_guidelines import get_system_prompt

# Reset client to pick up newly loaded env vars
reset_ai_client()

console = Console()

# Slash commands for autocomplete
SLASH_COMMANDS = [
    ("/help", "Show all commands"),
    ("/status", "Show AI provider status"),
    ("/providers", "List available AI providers"),
    ("/provider", "Switch AI provider"),
    ("/models", "Show current model"),
    ("/model", "Switch model"),
    ("/add-provider", "Add a custom AI provider"),
    ("/remove-provider", "Remove a custom AI provider"),
    ("/list-providers", "List all available providers (including custom)"),
    ("/clear", "Clear conversation"),
    ("/history", "Show chat history"),
    ("/reset", "Reset AI client"),
    ("/compact", "Toggle compact mode"),
    ("/preferences", "Manage ORC.md settings"),
    ("/exit", "Exit ORC"),
]

# Custom completer for slash commands
if PROMPT_TOOLKIT_AVAILABLE:
    class SlashCommandCompleter(Completer):
        def get_completions(self, document, complete_event):
            text = document.text_before_cursor
            if text.startswith("/"):
                for cmd, desc in SLASH_COMMANDS:
                    if cmd.startswith(text):
                        yield Completion(
                            cmd,
                            start_position=-len(text),
                            display=cmd,
                            display_meta=desc,
                            style="fg:ansicyan",
                            selected_style="fg:ansiwhite bg:ansicyan",
                        )
    
    # Style for the prompt
    prompt_style = Style.from_dict({
        'prompt': 'ansigreen bold',
        'completion-menu.completion': 'bg:#333333 #ffffff',
        'completion-menu.completion.current': 'bg:#00aa00 #ffffff',
        'completion-menu.meta.completion': 'bg:#333333 #888888',
        'completion-menu.meta.completion.current': 'bg:#00aa00 #ffffff',
    })

# Fun ORC-themed loading messages
ORC_LOADING_MESSAGES = [
    "Sharpening axes",
    "Stomping around impatiently",
    "Crushing bugs (literally and figuratively)",
    "Sniffing out errors",
    "Roaring at slow compilers",
    "Hoarding code snippets",
    "Flexing massive brainmuscles",
    "Intimidating the syntax into behaving",
    "Wrestling with dependencies",
    "Smashing logs together to make sense of them",
    "Bruteforcing enthusiasm",
    "Optimizing rage levels",
    "Refactoring battle plans",
    "Parsing scrolls of ancient code",
    "Summoning the Great Stack Trace",
    "Headbutting the database",
    "Growling at null pointers",
    "Bench-pressing server loads",
    "Interrogating variables",
    "Raiding the code dungeon",
]

# Global flag for stopping AI generation
_stop_generation = False

def set_stop_generation(value: bool):
    global _stop_generation
    _stop_generation = value

def should_stop_generation() -> bool:
    return _stop_generation


class RotatingLoader:
    """Rotating loading messages that change every few seconds"""
    
    def __init__(self, interval: float = 5.0):
        self.interval = interval
        self.current_message = random.choice(ORC_LOADING_MESSAGES)
        self.running = False
        self.thread = None
    
    def _rotate(self):
        while self.running:
            time.sleep(self.interval)
            if self.running:
                self.current_message = random.choice(ORC_LOADING_MESSAGES)
    
    def start(self):
        self.running = True
        self.current_message = random.choice(ORC_LOADING_MESSAGES)
        self.thread = threading.Thread(target=self._rotate, daemon=True)
        self.thread.start()
    
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=0.1)
    
    def get_message(self) -> str:
        return self.current_message


def show_error_panel(title: str, message: str, hint: str = None):
    """Show a nice error panel"""
    content = f"[white]{message}[/white]"
    if hint:
        content += f"\n\n[dim]{hint}[/dim]"
    
    panel = Panel(
        content,
        title=f"[red]{title}[/red]",
        border_style="red",
        box=ROUNDED,
        padding=(1, 2),
    )
    console.print(panel)


def show_rate_limit_panel(provider: str, wait_time: str = None):
    """Show a nice rate limit error panel"""
    message = f"The {provider} API has reached its rate limit."
    
    if wait_time:
        hint = f"Please wait {wait_time} or switch providers with /providers"
    else:
        hint = "Try switching providers with /providers or wait a moment"
    
    panel = Panel(
        f"[yellow]{message}[/yellow]\n\n[dim]{hint}[/dim]",
        title="[yellow]Rate Limit Reached[/yellow]",
        border_style="yellow",
        box=ROUNDED,
        padding=(1, 2),
    )
    console.print(panel)


def show_info_panel(title: str, content: str, style: str = "cyan"):
    """Show a nice info panel"""
    panel = Panel(
        content,
        title=f"[{style}]{title}[/{style}]",
        border_style=style,
        box=ROUNDED,
        padding=(1, 2),
    )
    console.print(panel)


def show_tool_log(tool_name: str, status: str = "running"):
    """Show attractive tool execution log"""
    if status == "running":
        console.print(f"  [dim]│[/dim]  [cyan]>[/cyan] [dim]{tool_name}[/dim]")
    elif status == "done":
        console.print(f"  [dim]│[/dim]  [green]✓[/green] [dim]{tool_name}[/dim]")
    elif status == "error":
        console.print(f"  [dim]│[/dim]  [red]✗[/red] [dim]{tool_name}[/dim]")


def show_ai_todo(tasks: List[Dict]):
    """Show AI's current task list"""
    if not tasks:
        return
    
    console.print()
    console.print("  [dim]┌─ Tasks[/dim]")
    for task in tasks:
        status = task.get("status", "pending")
        name = task.get("name", "Task")
        if status == "done":
            console.print(f"  [dim]│[/dim]  [green]✓[/green] [strike dim]{name}[/strike dim]")
        elif status == "running":
            console.print(f"  [dim]│[/dim]  [cyan]>[/cyan] [white]{name}[/white]")
        else:
            console.print(f"  [dim]│[/dim]  [dim]○[/dim] [dim]{name}[/dim]")
    console.print("  [dim]└─[/dim]")


def show_memory_bar(session: 'ORCChatSession'):
    """Show memory usage bar below AI responses"""
    # Count conversation pairs (user + assistant)
    msg_count = len([m for m in session.conversation_history if m["role"] == "user"])
    max_messages = 10
    
    # Calculate percentage and bar
    percentage = min(100, int((msg_count / max_messages) * 100))
    filled_blocks = int(percentage / 10)
    bar = "█" * filled_blocks + "░" * (10 - filled_blocks)
    
    # Determine color based on usage
    if msg_count >= 10:
        color = "yellow"
        hint = "  [yellow]💡 Consider /clear for optimal performance[/yellow]"
    elif msg_count >= 8:
        color = "yellow"
        hint = "  [dim]Approaching memory limit[/dim]"
    else:
        color = "dim"
        hint = ""
    
    # Show tools used (last 3)
    if session.tools_used_this_session:
        recent_tools = session.tools_used_this_session[-3:]
        tools_display = ", ".join(recent_tools)
        if len(session.tools_used_this_session) > 3:
            tools_display += f" (+{len(session.tools_used_this_session) - 3} more)"
    else:
        tools_display = "None yet"
    
    # Show memory info
    memory_age = "Unknown"
    if session.permanent_memory and session.permanent_memory.get("last_analysis_date"):
        from datetime import datetime
        age_delta = datetime.now() - session.permanent_memory["last_analysis_date"]
        hours = int(age_delta.total_seconds() / 3600)
        if hours < 1:
            memory_age = "Fresh (< 1h)"
        elif hours < 24:
            memory_age = f"{hours}h ago"
        else:
            days = int(hours / 24)
            memory_age = f"{days}d ago"
    
    # Rotating tips instead of Cache display
    tips = [
        "Type /models to change AI models",
        "Use /help to see all commands",
        "Try /providers to switch AI provider",
        "Type /clear to reset conversation",
        "/status shows AI provider info",
        "/compact toggles compact mode",
        "/history shows chat history",
    ]
    
    # Calculate which tip to show based on time (rotate every 50 seconds)
    import time as time_module
    tip_index = int(time_module.time() / 50) % len(tips)
    current_tip = tips[tip_index]
    
    console.print()
    console.print(f"  [{color}]Memory: [{bar}] {msg_count}/10  |  Tools: {tools_display}  |  {current_tip}[/{color}]")
    if hint:
        console.print(hint)


def format_response(content: str) -> str:
    """Format AI response for nice display"""
    # Add some visual hierarchy
    lines = content.split('\n')
    formatted_lines = []
    
    for line in lines:
        # Style headers
        if line.startswith('## '):
            formatted_lines.append(f"\n[bold cyan]{line[3:]}[/bold cyan]")
        elif line.startswith('### '):
            formatted_lines.append(f"\n[bold]{line[4:]}[/bold]")
        elif line.startswith('**') and line.endswith('**'):
            formatted_lines.append(f"[bold]{line[2:-2]}[/bold]")
        elif line.startswith('- '):
            formatted_lines.append(f"  [dim]•[/dim] {line[2:]}")
        elif line.startswith('* '):
            formatted_lines.append(f"  [dim]•[/dim] {line[2:]}")
        else:
            formatted_lines.append(line)
    
    return '\n'.join(formatted_lines)


def count_codebase_stats() -> tuple:
    """Count lines of code and detect languages in current directory"""
    loc = 0
    languages = set()
    
    extensions_map = {
        '.py': 'Python',
        '.js': 'JavaScript',
        '.jsx': 'JavaScript',
        '.ts': 'TypeScript',
        '.tsx': 'TypeScript',
        '.java': 'Java',
        '.cpp': 'C++',
        '.cxx': 'C++',
        '.cc': 'C++',
        '.c': 'C',
        '.h': 'C/C++',
        '.hpp': 'C++',
        '.html': 'HTML',
        '.htm': 'HTML',
        '.css': 'CSS',
        '.go': 'Go',
        '.rs': 'Rust',
        '.php': 'PHP',
        '.rb': 'Ruby',
        '.swift': 'Swift',
        '.kt': 'Kotlin',
    }
    
    code_extensions = set(extensions_map.keys())
    
    for root, dirs, files in os.walk("."):
        # Skip hidden directories and venv
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['venv', 'node_modules', '__pycache__']]
        
        for file in files:
            if file.startswith('.'):
                continue
            
            ext = Path(file).suffix.lower()
            
            if ext in extensions_map:
                languages.add(extensions_map[ext])
            
            if ext in code_extensions:
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        loc += len(f.readlines())
                except:
                    pass
    
    return loc, list(languages) if languages else ['Python']


def show_progress_bar(task_name: str, console: Console) -> None:
    """Show a progress bar while processing"""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=30),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console,
        transient=True
    ) as progress:
        task = progress.add_task(f"[cyan]{task_name}...", total=100)
        for i in range(100):
            time.sleep(0.02)
            progress.update(task, advance=1)


class ORCMemory:
    """
    Intelligent memory management system for ORC.
    Stores permanent context in ORC.md that AI can reference.
    """
    
    ORC_MD_PATH = Path("ORC.md")
    
    @classmethod
    def read_permanent_memory(cls) -> Optional[Dict[str, Any]]:
        """Read AI's permanent memory from ORC.md"""
        if not cls.ORC_MD_PATH.exists():
            return None
        
        try:
            content = cls.ORC_MD_PATH.read_text(encoding="utf-8")
            memory = {
                "last_analysis_date": None,
                "codebase_structure": None,
                "total_files": None,
                "total_loc": None,
                "main_folders": [],
                "known_issues": [],
                "cached_data": {}
            }
            
            # Parse "## AI Memory" section
            in_memory_section = False
            current_subsection = None
            
            for line in content.split("\n"):
                if "## AI Memory" in line or "## Permanent Memory" in line:
                    in_memory_section = True
                    continue
                
                if in_memory_section:
                    if line.startswith("## ") and "AI Memory" not in line and "Permanent Memory" not in line:
                        in_memory_section = False
                        break
                    
                    # Parse subsections
                    if line.startswith("### Last Analysis"):
                        current_subsection = "last_analysis"
                    elif line.startswith("### Codebase Structure"):
                        current_subsection = "structure"
                    elif line.startswith("### Known Issues"):
                        current_subsection = "issues"
                    elif line.strip().startswith("- Date:") and current_subsection == "last_analysis":
                        date_str = line.split("Date:", 1)[1].strip()
                        if date_str != "Never":
                            from datetime import datetime
                            try:
                                memory["last_analysis_date"] = datetime.fromisoformat(date_str)
                            except:
                                pass
                    elif line.strip().startswith("- Total Files:"):
                        try:
                            memory["total_files"] = int(line.split(":", 1)[1].strip())
                        except:
                            pass
                    elif line.strip().startswith("- Total LOC:"):
                        try:
                            memory["total_loc"] = int(line.split(":", 1)[1].strip().replace(",", ""))
                        except:
                            pass
                    elif line.strip().startswith("- Main Folders:"):
                        folders_str = line.split(":", 1)[1].strip()
                        if folders_str:
                            memory["main_folders"] = [f.strip() for f in folders_str.split(",")]
            
            return memory
        except Exception:
            return None
    
    @classmethod
    def write_permanent_memory(cls, analysis_data: Dict[str, Any]):
        """Write AI's findings to ORC.md permanent memory"""
        from datetime import datetime
        
        if not cls.ORC_MD_PATH.exists():
            return  # Don't create if doesn't exist
        
        try:
            content = cls.ORC_MD_PATH.read_text(encoding="utf-8")
            
            # Build the AI Memory section
            memory_section = f"""## AI Memory (Auto-Updated)

*This section is automatically maintained by ORC AI to remember your codebase.*

### Last Analysis
- Date: {datetime.now().isoformat()}
- Total Files: {analysis_data.get('total_files', 'Unknown')}
- Total LOC: {analysis_data.get('total_loc', 'Unknown')}
- Main Folders: {', '.join(analysis_data.get('main_folders', []))}

### Codebase Structure
{analysis_data.get('structure_summary', 'No structure data cached yet.')}

### Known Issues
{chr(10).join(f"- {issue}" for issue in analysis_data.get('known_issues', []))}

### Tools Recently Used
{chr(10).join(f"- {tool}" for tool in analysis_data.get('tools_used', []))}

"""
            
            # Find and replace AI Memory section, or add it
            if "## AI Memory" in content or "## Permanent Memory" in content:
                # Replace existing section
                lines = content.split("\n")
                new_lines = []
                in_ai_memory = False
                skip_until_next_section = False
                
                for line in lines:
                    if "## AI Memory" in line or "## Permanent Memory" in line:
                        in_ai_memory = True
                        skip_until_next_section = True
                        new_lines.append(memory_section.strip())
                        continue
                    
                    if skip_until_next_section:
                        if line.startswith("## ") and "AI Memory" not in line and "Permanent Memory" not in line:
                            skip_until_next_section = False
                            new_lines.append(line)
                        continue
                    else:
                        new_lines.append(line)
                
                content = "\n".join(new_lines)
            else:
                # Add AI Memory section after Preferences
                if "## Preferences" in content:
                    parts = content.split("## Preferences", 1)
                    # Find next section after Preferences
                    if "## " in parts[1]:
                        pref_part, rest = parts[1].split("## ", 1)
                        content = parts[0] + "## Preferences" + pref_part + "\n" + memory_section + "\n## " + rest
                    else:
                        content = parts[0] + "## Preferences" + parts[1] + "\n" + memory_section
                else:
                    content += "\n" + memory_section
            
            cls.ORC_MD_PATH.write_text(content, encoding="utf-8")
        except Exception as e:
            # Silently fail - don't crash if can't write
            pass
    
    @classmethod
    def should_refresh_analysis(cls, cached_memory: Optional[Dict[str, Any]]) -> bool:
        """Determine if cached analysis should be refreshed"""
        if not cached_memory or not cached_memory.get("last_analysis_date"):
            return True
        
        from datetime import datetime, timedelta
        last_analysis = cached_memory["last_analysis_date"]
        age = datetime.now() - last_analysis
        
        # Refresh if older than 24 hours
        return age > timedelta(hours=24)


class ORCPreferences:
    """Handles ORC.md preferences file"""
    
    ORC_MD_PATH = Path("ORC.md")
    
    @classmethod
    def exists(cls) -> bool:
        return cls.ORC_MD_PATH.exists()
    
    @classmethod
    def load(cls) -> Dict[str, Any]:
        """Load preferences from ORC.md"""
        if not cls.exists():
            return {}
        
        try:
            content = cls.ORC_MD_PATH.read_text(encoding="utf-8")
            prefs = {}
            
            # Parse simple key: value format from markdown
            in_prefs_section = False
            for line in content.split("\n"):
                if "## Preferences" in line:
                    in_prefs_section = True
                    continue
                if in_prefs_section and line.startswith("## "):
                    in_prefs_section = False
                if in_prefs_section and ": " in line:
                    line = line.lstrip("- ")
                    key, value = line.split(": ", 1)
                    prefs[key.strip().lower()] = value.strip()
            
            return prefs
        except Exception:
            return {}
    
    @classmethod
    def save(cls, prefs: Dict[str, Any], project_info: Dict[str, Any] = None):
        """Save preferences to ORC.md"""
        content = f"""# ORC Project Configuration

This file stores your preferences and project information for ORC.
ORC uses this to provide better, more personalized assistance.

## Project Info

- Name: {project_info.get('name', 'Unknown') if project_info else 'Unknown'}
- Languages: {', '.join(project_info.get('languages', [])) if project_info else 'Unknown'}
- Created: {project_info.get('created', 'Unknown') if project_info else 'Unknown'}

## Preferences

- response_style: {prefs.get('response_style', 'detailed')}
- ai_provider: {prefs.get('ai_provider', 'auto')}
- ai_model: {prefs.get('ai_model', 'default')}
- compact_mode: {prefs.get('compact_mode', 'false')}

## AI Memory (Auto-Updated)

*This section is automatically maintained by ORC AI to remember your codebase.*

### Last Analysis
- Date: Never
- Total Files: Unknown
- Total LOC: Unknown
- Main Folders: Not analyzed yet

### Codebase Structure
No structure data cached yet.

### Known Issues
No issues found yet.

### Tools Recently Used
No tools used yet.

## Project Notes

Add any notes about your project here that might help ORC understand it better:

- 

## Custom Instructions

Add any custom instructions for ORC here:

- 

---
*This file is auto-generated by ORC. Feel free to edit it!*
"""
        cls.ORC_MD_PATH.write_text(content, encoding="utf-8")
    
    @classmethod
    def first_run_prompt(cls) -> bool:
        """Ask user if they want to create ORC.md. Returns True if yes."""
        console.print("\n[cyan]Welcome to ORC![/cyan]")
        console.print("[dim]Would you like to create an ORC.md file to store your preferences?[/dim]")
        console.print("[dim]This helps ORC remember your settings and provide better assistance.[/dim]\n")
        
        while True:
            response = console.input("[green]Create ORC.md? (yes/no):[/green] ").strip().lower()
            if response in ["yes", "y", "yeah", "yep", "sure", "ok"]:
                return True
            elif response in ["no", "n", "nope", "nah"]:
                return False
            else:
                console.print("[dim]Please type 'yes' or 'no'[/dim]")


class ORCChatSession:
    """Main chat session handler"""
    
    def __init__(self):
        # Load web configs from CLI auth if authenticated
        web_configs = self._load_web_configs()
        self.ai_client = get_ai_client(web_configs=web_configs)
        self.tools = ORCTools()
        self.conversation_history: List[Dict[str, str]] = []
        self.project_name = os.path.basename(os.getcwd()) or "project"
        self.preferences = {}
        
        # Session memory tracking
        self.tools_used_this_session: List[str] = []
        self.permanent_memory: Optional[Dict[str, Any]] = None
        
        # Auto-create web project if authenticated
        self._auto_create_web_project()
        
        # Load preferences if ORC.md exists
        if ORCPreferences.exists():
            self.preferences = ORCPreferences.load()
            # Load permanent memory
            self.permanent_memory = ORCMemory.read_permanent_memory()
    
    def _load_web_configs(self) -> Optional[Dict[str, Dict[str, str]]]:
        """Load API configs from web interface if authenticated"""
        try:
            from orc.cli_auth import is_authenticated, get_api_config
            
            if not is_authenticated():
                return None
            
            # Fetch all configs from web
            import httpx
            from orc.cli_auth import get_token, get_web_url
            
            token = get_token()
            web_url = get_web_url()
            
            response = httpx.get(
                f'{web_url}/api/configs',
                headers={'X-CLI-Token': token},
                timeout=5.0
            )
            
            if response.status_code == 200:
                data = response.json()
                configs = data.get('configs', [])
                
                # Transform to the format MultiProviderClient expects
                web_configs = {}
                for config in configs:
                    provider = config.get('provider', '').lower()
                    if provider:
                        web_configs[provider] = {
                            'api_key': config.get('api_key'),
                            'model_name': config.get('model_name')
                        }
                
                return web_configs if web_configs else None
        except Exception:
            # If web config loading fails, fall back to env vars
            pass
        
        return None
    
    def _auto_create_web_project(self):
        """Auto-create a project in web interface if authenticated and in a directory"""
        try:
            from orc.cli_auth import is_authenticated, get_token, get_web_url
            
            if not is_authenticated():
                return
            
            import httpx
            
            token = get_token()
            web_url = get_web_url()
            
            # Get current directory info
            current_dir = os.getcwd()
            project_name = os.path.basename(current_dir)
            
            # Check if .orc/index.db exists
            db_path = os.path.join(current_dir, '.orc', 'index.db')
            has_index = os.path.exists(db_path)
            
            # Try to create project (will fail silently if already exists)
            response = httpx.post(
                f'{web_url}/api/projects/auto-create',
                headers={'X-CLI-Token': token},
                json={
                    'name': project_name,
                    'path': current_dir,
                    'db_path': db_path if has_index else None,
                },
                timeout=5.0
            )
            
            # Don't show errors - auto-creation is optional
            if response.status_code == 201:
                # Successfully created
                pass
            
        except Exception:
            # Silently fail - auto-creation is optional
            pass
        
    def format_tool_result(self, tool_name: str, result: Dict) -> str:
        """Format tool result for display and AI consumption"""
        if "error" in result:
            return f"Error: {result['error']}"
        return json.dumps(result, indent=2, default=str)
    
    def execute_tool_calls(self, tool_calls: List[Dict]) -> List[Dict]:
        """Execute tool calls and return results with nice logging"""
        results = []
        
        for tool_call in tool_calls:
            tool_name = tool_call["name"]
            arguments = tool_call.get("arguments", {})
            
            # Show tool being executed
            show_tool_log(tool_name, "running")
            
            # Execute the tool with error handling
            try:
                result = self.tools.execute_tool(tool_name, arguments)
                show_tool_log(tool_name, "done")
            except Exception as e:
                result = {"error": f"Tool failed: {str(e)}"}
                show_tool_log(tool_name, "error")
            
            results.append({
                "tool_call_id": tool_call.get("id", ""),
                "name": tool_name,
                "result": result
            })
        
        return results
    
    def chat(self, user_message: str) -> str:
        """Process a user message and return AI response"""
        
        # Reset stop flag
        set_stop_generation(False)
        
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # Build memory context for AI
        memory_context = None
        if self.permanent_memory:
            memory_lines = []
            if self.permanent_memory.get("last_analysis_date"):
                memory_lines.append(f"Last Analysis: {self.permanent_memory['last_analysis_date'].strftime('%Y-%m-%d %H:%M')}")
            if self.permanent_memory.get("total_files"):
                memory_lines.append(f"Total Files: {self.permanent_memory['total_files']}")
            if self.permanent_memory.get("total_loc"):
                memory_lines.append(f"Total LOC: {self.permanent_memory['total_loc']:,}")
            if self.permanent_memory.get("main_folders"):
                memory_lines.append(f"Main Folders: {', '.join(self.permanent_memory['main_folders'])}")
            
            if memory_lines:
                memory_context = "\n".join(memory_lines)
        
        # Build messages for AI with smart context-aware system prompt
        messages = [
            {"role": "system", "content": get_system_prompt(
                memory_context=memory_context,
                tools_used_this_session=self.tools_used_this_session
            )}
        ]
        for msg in self.conversation_history:
            if msg["role"] in ["user", "assistant"] and "tool_calls" not in msg:
                messages.append({"role": msg["role"], "content": msg["content"]})
        
        # Show thinking indicator with rotating messages
        console.print()  # Spacing
        console.print("  [dim]┌─ Thinking[/dim]")
        
        # Use Rich Live display for animated loading
        from rich.live import Live
        from rich.text import Text
        
        loader = RotatingLoader(interval=2.0)
        loader.start()
        
        try:
            with Live(console=console, refresh_per_second=2, transient=False) as live:
                def update_display():
                    import threading
                    while loader.running:
                        msg_text = Text()
                        msg_text.append("  ", style="dim")
                        msg_text.append("│", style="dim")
                        msg_text.append("  ")
                        msg_text.append("⠋", style="cyan")
                        msg_text.append(" ", style="dim")
                        msg_text.append(f"{loader.get_message()}...", style="dim")
                        live.update(msg_text)
                        time.sleep(0.5)
                
                display_thread = threading.Thread(target=update_display, daemon=True)
                display_thread.start()
                
                # Get initial AI response
                response = self.ai_client.chat(
                    messages=messages,
                    tools=TOOL_DEFINITIONS,
                    temperature=0.7,
                    max_tokens=4096
                )
        finally:
            loader.stop()
        
        # Check for errors (rate limit, etc)
        if response.finish_reason == "error":
            self._handle_error_response(response.content)
            return ""
        
        console.print("  [dim]└─[/dim] [green]✓[/green] [dim]Ready[/dim]")
        
        # Handle tool calls in a loop
        max_iterations = 5  # Increased to allow more tool calls before requiring response
        max_tools_per_iteration = 1
        iteration = 0
        tool_messages = []
        tools_called = set()  # Track which tools have been called to avoid duplicates
        all_tool_results = []  # Track all results for memory update
        
        while response.tool_calls and iteration < max_iterations:
            # Check if user wants to stop
            if should_stop_generation():
                console.print("\n  [yellow]! Generation stopped[/yellow]")
                break
            
            iteration += 1
            
            # Limit to first tool only
            tools_to_run = response.tool_calls[:max_tools_per_iteration]
            
            # Track tool usage
            for tc in tools_to_run:
                tool_key = f"{tc['name']}"
                tools_called.add(tool_key)
                # Add to session tracking
                if tc['name'] not in self.tools_used_this_session:
                    self.tools_used_this_session.append(tc['name'])
            
            # Execute tool calls with nice logging
            console.print()
            console.print("  [dim]┌─ Running Tools[/dim]")
            
            try:
                tool_results = self.execute_tool_calls(tools_to_run)
                all_tool_results.extend(tool_results)  # Save for memory update
            except Exception as e:
                show_error_panel("Tool Error", str(e))
                break
            
            console.print("  [dim]└─[/dim] [green]✓[/green] [dim]Complete[/dim]")
            
            # Build tool call message for API
            tool_calls_for_api = [
                {
                    "id": tc["id"],
                    "type": "function",
                    "function": {
                        "name": tc["name"],
                        "arguments": json.dumps(tc["arguments"])
                    }
                }
                for tc in tools_to_run
            ]
            
            # Add assistant's tool call message
            tool_messages.append({
                "role": "assistant",
                "content": response.content or "",
                "tool_calls": tool_calls_for_api
            })
            
            # Add tool results
            for result in tool_results:
                tool_messages.append({
                    "role": "tool",
                    "tool_call_id": result["tool_call_id"],
                    "content": json.dumps(result["result"], default=str)
                })
            
            # Rebuild messages with tool context and updated system prompt
            messages = [
                {"role": "system", "content": get_system_prompt(
                    memory_context=memory_context,
                    tools_used_this_session=self.tools_used_this_session
                )}
            ]
            for msg in self.conversation_history:
                if msg["role"] in ["user", "assistant"] and "tool_calls" not in msg:
                    messages.append({"role": msg["role"], "content": msg["content"]})
            messages.extend(tool_messages)
            
            # Get next response
            console.print()
            console.print("  [dim]┌─ Processing[/dim]")
            
            loader = RotatingLoader(interval=2.0)
            loader.start()
            
            try:
                with Live(console=console, refresh_per_second=2, transient=False) as live:
                    def update_display():
                        while loader.running:
                            msg_text = Text()
                            msg_text.append("  ", style="dim")
                            msg_text.append("│", style="dim")
                            msg_text.append("  ")
                            msg_text.append("⠋", style="cyan")
                            msg_text.append(" ", style="dim")
                            msg_text.append(f"{loader.get_message()}...", style="dim")
                            live.update(msg_text)
                            time.sleep(0.5)
                    
                    display_thread = threading.Thread(target=update_display, daemon=True)
                    display_thread.start()
                    
                    response = self.ai_client.chat(
                        messages=messages,
                        tools=TOOL_DEFINITIONS,
                        temperature=0.7,
                        max_tokens=4096
                    )
            finally:
                loader.stop()
            
            # Check for errors
            if response.finish_reason == "error":
                self._handle_error_response(response.content)
                return ""
            
            console.print("  [dim]└─[/dim] [green]✓[/green] [dim]Ready[/dim]")
        
        # Get final response content
        # If no content but we did process tools, it might be the AI didn't generate a final response
        if not response.content and iteration > 0:
            final_response = "I analyzed the codebase but couldn't formulate a response. Please try rephrasing your question."
        else:
            final_response = response.content or "I couldn't generate a response. Please try again."
        
        # Add to history
        self.conversation_history.append({
            "role": "assistant",
            "content": final_response
        })
        
        # Update permanent memory if tools were used
        if tools_called and ORCPreferences.exists():
            self._update_permanent_memory(tools_called, all_tool_results)
        
        return final_response
    
    def _update_permanent_memory(self, tools_called: set, tool_results: list):
        """Update ORC.md with findings from this session"""
        try:
            # Extract useful data from tool results
            analysis_data = {
                "tools_used": list(tools_called),
                "total_files": None,
                "total_loc": None,
                "main_folders": [],
                "structure_summary": "",
                "known_issues": []
            }
            
            # Parse tool results for codebase info
            for result in tool_results:
                result_data = result.get("result", {})
                tool_name = result.get("name", "")
                
                # Extract from get_codebase_map
                if tool_name == "get_codebase_map" and isinstance(result_data, dict):
                    if "folders" in result_data:
                        analysis_data["main_folders"] = [f["path"] for f in result_data["folders"][:10]]
                    if "summary" in result_data:
                        analysis_data["structure_summary"] = result_data["summary"][:500]
                
                # Extract from get_codebase_stats
                elif tool_name == "get_codebase_stats" and isinstance(result_data, dict):
                    analysis_data["total_files"] = result_data.get("total_files")
                    analysis_data["total_loc"] = result_data.get("total_loc")
                
                # Extract from get_hotspots
                elif tool_name == "get_hotspots" and isinstance(result_data, dict):
                    if "complexity_hotspots" in result_data:
                        for hotspot in result_data["complexity_hotspots"][:3]:
                            issue = f"High complexity in {hotspot.get('file', 'unknown')}"
                            analysis_data["known_issues"].append(issue)
                
                # Extract from get_dead_code
                elif tool_name == "get_dead_code" and isinstance(result_data, dict):
                    summary = result_data.get("summary", {})
                    dead_count = summary.get("total_potentially_unused", 0)
                    if dead_count > 0:
                        analysis_data["known_issues"].append(f"{dead_count} potentially unused functions")
            
            # Write to ORC.md
            if analysis_data["total_files"] or analysis_data["main_folders"] or analysis_data["known_issues"]:
                ORCMemory.write_permanent_memory(analysis_data)
                # Reload memory for next query
                self.permanent_memory = ORCMemory.read_permanent_memory()
        except Exception:
            # Silently fail - don't crash if memory update fails
            pass
    
    def _handle_error_response(self, error_content: str):
        """Handle error responses with nice formatting"""
        error_lower = error_content.lower()
        
        # Check for rate limit
        if "rate limit" in error_lower or "429" in error_content:
            # Try to extract wait time
            import re
            wait_match = re.search(r'(\d+m\d+s|\d+\s*minutes?|\d+\s*seconds?)', error_content)
            wait_time = wait_match.group(1) if wait_match else None
            
            # Extract provider name
            provider = "AI"
            if "groq" in error_lower:
                provider = "Groq"
            elif "deepseek" in error_lower:
                provider = "DeepSeek"
            elif "openai" in error_lower:
                provider = "OpenAI"
            elif "anthropic" in error_lower:
                provider = "Anthropic"
            
            show_rate_limit_panel(provider, wait_time)
        
        # Check for insufficient balance
        elif "insufficient balance" in error_lower or "402" in error_content:
            show_error_panel(
                "Insufficient Balance",
                "Your API account has run out of credits.",
                "Add credits to your account or switch providers with /providers"
            )
        
        # Check for invalid API key
        elif "invalid" in error_lower and "key" in error_lower:
            show_error_panel(
                "Invalid API Key",
                "The API key is invalid or expired.",
                "Check your .env file and update your API key"
            )
        
        # Generic error
        else:
            show_error_panel("Error", error_content)
    
    def run(self):
        """Run the interactive chat session"""
        # Display banner
        console.print(get_orc_banner())
        
        # Get codebase stats
        loc, languages = count_codebase_stats()
        console.print(print_startup_info(self.project_name, loc, languages))
        
        # Check AI availability
        if not self.ai_client.is_available():
            console.print("[yellow]Warning: No AI service available.[/yellow]")
            console.print("[dim]Set your API key in .env file. Type /providers for options.[/dim]")
            console.print()
        else:
            console.print(f"[dim]    AI: {self.ai_client.get_status()}[/dim]")
            console.print()
        
        # First run - ask about ORC.md
        if not ORCPreferences.exists():
            if ORCPreferences.first_run_prompt():
                from datetime import datetime
                project_info = {
                    "name": self.project_name,
                    "languages": languages,
                    "created": datetime.now().strftime("%Y-%m-%d"),
                }
                ORCPreferences.save({}, project_info)
                console.print("\n[green]Created ORC.md![/green]")
                console.print("[dim]You can edit this file anytime to customize ORC's behavior.[/dim]\n")
            else:
                console.print("\n[dim]No problem! You can create it later with /preferences[/dim]\n")
        
        # Main loop
        while True:
            try:
                # Get user input - simple clean prompt
                if PROMPT_TOOLKIT_AVAILABLE:
                    try:
                        user_input = prompt(
                            [('class:prompt', '> ')],
                            completer=SlashCommandCompleter(),
                            style=prompt_style,
                            complete_while_typing=True,
                        ).strip()
                    except (EOFError, KeyboardInterrupt):
                        console.print("\n[dim]Session ended.[/dim]")
                        break
                else:
                    user_input = console.input("\n[green]>[/green] ").strip()
                
                if not user_input:
                    continue
                
                # Handle exit commands
                if user_input.lower() in ["exit", "quit", "q", "/exit", "/quit"]:
                    console.print("\n[dim]Session ended.[/dim]")
                    break
                
                # Show command suggestions when user types just "/"
                if user_input == "/":
                    self.show_command_suggestions()
                    continue
                
                # Handle slash commands
                if user_input.startswith("/"):
                    # Check for partial command and show suggestions
                    if " " not in user_input and len(user_input) > 1:
                        partial = user_input.lower()
                        commands = ["/help", "/status", "/providers", "/provider", "/models", "/model", "/clear", "/history", "/reset", "/compact", "/exit"]
                        matches = [c for c in commands if c.startswith(partial)]
                        # Filter out exact matches from suggestions
                        if partial in matches:
                            matches = [partial]
                        if len(matches) > 1:
                            console.print(f"[dim]Did you mean: {', '.join(matches)}[/dim]")
                            continue
                        elif len(matches) == 1 and matches[0] != partial:
                            # Auto-complete to the matched command
                            user_input = matches[0]
                    
                    self.handle_slash_command(user_input, loc, languages)
                    continue
                
                # Handle help command
                if user_input.lower() in ["help", "?"]:
                    self.show_help()
                    continue
                
                # Handle clear command
                if user_input.lower() == "clear":
                    self.conversation_history.clear()
                    console.clear()
                    console.print(get_orc_banner())
                    console.print(print_startup_info(self.project_name, loc, languages))
                    console.print("[dim]Conversation cleared.[/dim]")
                    continue
                
                # Handle simple greetings locally (no AI needed - but fake the loading!)
                greetings = ["hi", "hello", "hey", "yo", "hola", "howdy"]
                thanks = ["thanks", "thank you", "thx", "ty", "cheers"]
                if user_input.lower().strip() in greetings:
                    # Fake loading animation
                    loading_msg = random.choice(ORC_LOADING_MESSAGES)
                    with console.status(f"[cyan]{loading_msg}...[/cyan]", spinner="dots"):
                        time.sleep(random.uniform(0.5, 1.2))  # Fake thinking time
                    
                    responses = [
                        "Hey! What can I help you explore in your codebase today?",
                        "Hello! Ready to dive into your code. What would you like to analyze?",
                        "Hi there! What can I help you with?",
                        "Hey! What's on your mind?",
                    ]
                    console.print(f"\n{random.choice(responses)}\n")
                    continue
                
                if user_input.lower().strip() in thanks:
                    # Fake loading animation
                    loading_msg = random.choice(ORC_LOADING_MESSAGES)
                    with console.status(f"[cyan]{loading_msg}...[/cyan]", spinner="dots"):
                        time.sleep(random.uniform(0.3, 0.8))  # Shorter for thanks
                    
                    responses = [
                        "You're welcome! Let me know if there's anything else.",
                        "Happy to help! What else would you like to explore?",
                        "Anytime! Need anything else?",
                    ]
                    console.print(f"\n{random.choice(responses)}\n")
                    continue
                
                # Process with AI
                response = self.chat(user_input)
                
                # Display response with nice formatting
                if response:
                    console.print()
                    console.print(Panel(
                        format_response(response),
                        border_style="dim",
                        box=ROUNDED,
                        padding=(1, 2),
                    ))
                    
                    # Show memory bar below response
                    show_memory_bar(self)
                
            except KeyboardInterrupt:
                console.print("\n\n[dim]Session ended.[/dim]")
                break
            except Exception as e:
                console.print(f"\n[red]Error: {str(e)}[/red]")
                continue
    
    def show_command_suggestions(self):
        """Show faint command suggestions when user types /"""
        console.print("""
[dim]  /help        /status      /providers   /provider <name>
  /models      /model <name> /clear       /history
  /reset       /compact     /exit[/dim]
""")
    
    def handle_slash_command(self, command: str, loc: int, languages: list):
        """Handle slash commands for AI interface control"""
        parts = command.split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        if cmd == "/help":
            self.show_slash_help()
        
        elif cmd == "/models":
            # Always show model info for /models
            self.show_models()
        
        elif cmd == "/model":
            if args:
                # Switch model if argument provided
                self.switch_model(args)
            else:
                # Show model info if no argument
                self.show_models()
        
        elif cmd == "/provider" or cmd == "/providers":
            if args:
                self.switch_provider(args)
            else:
                self.show_providers()
        
        elif cmd == "/setup":
            if args:
                self.setup_provider(args)
            else:
                console.print("[yellow]Usage: /setup <provider>[/yellow]")
                console.print("[dim]Example: /setup groq[/dim]")
        
        elif cmd == "/status":
            self.show_status()
        
        elif cmd == "/clear":
            self.conversation_history.clear()
            console.clear()
            console.print(get_orc_banner())
            console.print(print_startup_info(self.project_name, loc, languages))
            console.print("[dim]Conversation cleared.[/dim]")
        
        elif cmd == "/history":
            self.show_history()
        
        elif cmd == "/reset":
            self.conversation_history.clear()
            reset_ai_client()
            self.ai_client = get_ai_client(force_new=True)
            console.print("[green]AI client reset. Conversation cleared.[/green]")
        
        elif cmd == "/compact":
            # Toggle compact mode
            if not hasattr(self, 'compact_mode'):
                self.compact_mode = False
            self.compact_mode = not self.compact_mode
            mode = "on" if self.compact_mode else "off"
            console.print(f"[cyan]Compact mode: {mode}[/cyan]")

        elif cmd == "/preferences" or cmd == "/prefs":
            self.manage_preferences(loc, languages)

        elif cmd == "/add-provider":
            self.add_custom_provider()

        elif cmd == "/remove-provider":
            self.remove_custom_provider()

        elif cmd == "/list-providers":
            self.list_all_providers()

        else:
            console.print(f"[yellow]Unknown command: {cmd}[/yellow]")
            console.print("[dim]Type /help for available commands[/dim]")
    
    def manage_preferences(self, loc: int, languages: list):
        """Manage ORC.md preferences"""
        if ORCPreferences.exists():
            console.print("\n[cyan]ORC.md exists![/cyan]")
            console.print(f"[dim]Location: {ORCPreferences.ORC_MD_PATH.absolute()}[/dim]")
            console.print("\n[dim]Current preferences:[/dim]")
            for key, value in self.preferences.items():
                console.print(f"  {key}: {value}")
            console.print("\n[dim]Edit ORC.md directly to change preferences.[/dim]\n")
        else:
            console.print("\n[dim]ORC.md doesn't exist yet.[/dim]")
            response = console.input("[green]Create it now? (yes/no):[/green] ").strip().lower()
            if response in ["yes", "y", "yeah", "yep", "sure", "ok"]:
                from datetime import datetime
                project_info = {
                    "name": self.project_name,
                    "languages": languages,
                    "created": datetime.now().strftime("%Y-%m-%d"),
                }
                ORCPreferences.save({}, project_info)
                self.preferences = ORCPreferences.load()
                console.print("\n[green]Created ORC.md![/green]\n")
            else:
                console.print("[dim]No problem![/dim]\n")
    
    def show_slash_help(self):
        """Show slash command help"""
        help_text = """
[cyan]Slash Commands:[/cyan]

  [bold]/help[/bold]              - Show this help
  [bold]/status[/bold]            - Show current AI provider and status
  [bold]/providers[/bold]         - List all available AI providers
  [bold]/provider <name>[/bold]   - Switch to a specific provider (groq, ollama, etc.)
  [bold]/models[/bold]            - Show current model info
  [bold]/model <name>[/bold]      - Switch to a different model
  [bold]/clear[/bold]             - Clear conversation history
  [bold]/history[/bold]           - Show conversation history
  [bold]/reset[/bold]             - Reset AI client and clear history
  [bold]/compact[/bold]           - Toggle compact response mode
  [bold]/preferences[/bold]       - Manage ORC.md preferences file
  [bold]/exit[/bold]              - Exit the session

[dim]Examples:[/dim]
  /provider groq
  /provider ollama
  /model llama-3.1-8b-instant
"""
        console.print(help_text)
    
    def add_custom_provider(self):
        """Add a new custom AI provider"""
        from .config import get_config, CustomProvider
        
        console.print("\n[cyan]Add Custom AI Provider[/cyan]\n")
        
        name = console.input("[green]Provider name:[/green] ").strip()
        if not name:
            console.print("[red]Name is required[/red]")
            return
        
        api_key = console.input("[green]API key:[/green] ").strip()
        if not api_key:
            console.print("[red]API key is required[/red]")
            return
        
        base_url = console.input("[green]Base URL:[/green] ").strip()
        if not base_url:
            console.print("[red]Base URL is required[/red]")
            return
        
        model = console.input("[green]Model name (default: default):[/green] ").strip() or "default"
        
        auth_type = console.input("[green]Auth type (bearer/api_key/custom) [bearer]:[/green] ").strip() or "bearer"
        
        supports_tools = console.input("[green]Supports tools? (y/n) [y]:[/green] ").strip().lower() != "n"
        
        try:
            config = get_config()
            provider = CustomProvider(
                name=name,
                api_key=api_key,
                base_url=base_url,
                model=model,
                auth_type=auth_type,
                supports_tools=supports_tools
            )
            
            config.save_custom_provider(provider)
            
            # Reset AI client to pick up new provider
            reset_ai_client()
            self.ai_client = get_ai_client(force_new=True)
            
            console.print(f"\n[green]✓ Added custom provider: {name}[/green]\n")
            
        except Exception as e:
            console.print(f"\n[red]Error adding provider: {str(e)}[/red]\n")
    
    def remove_custom_provider(self):
        """Remove a custom AI provider"""
        from .config import get_config
        
        config = get_config()
        custom_providers = config.load_custom_providers()
        
        if not custom_providers:
            console.print("[dim]No custom providers configured[/dim]")
            return
        
        console.print("\n[cyan]Custom Providers:[/cyan]\n")
        for i, name in enumerate(custom_providers.keys(), 1):
            console.print(f"  {i}. {name}")
        
        name = console.input("\n[green]Provider name to remove:[/green] ").strip()
        
        if name in custom_providers:
            if config.remove_custom_provider(name):
                # Reset AI client
                reset_ai_client()
                self.ai_client = get_ai_client(force_new=True)
                console.print(f"\n[green]✓ Removed custom provider: {name}[/green]\n")
            else:
                console.print(f"\n[red]Failed to remove provider: {name}[/red]\n")
        else:
            console.print(f"[red]Provider not found: {name}[/red]")
    
    def list_all_providers(self):
        """List all available providers including custom ones"""
        from .config import get_config
        
        config = get_config()
        all_providers = config.list_all_providers()
        current = self.ai_client.active_provider.name.lower() if self.ai_client.active_provider else None
        
        console.print("\n[cyan]All Available Providers:[/cyan]\n")
        
        for name, info in all_providers.items():
            if name == current:
                console.print(f"  [green]● {info['name']}[/green] - {info['description']} [green](active)[/green]")
            else:
                console.print(f"  [cyan]● {info['name']}[/cyan] - {info['description']}")
        
        console.print("\n[dim]Switch with: /provider <name>[/dim]\n")
    
    def show_providers(self):
        """Show all available AI providers"""
        console.print("\n[cyan]ORC AI Providers (BYOK - Bring Your Own Key):[/cyan]\n")
        console.print("[dim]ORC is open source - users provide their own API keys[/dim]\n")
        
        available = self.ai_client.get_available_providers()
        current = self.ai_client.active_provider.name.lower() if self.ai_client.active_provider else None
        
        providers_info = [
            ("ollama", "Ollama", "FREE - Local, no key needed", "ollama.ai"),
            ("groq", "Groq", "FREE tier - 100k tokens/day [Recommended]", "console.groq.com"),
            ("gemini", "Gemini", "FREE tier - 1M tokens/day", "makersuite.google.com"),
            ("deepseek", "DeepSeek", "CHEAP - $0.14/1M tokens", "platform.deepseek.com"),
            ("openai", "OpenAI", "PAID - GPT models", "platform.openai.com"),
            ("anthropic", "Anthropic", "PAID - Claude models", "console.anthropic.com"),
        ]
        
        for key, name, desc, url in providers_info:
            if key in available:
                if key == current:
                    console.print(f"  [green]* {name}[/green] - {desc} [green](active)[/green]")
                else:
                    console.print(f"  [cyan]* {name}[/cyan] - {desc}")
            else:
                console.print(f"  [dim]* {name} - {desc} (not configured)[/dim]")
                console.print(f"    [dim]Setup: /setup {key}[/dim]")
        
        console.print("\n[dim]Configure a provider: /setup <provider>[/dim]")
        console.print("[dim]Switch providers: /provider <name>[/dim]\n")
    
    def setup_provider(self, provider_name: str):
        """Interactive setup for a provider"""
        provider_name = provider_name.lower().strip()
        
        provider_configs = {
            "ollama": {
                "name": "Ollama",
                "key_name": None,
                "url": "ollama.ai",
                "instructions": "Install Ollama from ollama.ai, then run: ollama pull llama3.1"
            },
            "groq": {
                "name": "Groq",
                "key_name": "GROQ_API_KEY",
                "key_prefix": "gsk_",
                "url": "console.groq.com",
                "models": ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"]
            },
            "gemini": {
                "name": "Gemini",
                "key_name": "GEMINI_API_KEY",
                "url": "makersuite.google.com/app/apikey",
                "models": ["gemini-1.5-flash", "gemini-1.5-pro"]
            },
            "deepseek": {
                "name": "DeepSeek",
                "key_name": "DEEPSEEK_API_KEY",
                "key_prefix": "sk-",
                "url": "platform.deepseek.com",
                "models": ["deepseek-chat", "deepseek-coder"]
            },
            "openai": {
                "name": "OpenAI",
                "key_name": "OPENAI_API_KEY",
                "key_prefix": "sk-",
                "url": "platform.openai.com",
                "models": ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo"]
            },
            "anthropic": {
                "name": "Anthropic",
                "key_name": "ANTHROPIC_API_KEY",
                "key_prefix": "sk-ant-",
                "url": "console.anthropic.com",
                "models": ["claude-3-haiku-20240307", "claude-3-sonnet-20240229", "claude-3-opus-20240229"]
            },
        }
        
        if provider_name not in provider_configs:
            console.print(f"[red]Unknown provider: {provider_name}[/red]")
            console.print("[dim]Available: ollama, groq, gemini, deepseek, openai, anthropic[/dim]")
            return
        
        config = provider_configs[provider_name]
        console.print(f"\n[cyan]Setup {config['name']}[/cyan]\n")
        
        # Special case for Ollama
        if provider_name == "ollama":
            console.print(f"[dim]{config['instructions']}[/dim]")
            console.print(f"\n[dim]Get it at: {config['url']}[/dim]\n")
            return
        
        # For API-based providers
        console.print(f"[dim]Get your API key at: {config['url']}[/dim]\n")
        
        # Get API key
        api_key = console.input(f"[green]Enter your {config['name']} API key:[/green] ").strip()
        
        if not api_key:
            console.print("[yellow]Setup cancelled[/yellow]")
            return
        
        # Optional: choose model
        if "models" in config and len(config["models"]) > 1:
            console.print(f"\n[dim]Available models:[/dim]")
            for i, model in enumerate(config["models"], 1):
                default = " (default)" if i == 1 else ""
                console.print(f"  {i}. {model}{default}")
            
            model_choice = console.input(f"\n[green]Choose model (1-{len(config['models'])}) or press Enter for default:[/green] ").strip()
            
            if model_choice.isdigit() and 1 <= int(model_choice) <= len(config["models"]):
                model = config["models"][int(model_choice) - 1]
            else:
                model = config["models"][0]
        else:
            model = config.get("models", [None])[0] if "models" in config else None
        
        # Save to .env
        env_path = Path.cwd() / ".env"
        
        # Read existing .env
        env_lines = []
        if env_path.exists():
            env_lines = env_path.read_text().splitlines()
        
        # Update or add the key
        key_name = config["key_name"]
        key_found = False
        for i, line in enumerate(env_lines):
            if line.startswith(f"{key_name}="):
                env_lines[i] = f"{key_name}={api_key}"
                key_found = True
                break
        
        if not key_found:
            env_lines.append(f"{key_name}={api_key}")
        
        # Add model if specified
        if model:
            model_key = f"{provider_name.upper()}_MODEL"
            model_found = False
            for i, line in enumerate(env_lines):
                if line.startswith(f"{model_key}="):
                    env_lines[i] = f"{model_key}={model}"
                    model_found = True
                    break
            if not model_found:
                env_lines.append(f"{model_key}={model}")
        
        # Write back to .env
        env_path.write_text("\n".join(env_lines) + "\n")
        
        console.print(f"\n[green]Configured {config['name']}![/green]")
        console.print(f"[dim]API key saved to .env[/dim]")
        if model:
            console.print(f"[dim]Model: {model}[/dim]")
        
        # Reset AI client to pick up new config
        console.print("\n[dim]Reloading AI client...[/dim]")
        _load_env()
        reset_ai_client()
        self.ai_client = get_ai_client(force_new=True)
        
        # Try to switch to the new provider
        if provider_name in self.ai_client.get_available_providers():
            self.ai_client.active_provider = self.ai_client.providers[provider_name]
            console.print(f"[green]Switched to {config['name']}![/green]\n")
        else:
            console.print(f"[yellow]Provider configured but not available. Check your API key.[/yellow]\n")
    
    def switch_provider(self, provider_name: str):
        """Switch to a different AI provider"""
        provider_name = provider_name.lower().strip()
        
        if provider_name not in self.ai_client.providers:
            console.print(f"[red]Unknown provider: {provider_name}[/red]")
            console.print("[dim]Available: ollama, groq, gemini, deepseek, openai, anthropic[/dim]")
            return
        
        provider = self.ai_client.providers[provider_name]
        if not provider.is_available():
            console.print(f"[red]{provider.name} is not configured.[/red]")
            console.print(f"[dim]Run: /setup {provider_name}[/dim]")
            return
        
        self.ai_client.active_provider = provider
        self.ai_client.provider_order = [provider_name] + [p for p in self.ai_client.provider_order if p != provider_name]
        console.print(f"[green]Switched to {provider.name} ({provider.model})[/green]")
    
    def show_models(self):
        """Show current model info"""
        if not self.ai_client.active_provider:
            console.print("[yellow]No AI provider active[/yellow]")
            return
        
        provider = self.ai_client.active_provider
        console.print(f"\n[cyan]Current Model:[/cyan]")
        console.print(f"  Provider: {provider.name}")
        console.print(f"  Model: {provider.model}")
        console.print(f"\n[dim]Change with: /model <model_name>[/dim]")
        
        # Show available models for current provider
        if provider.name == "Groq":
            console.print("\n[dim]Popular Groq models:[/dim]")
            console.print("  llama-3.3-70b-versatile (default)")
            console.print("  llama-3.1-8b-instant (faster)")
            console.print("  mixtral-8x7b-32768")
        elif provider.name == "OpenAI":
            console.print("\n[dim]Popular OpenAI models:[/dim]")
            console.print("  gpt-4o-mini (default, cheap)")
            console.print("  gpt-4o (better)")
            console.print("  gpt-4-turbo")
        elif provider.name == "Anthropic":
            console.print("\n[dim]Popular Anthropic models:[/dim]")
            console.print("  claude-3-haiku-20240307 (default, fast)")
            console.print("  claude-3-sonnet-20240229")
            console.print("  claude-3-opus-20240229")
        elif provider.name == "Ollama":
            console.print("\n[dim]List local models: ollama list[/dim]")
        console.print()
    
    def switch_model(self, model_name: str):
        """Switch to a different model"""
        if not self.ai_client.active_provider:
            console.print("[yellow]No AI provider active[/yellow]")
            return
        
        self.ai_client.active_provider.model = model_name.strip()
        console.print(f"[green]Model changed to: {model_name}[/green]")
    
    def show_status(self):
        """Show current AI status"""
        console.print(f"\n[cyan]ORC Status:[/cyan]")
        console.print(f"  AI Provider: {self.ai_client.get_status()}")
        console.print(f"  Available: {', '.join(self.ai_client.get_available_providers()) or 'None'}")
        console.print(f"  Conversation: {len(self.conversation_history)} messages")
        console.print()
    
    def show_history(self):
        """Show conversation history"""
        if not self.conversation_history:
            console.print("[dim]No conversation history[/dim]")
            return
        
        console.print(f"\n[cyan]Conversation History ({len(self.conversation_history)} messages):[/cyan]\n")
        for i, msg in enumerate(self.conversation_history[-10:], 1):  # Show last 10
            role = msg["role"]
            content = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
            if role == "user":
                console.print(f"  [green]{i}. You:[/green] {content}")
            else:
                console.print(f"  [cyan]{i}. ORC:[/cyan] {content}")
        console.print()
    
    def show_help(self):
        """Show help information"""
        help_text = """
[cyan]ORC Commands:[/cyan]

[dim]You can ask natural language questions about your codebase:[/dim]

  show me authentication code
  find all security issues
  what are the performance bottlenecks
  find dead code in this project
  show me the most complex functions
  what would break if I delete user.py
  find all files that import flask
  search for TODO comments

[cyan]Slash Commands:[/cyan]

  /help       - Show all slash commands
  /status     - Show current AI provider
  /providers  - List available providers
  /provider X - Switch provider
  /models     - Show model info
  /clear      - Clear history
  /exit       - Exit

[dim]Type /help for more slash commands[/dim]
"""
        console.print(help_text)


def run_cli_session():
    """Main entry point for the CLI session"""
    session = ORCChatSession()
    session.run()


# Allow running directly
if __name__ == "__main__":
    # Check authentication before showing UI
    from orc.cli_auth import is_authenticated, require_auth
    if not is_authenticated():
        require_auth()
    run_cli_session()
