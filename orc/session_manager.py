"""
Session Management for ORC Chat
Handles saving, loading, and exporting conversations
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from rich.console import Console

console = Console()


class SessionManager:
    """Manage chat sessions - save, load, export"""
    
    def __init__(self, sessions_dir: Optional[Path] = None):
        """
        Initialize session manager
        
        Args:
            sessions_dir: Directory to store sessions (default: .orc/sessions)
        """
        if sessions_dir is None:
            sessions_dir = Path.cwd() / ".orc" / "sessions"
        
        self.sessions_dir = sessions_dir
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        
        # Current session tracking
        self.current_session_name: Optional[str] = None
        self.last_code_block: Optional[str] = None
    
    def save_session(self, name: str, conversation_history: List[Dict[str, str]], 
                     metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Save conversation to disk
        
        Args:
            name: Session name (alphanumeric + underscores)
            conversation_history: List of message dicts
            metadata: Optional metadata (tokens, cost, etc.)
        
        Returns:
            True if saved successfully
        """
        try:
            # Sanitize filename
            safe_name = "".join(c for c in name if c.isalnum() or c in "_-")
            if not safe_name:
                safe_name = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Build session data
            session_data = {
                "name": name,
                "saved_at": datetime.now().isoformat(),
                "conversation": conversation_history,
                "metadata": metadata or {}
            }
            
            # Save to file
            session_file = self.sessions_dir / f"{safe_name}.json"
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
            
            self.current_session_name = safe_name
            return True
            
        except Exception as e:
            console.print(f"[red]Failed to save session: {e}[/red]")
            return False
    
    def load_session(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Load conversation from disk
        
        Args:
            name: Session name to load
        
        Returns:
            Session data dict or None if not found
        """
        try:
            # Try exact match first
            session_file = self.sessions_dir / f"{name}.json"
            
            if not session_file.exists():
                # Try fuzzy match
                matches = list(self.sessions_dir.glob(f"*{name}*.json"))
                if not matches:
                    return None
                session_file = matches[0]
            
            with open(session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            self.current_session_name = session_file.stem
            return session_data
            
        except Exception as e:
            console.print(f"[red]Failed to load session: {e}[/red]")
            return None
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """
        List all saved sessions
        
        Returns:
            List of dicts with session info (name, date, message_count)
        """
        sessions = []
        
        try:
            for session_file in sorted(self.sessions_dir.glob("*.json"), 
                                      key=lambda p: p.stat().st_mtime, 
                                      reverse=True):
                try:
                    with open(session_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    sessions.append({
                        "name": session_file.stem,
                        "saved_at": data.get("saved_at", "Unknown"),
                        "message_count": len(data.get("conversation", [])),
                        "metadata": data.get("metadata", {})
                    })
                except:
                    continue
        except Exception:
            pass
        
        return sessions
    
    def delete_session(self, name: str) -> bool:
        """Delete a saved session"""
        try:
            session_file = self.sessions_dir / f"{name}.json"
            if session_file.exists():
                session_file.unlink()
                return True
            return False
        except Exception:
            return False
    
    def export_to_markdown(self, conversation_history: List[Dict[str, str]], 
                          output_file: Optional[Path] = None) -> Optional[str]:
        """
        Export conversation to markdown format
        
        Args:
            conversation_history: List of message dicts
            output_file: Optional file path to write to
        
        Returns:
            Markdown string or None if failed
        """
        try:
            lines = [
                f"# ORC Conversation Export",
                f"",
                f"**Exported:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"**Messages:** {len(conversation_history)}",
                f"",
                "---",
                ""
            ]
            
            for i, msg in enumerate(conversation_history, 1):
                role = msg.get("role", "unknown")
                content = msg.get("content", "")
                
                if role == "user":
                    lines.append(f"## Message {i}: You")
                    lines.append("")
                    lines.append(content)
                elif role == "assistant":
                    lines.append(f"## Message {i}: ORC")
                    lines.append("")
                    lines.append(content)
                
                lines.append("")
                lines.append("---")
                lines.append("")
            
            markdown = "\n".join(lines)
            
            # Write to file if specified
            if output_file:
                output_file.write_text(markdown, encoding='utf-8')
            
            return markdown
            
        except Exception as e:
            console.print(f"[red]Failed to export to markdown: {e}[/red]")
            return None
    
    def export_to_json(self, conversation_history: List[Dict[str, str]], 
                      output_file: Optional[Path] = None,
                      metadata: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Export conversation to JSON format
        
        Args:
            conversation_history: List of message dicts
            output_file: Optional file path to write to
            metadata: Optional metadata to include
        
        Returns:
            JSON string or None if failed
        """
        try:
            export_data = {
                "exported_at": datetime.now().isoformat(),
                "message_count": len(conversation_history),
                "conversation": conversation_history,
                "metadata": metadata or {}
            }
            
            json_str = json.dumps(export_data, indent=2, ensure_ascii=False)
            
            # Write to file if specified
            if output_file:
                output_file.write_text(json_str, encoding='utf-8')
            
            return json_str
            
        except Exception as e:
            console.print(f"[red]Failed to export to JSON: {e}[/red]")
            return None
    
    def auto_save(self, conversation_history: List[Dict[str, str]], 
                  metadata: Optional[Dict[str, Any]] = None):
        """
        Auto-save conversation with timestamp name
        Keeps only last 10 auto-saves
        """
        try:
            # Save with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            self.save_session(f"auto_{timestamp}", conversation_history, metadata)
            
            # Clean up old auto-saves (keep last 10)
            auto_saves = sorted(
                self.sessions_dir.glob("auto_*.json"),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )
            
            for old_save in auto_saves[10:]:
                try:
                    old_save.unlink()
                except:
                    pass
                    
        except Exception:
            pass  # Silent fail for auto-save
    
    def update_last_code_block(self, message: str):
        """Extract and store last code block from message"""
        import re
        
        # Find all code blocks
        code_blocks = re.findall(r'```(?:\w+)?\n(.*?)```', message, re.DOTALL)
        
        if code_blocks:
            self.last_code_block = code_blocks[-1].strip()
    
    def get_last_code_block(self) -> Optional[str]:
        """Get the last code block from conversation"""
        return self.last_code_block
