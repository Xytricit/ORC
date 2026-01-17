"""
ORC Chat Loop Module

Interactive AI chat with session management and tool calling.

Author: ORC Team
Date: 2026-01-14
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Optional

from orc.cli.cli_style import CLIOutput
from orc.cli.ui_components import UIComponents
from orc.session.session_manager import SessionManager
from orc.session.token_tracker import TokenTracker

# Import AI components
try:
    from orc.ai.ai_client import AIClient, AIMessage
    from orc.ai.ai_tools import ORCTools, get_tools_for_ai, execute_tool
    from orc.storage.graph_db import GraphDB
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False


class ORCChatSession:
    """Interactive AI chat session with tool calling and slash commands."""
    
    SLASH_COMMANDS = {
        '/help': 'Show available commands and examples',
        '/clear': 'Clear conversation history',
        '/reset': 'Reset conversation (clear history)',
        '/mode': 'Set operational mode (auto|chat|work)',
        '/models': 'Manage AI models (view|new|edit|delete)',
        '/summarizer': 'Configure AI provider for summaries',
        '/save': 'Save conversation with optional name',
        '/load': 'Load saved session (by number or name)',
        '/sessions': 'List all saved sessions with timestamps',
        '/export': 'Export conversation to file (md|json)',
        '/copy': 'Copy last code block to clipboard',
        '/tokens': 'Show token usage stats',
        '/cost': 'Show estimated cost so far',
        '/context': 'Show context window usage',
        '/exit': 'Exit chat (also /quit)',
    }
    
    def __init__(self, root_path: str = '.', config: Optional[Dict] = None):
        """
        Initialize chat session.
        
        Args:
            root_path: Project root path
            config: Configuration dict
        """
        self.root_path = Path(root_path)
        self.config = config or {}
        self.output = CLIOutput()
        self.ui = UIComponents()
        self.session_manager = SessionManager()
        self.token_tracker = TokenTracker()
        
        self.messages: List[Dict] = []
        self.mode = 'auto'  # auto, chat, work
        self.running = False
        
        # Initialize AI client if available
        self.ai_client = None
        self.tools_instance = None
        
        if AI_AVAILABLE:
            try:
                # Get AI config
                ai_config = self.config.get('ai', {})
                provider = ai_config.get('provider', 'groq')
                model = ai_config.get('model')
                
                # Create AI client
                self.ai_client = AIClient(provider=provider, model=model)
                
                # Create tools instance (if database available)
                db_path = self.config.get('db_path', '.orc/graph.db')
                if Path(db_path).exists():
                    db = GraphDB(db_path)
                    self.tools_instance = ORCTools(db)
                
                self.output.success(f"AI initialized: {provider} ({self.ai_client.model})")
            except Exception as e:
                self.output.warning(f"AI initialization failed: {e}")
                self.output.info("Falling back to mock responses")
    
    def run(self) -> None:
        """Start interactive chat loop."""
        # Run onboarding if needed
        try:
            from orc.cli.onboarding import run_onboarding_if_needed
            if run_onboarding_if_needed():
                # Onboarding just ran, reload AI client
                self._initialize_ai()
        except ImportError:
            pass
        
        self.running = True
        
        # Show banner
        try:
            from orc.cli.banner import get_orc_banner
            from rich.console import Console
            console = Console()
            console.print(get_orc_banner())
            print()
        except ImportError:
            # Fallback to simple welcome
            print()
            self.output.print("=" * 60, 'accent')
            self.output.print("ORC Interactive Chat", 'accent')
            self.output.print("=" * 60, 'accent')
            print()
        
        # Check if database exists and load it
        db_path = Path('.orc/graph.db')
        toc_path = Path('.orc/toc.json')
        
        if db_path.exists():
            if not self.tools_instance:
                # Initialize database and tools if not already done
                try:
                    db = GraphDB(str(db_path))
                    self.tools_instance = ORCTools(db)
                    self.output.success("Database loaded - AI has access to your codebase")
                except Exception as e:
                    self.output.warning(f"Database found but failed to load: {e}")
            
            # Load TOC if available
            if toc_path.exists():
                self.output.info(f"TOC available for fast navigation")
            else:
                self.output.info("Tip: Run 'orc index' to generate searchable TOC")
        else:
            self.output.warning("No database found. Run 'orc index' to analyze your codebase")
        
        print()
        print("Type /help for available commands, /exit to quit")
        print()
        
        # Main loop
        while self.running:
            try:
                # Get user input
                user_input = self._get_input()
                
                if not user_input.strip():
                    continue
                
                # Handle slash commands
                if user_input.startswith('/'):
                    self._handle_slash_command(user_input)
                else:
                    # Regular message - would call AI here
                    self._handle_message(user_input)
                
            except KeyboardInterrupt:
                print()
                self.output.info("Use /exit to quit")
                print()
            except EOFError:
                break
        
        # Goodbye message
        print()
        self.output.success("Chat session ended. Goodbye!")
        print()
    
    def _get_input(self) -> str:
        """
        Get user input with prompt.
        
        Returns:
            str: User input
        """
        try:
            # Try to use prompt_toolkit for better experience
            from prompt_toolkit import PromptSession
            from prompt_toolkit.history import InMemoryHistory
            
            session = PromptSession(history=InMemoryHistory())
            return session.prompt("ORC > ")
        except ImportError:
            # Fallback to basic input
            return input("ORC > ")
    
    def _handle_message(self, message: str) -> None:
        """
        Handle regular user message.
        
        Args:
            message: User's message
        """
        # Add to messages
        self.messages.append({
            'role': 'user',
            'content': message
        })
        
        # Display user message
        self.ui.display_user_message(message)
        
        # Get AI response (real or mock)
        if self.ai_client and AI_AVAILABLE:
            ai_response = self._generate_ai_response(message)
        else:
            ai_response = self._generate_mock_response(message)
        
        # Add AI response to messages
        self.messages.append({
            'role': 'assistant',
            'content': ai_response
        })
        
        # Display AI response
        self.ui.display_ai_message(ai_response)
        
        # Update last code block
        self.session_manager.update_last_code_block(ai_response)
        
        # Auto-save
        if len(self.messages) % 10 == 0:
            self.session_manager.auto_save(self.messages)
    
    def _generate_ai_response(self, message: str) -> str:
        """
        Generate real AI response.
        
        Args:
            message: User message
        
        Returns:
            str: AI-generated response
        """
        try:
            # Build conversation history
            ai_messages = [
                AIMessage(
                    role='system',
                    content="You are ORC, an AI assistant for code analysis. You help developers understand, analyze, and improve their codebases."
                )
            ]
            
            # Add conversation history (last 10 messages)
            for msg in self.messages[-10:]:
                ai_messages.append(AIMessage(
                    role=msg['role'],
                    content=msg['content']
                ))
            
            # Get tools if available
            tools = None
            if self.tools_instance and self.mode in ['auto', 'work']:
                tools = get_tools_for_ai()
            
            # Call AI
            response = self.ai_client.chat(ai_messages, tools=tools)
            
            # Track tokens
            self.token_tracker.add_request(
                provider=response.provider,
                model=response.model,
                input_tokens=response.input_tokens,
                output_tokens=response.output_tokens
            )
            
            # Show token usage
            self._show_token_usage(response.input_tokens, response.output_tokens, response.provider)
            
            # Handle tool calls if present
            if response.tool_calls:
                return self._handle_tool_calls(response.tool_calls)
            
            return response.content
        
        except Exception as e:
            self.output.error(f"AI request failed: {e}")
            return self._generate_mock_response(message)
    
    def _handle_tool_calls(self, tool_calls: List[Dict]) -> str:
        """
        Handle AI tool calls.
        
        Args:
            tool_calls: List of tool call requests
        
        Returns:
            str: Results of tool execution
        """
        results = []
        
        for tool_call in tool_calls:
            tool_name = tool_call['function']['name']
            arguments = json.loads(tool_call['function']['arguments'])
            
            # Execute tool
            result = execute_tool(tool_name, arguments, self.tools_instance)
            results.append(f"Tool: {tool_name}\nResult: {result}")
        
        return "\n\n".join(results)
    
    def _initialize_ai(self) -> None:
        """(Re)initialize AI client after configuration."""
        if not AI_AVAILABLE:
            return
        
        try:
            # Load .env file
            from dotenv import load_dotenv
            env_path = Path.home() / ".orc" / ".env"
            if env_path.exists():
                load_dotenv(env_path)
            
            # Get provider from .env
            provider = os.getenv('ORC_AI_PROVIDER', 'groq')
            
            # Create AI client
            self.ai_client = AIClient(provider=provider)
            
            # Create tools instance (if database available)
            db_path = self.config.get('db_path', '.orc/graph.db')
            if Path(db_path).exists():
                db = GraphDB(db_path)
                self.tools_instance = ORCTools(db)
            
            self.output.success(f"AI initialized: {provider} ({self.ai_client.model})")
        except Exception as e:
            self.output.warning(f"AI initialization failed: {e}")
    
    def _show_token_usage(self, input_tokens: int, output_tokens: int, provider: str) -> None:
        """Show token usage after AI response."""
        try:
            from orc.cli.onboarding import ORCOnboarding
            onboarding = ORCOnboarding()
            onboarding.show_token_usage(input_tokens, output_tokens, provider)
        except:
            # Fallback: simple display
            total = input_tokens + output_tokens
            print()
            print(f"  Tokens: {total:,} (in: {input_tokens:,}, out: {output_tokens:,})")
    
    def _generate_mock_response(self, message: str) -> str:
        """
        Generate mock AI response for testing.
        
        Args:
            message: User message
        
        Returns:
            str: Mock response
        """
        if 'code' in message.lower():
            return """Here's a simple example:

```python
def hello_world():
    print("Hello, World!")
    return True
```

This function prints a greeting and returns True."""
        
        return f"I understand you said: '{message}'. This is a mock response for testing. In production, this would call an AI model."
    
    def _handle_slash_command(self, command: str) -> None:
        """
        Handle slash commands.
        
        Args:
            command: Slash command string
        """
        parts = command.split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ''
        
        # Handle / alone - show available commands
        if cmd == '/':
            self._cmd_show_commands()
            return
        
        if cmd == '/help':
            self._cmd_help()
        elif cmd == '/clear' or cmd == '/reset':
            self._cmd_clear()
        elif cmd == '/mode':
            self._cmd_mode(args)
        elif cmd == '/models':
            self._cmd_models(args)
        elif cmd == '/summarizer':
            self._cmd_summarizer(args)
        elif cmd == '/save':
            self._cmd_save(args)
        elif cmd == '/load':
            self._cmd_load(args)
        elif cmd == '/sessions':
            self._cmd_sessions()
        elif cmd == '/export':
            self._cmd_export(args)
        elif cmd == '/copy':
            self._cmd_copy()
        elif cmd == '/tokens':
            self._cmd_tokens()
        elif cmd == '/cost':
            self._cmd_cost()
        elif cmd == '/context':
            self._cmd_context()
        elif cmd in ['/exit', '/quit']:
            self._cmd_exit()
        else:
            self.output.error(f"Unknown command: {cmd}")
            self.output.info("Type / to see available commands")
    
    def _cmd_show_commands(self) -> None:
        """Show quick list of available commands."""
        print()
        print("Available Commands:")
        for cmd in self.SLASH_COMMANDS.keys():
            print(f"  {cmd}")
        print()
        print("Type /help for detailed information")
        print()
    
    def _cmd_help(self) -> None:
        """Show help for all commands."""
        print()
        self.output.start_phase("Available Commands")
        print()
        
        for cmd, description in self.SLASH_COMMANDS.items():
            print(f"  {cmd:<15} {description}")
        
        print()
        print("Examples:")
        print("  /mode auto              Set to auto mode")
        print("  /models                 View configured models")
        print("  /models new             Add new model")
        print("  /save my_session        Save with name 'my_session'")
        print("  /export md              Export to markdown")
        print()
    
    def _cmd_clear(self) -> None:
        """Clear conversation history."""
        self.messages = []
        self.output.success("Conversation history cleared")
    
    def _cmd_mode(self, mode: str) -> None:
        """
        Set operational mode.
        
        Args:
            mode: Mode name (auto|chat|work)
        """
        mode = mode.lower().strip()
        
        if mode in ['auto', 'chat', 'work']:
            self.mode = mode
            self.output.success(f"Mode set to: {mode}")
            
            if mode == 'auto':
                self.output.info("AI will use tools when useful")
            elif mode == 'chat':
                self.output.info("General conversation, minimal tools")
            elif mode == 'work':
                self.output.info("Intensive analysis, use all tools")
        else:
            self.output.error("Invalid mode. Use: auto, chat, or work")
    
    def _cmd_summarizer(self, provider: str) -> None:
        """
        Configure AI provider.
        
        Args:
            provider: Provider name
        """
        if provider:
            self.output.success(f"AI provider set to: {provider}")
        else:
            current = self.config.get('ai', {}).get('provider', 'groq')
            self.output.info(f"Current provider: {current}")
    
    def _cmd_save(self, name: str) -> None:
        """
        Save conversation.
        
        Args:
            name: Session name
        """
        if not name:
            name = f"session_{len(self.messages)}"
        
        try:
            filepath = self.session_manager.save_session(name, self.messages)
            self.output.success(f"Session saved to: {filepath}")
        except Exception as e:
            self.output.error(f"Failed to save session: {e}")
    
    def _cmd_load(self, identifier: str) -> None:
        """
        Load saved session.
        
        Args:
            identifier: Session name or number
        """
        try:
            session_data = self.session_manager.load_session(identifier)
            
            if session_data:
                self.messages = session_data['messages']
                self.output.success(f"Loaded session: {session_data['name']}")
                self.output.info(f"Messages: {len(self.messages)}")
            else:
                self.output.warning(f"Session not found: {identifier}")
        
        except Exception as e:
            self.output.error(f"Failed to load session: {e}")
    
    def _cmd_sessions(self) -> None:
        """List all saved sessions."""
        sessions = self.session_manager.list_sessions()
        
        if not sessions:
            self.output.info("No saved sessions")
            return
        
        print()
        self.output.start_phase(f"Saved Sessions ({len(sessions)})")
        print()
        
        for i, (name, timestamp, count) in enumerate(sessions, 1):
            print(f"  {i}. {name}")
            print(f"     Time: {timestamp}")
            print(f"     Messages: {count}")
            print()
    
    def _cmd_export(self, format_type: str) -> None:
        """
        Export conversation.
        
        Args:
            format_type: Export format (md|json)
        """
        format_type = format_type.lower().strip()
        
        if not format_type:
            format_type = 'md'
        
        try:
            if format_type == 'md':
                filepath = self.session_manager.export_to_markdown(
                    self.messages,
                    'orc_conversation.md'
                )
                self.output.success(f"Exported to: {filepath}")
            
            elif format_type == 'json':
                filepath = self.session_manager.export_to_json(
                    self.messages,
                    'orc_conversation.json'
                )
                self.output.success(f"Exported to: {filepath}")
            
            else:
                self.output.error("Invalid format. Use: md or json")
        
        except Exception as e:
            self.output.error(f"Export failed: {e}")
    
    def _cmd_copy(self) -> None:
        """Copy last code block to clipboard."""
        code = self.session_manager.get_last_code_block()
        
        if code:
            try:
                # Try to copy to clipboard
                import pyperclip
                pyperclip.copy(code)
                self.output.success("Code block copied to clipboard")
            except ImportError:
                # Fallback: just display
                print()
                self.output.info("Clipboard not available. Here's the code:")
                print()
                print(code)
                print()
        else:
            self.output.warning("No code block found in last response")
    
    def _cmd_tokens(self) -> None:
        """Show token usage statistics."""
        stats = self.token_tracker.get_statistics()
        
        print()
        self.output.start_phase("Token Usage Statistics")
        print()
        print(f"  Total Requests: {stats['total_requests']}")
        print(f"  Total Tokens: {stats['total_tokens']:,}")
        print(f"  Input Tokens: {stats['total_input_tokens']:,}")
        print(f"  Output Tokens: {stats['total_output_tokens']:,}")
        print()
        
        if stats['by_provider']:
            print("  By Provider:")
            for provider, data in stats['by_provider'].items():
                print(f"    {provider}: {data['total_tokens']:,} tokens")
            print()
    
    def _cmd_cost(self) -> None:
        """Show estimated cost."""
        stats = self.token_tracker.get_statistics()
        
        print()
        self.output.start_phase("Cost Estimate")
        print()
        print(f"  Total Cost: ${stats['total_cost']:.4f}")
        print()
        
        if stats['by_provider']:
            print("  By Provider:")
            for provider, data in stats['by_provider'].items():
                print(f"    {provider}: ${data['cost']:.4f}")
            print()
    
    def _cmd_context(self) -> None:
        """Show context window usage."""
        total_tokens = sum(len(msg['content'].split()) * 1.3 
                          for msg in self.messages)
        
        print()
        self.output.start_phase("Context Window")
        print()
        print(f"  Messages: {len(self.messages)}")
        print(f"  Estimated Tokens: {int(total_tokens):,}")
        print()
    
    def _cmd_models(self, args: str) -> None:
        """
        Manage AI models.
        
        Args:
            args: Subcommand (view|new|edit|delete)
        """
        from dotenv import load_dotenv, set_key, unset_key
        import os
        
        env_path = Path.home() / ".orc" / ".env"
        
        # Ensure .env exists
        if not env_path.exists():
            env_path.parent.mkdir(parents=True, exist_ok=True)
            env_path.touch()
        
        # Parse subcommand
        parts = args.split(maxsplit=1)
        subcmd = parts[0].lower() if parts else 'view'
        
        if subcmd in ['view', 'list', '']:
            self._cmd_models_view(env_path)
        elif subcmd == 'new':
            self._cmd_models_new(env_path)
        elif subcmd == 'edit':
            model_name = parts[1] if len(parts) > 1 else None
            self._cmd_models_edit(env_path, model_name)
        elif subcmd == 'delete':
            model_name = parts[1] if len(parts) > 1 else None
            self._cmd_models_delete(env_path, model_name)
        else:
            self.output.error(f"Unknown subcommand: {subcmd}")
            self.output.info("Usage: /models [view|new|edit|delete]")
    
    def _cmd_models_view(self, env_path: Path) -> None:
        """View configured models."""
        from dotenv import dotenv_values
        
        config = dotenv_values(env_path)
        
        # Get all model configurations
        models = {}
        for key, value in config.items():
            if key.startswith('ORC_MODEL_'):
                model_name = key.replace('ORC_MODEL_', '', 1).split('_')[0]
                if model_name not in models:
                    models[model_name] = {}
                
                field = key.replace(f'ORC_MODEL_{model_name}_', '')
                models[model_name][field] = value
        
        current_provider = config.get('ORC_AI_PROVIDER', 'Not set')
        
        print()
        self.output.start_phase("Configured Models")
        print()
        print(f"  Current Provider: {current_provider}")
        print()
        
        if models:
            for name, info in models.items():
                is_current = (info.get('PROVIDER') == current_provider)
                marker = " (active)" if is_current else ""
                print(f"  {name}{marker}")
                print(f"    Provider: {info.get('PROVIDER', 'N/A')}")
                print(f"    Model: {info.get('MODEL', 'N/A')}")
                if 'BASE_URL' in info:
                    print(f"    Base URL: {info['BASE_URL']}")
                print()
        else:
            print("  No models configured")
            print()
        
        print("  Tip: Type '/models new' to add a new model")
        print()
    
    def _cmd_models_new(self, env_path: Path) -> None:
        """Add new model configuration."""
        from dotenv import set_key
        
        print()
        self.output.start_phase("Add New Model")
        print()
        
        # Get model name
        model_name = input("  Model name (e.g., groq-llama, openai-gpt4): ").strip()
        if not model_name:
            self.output.error("Model name required")
            return
        
        # Get provider
        print()
        print("  Available providers:")
        print("    1. groq")
        print("    2. openai")
        print("    3. anthropic")
        print("    4. deepseek")
        print("    5. ollama")
        print()
        provider = input("  Provider: ").strip().lower()
        if not provider:
            self.output.error("Provider required")
            return
        
        # Get model ID
        model_id = input(f"  Model ID (e.g., llama-3.1-70b-versatile, gpt-4): ").strip()
        if not model_id:
            self.output.error("Model ID required")
            return
        
        # Get API key
        api_key = input("  API key: ").strip()
        if not api_key and provider != 'ollama':
            self.output.error("API key required")
            return
        
        # Get base URL (only for ollama)
        base_url = None
        if provider == 'ollama':
            base_url = input("  Base URL (press Enter for http://localhost:11434): ").strip()
            if not base_url:
                base_url = "http://localhost:11434"
        
        # Save to .env
        model_prefix = f"ORC_MODEL_{model_name.upper()}"
        set_key(env_path, f"{model_prefix}_PROVIDER", provider)
        set_key(env_path, f"{model_prefix}_MODEL", model_id)
        
        if api_key:
            # Save API key with provider-specific format
            if provider == 'groq':
                set_key(env_path, 'GROQ_API_KEY', api_key)
            elif provider == 'openai':
                set_key(env_path, 'OPENAI_API_KEY', api_key)
            elif provider == 'anthropic':
                set_key(env_path, 'ANTHROPIC_API_KEY', api_key)
            elif provider == 'deepseek':
                set_key(env_path, 'DEEPSEEK_API_KEY', api_key)
        
        if base_url:
            set_key(env_path, f"{model_prefix}_BASE_URL", base_url)
        
        print()
        self.output.success(f"Model '{model_name}' added successfully")
        print()
    
    def _cmd_models_edit(self, env_path: Path, model_name: Optional[str]) -> None:
        """Edit existing model configuration."""
        if not model_name:
            self.output.error("Usage: /models edit <model_name>")
            return
        
        from dotenv import dotenv_values, set_key
        
        config = dotenv_values(env_path)
        model_prefix = f"ORC_MODEL_{model_name.upper()}"
        
        # Check if model exists
        provider_key = f"{model_prefix}_PROVIDER"
        if provider_key not in config:
            self.output.error(f"Model '{model_name}' not found")
            return
        
        print()
        self.output.start_phase(f"Edit Model: {model_name}")
        print()
        
        # Show current values
        current_provider = config.get(provider_key)
        current_model = config.get(f"{model_prefix}_MODEL")
        current_url = config.get(f"{model_prefix}_BASE_URL")
        
        print(f"  Current Provider: {current_provider}")
        print(f"  Current Model: {current_model}")
        if current_url:
            print(f"  Current Base URL: {current_url}")
        print()
        
        # Get new values
        provider = input(f"  New provider (Enter to keep '{current_provider}'): ").strip().lower()
        if not provider:
            provider = current_provider
        
        model_id = input(f"  New model ID (Enter to keep '{current_model}'): ").strip()
        if not model_id:
            model_id = current_model
        
        # Update
        set_key(env_path, provider_key, provider)
        set_key(env_path, f"{model_prefix}_MODEL", model_id)
        
        print()
        self.output.success(f"Model '{model_name}' updated")
        print()
    
    def _cmd_models_delete(self, env_path: Path, model_name: Optional[str]) -> None:
        """Delete model configuration."""
        if not model_name:
            self.output.error("Usage: /models delete <model_name>")
            return
        
        from dotenv import dotenv_values
        
        config = dotenv_values(env_path)
        model_prefix = f"ORC_MODEL_{model_name.upper()}"
        
        # Check if model exists
        provider_key = f"{model_prefix}_PROVIDER"
        if provider_key not in config:
            self.output.error(f"Model '{model_name}' not found")
            return
        
        # Confirm deletion
        confirm = input(f"  Delete model '{model_name}'? (y/N): ").strip().lower()
        if confirm != 'y':
            self.output.info("Cancelled")
            return
        
        # Remove from .env by rewriting file
        lines = []
        if env_path.exists():
            with open(env_path, 'r') as f:
                lines = f.readlines()
        
        # Filter out lines for this model
        new_lines = [line for line in lines if not line.startswith(model_prefix)]
        
        with open(env_path, 'w') as f:
            f.writelines(new_lines)
        
        print()
        self.output.success(f"Model '{model_name}' deleted")
        print()
    
    def _cmd_exit(self) -> None:
        """Exit chat session."""
        # Auto-save before exit
        if self.messages:
            self.session_manager.auto_save(self.messages)
        
        self.running = False


def main():
    """Entry point for chat loop."""
    chat = ORCChatSession()
    chat.run()


if __name__ == '__main__':
    main()
