"""
ORC Session Manager Module

Manage conversation persistence, saving, loading, and export.

Author: ORC Team
Date: 2026-01-14
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class SessionManager:
    """Manage conversation sessions with persistence and export."""
    
    def __init__(self, sessions_dir: str = ".orc/sessions"):
        """
        Initialize session manager.
        
        Args:
            sessions_dir: Directory to store session files
        """
        self.sessions_dir = Path(sessions_dir)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self.last_code_block: Optional[str] = None
    
    def save_session(self, name: str, messages: List[Dict], metadata: Optional[Dict] = None) -> str:
        """
        Save conversation session to file.
        
        Args:
            name: Session name
            messages: List of message dicts with 'role' and 'content'
            metadata: Optional metadata dict
        
        Returns:
            str: Path to saved session file
        """
        timestamp = datetime.now().isoformat()
        
        session_data = {
            'name': name,
            'timestamp': timestamp,
            'message_count': len(messages),
            'metadata': metadata or {},
            'messages': messages
        }
        
        # Create filename from name and timestamp
        safe_name = re.sub(r'[^\w\s-]', '', name).strip().replace(' ', '_')
        filename = f"{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.sessions_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
        
        return str(filepath)
    
    def load_session(self, name: str) -> Optional[Dict]:
        """
        Load session by name (loads most recent if multiple matches).
        
        Args:
            name: Session name or partial name
        
        Returns:
            dict: Session data with 'messages' and 'metadata', or None if not found
        """
        # Find matching sessions
        matching_files = []
        for filepath in self.sessions_dir.glob("*.json"):
            if name.lower() in filepath.stem.lower():
                matching_files.append(filepath)
        
        if not matching_files:
            return None
        
        # Load most recent
        latest_file = max(matching_files, key=lambda p: p.stat().st_mtime)
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def list_sessions(self) -> List[Tuple[str, str, int]]:
        """
        List all saved sessions.
        
        Returns:
            list: List of tuples (name, timestamp, message_count)
        """
        sessions = []
        
        for filepath in sorted(self.sessions_dir.glob("*.json"), 
                              key=lambda p: p.stat().st_mtime, 
                              reverse=True):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    sessions.append((
                        data.get('name', filepath.stem),
                        data.get('timestamp', ''),
                        data.get('message_count', 0)
                    ))
            except (json.JSONDecodeError, KeyError):
                continue
        
        return sessions
    
    def export_to_markdown(self, messages: List[Dict], output_path: str) -> str:
        """
        Export conversation to markdown format.
        
        Args:
            messages: List of message dicts
            output_path: Path to save markdown file
        
        Returns:
            str: Path to exported file
        """
        output_path = Path(output_path)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# ORC Conversation Export\n\n")
            f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Messages:** {len(messages)}\n\n")
            f.write("---\n\n")
            
            for i, msg in enumerate(messages, 1):
                role = msg.get('role', 'unknown').title()
                content = msg.get('content', '')
                
                f.write(f"## Message {i}: {role}\n\n")
                f.write(f"{content}\n\n")
                f.write("---\n\n")
        
        return str(output_path)
    
    def export_to_json(self, messages: List[Dict], output_path: str) -> str:
        """
        Export conversation to JSON format.
        
        Args:
            messages: List of message dicts
            output_path: Path to save JSON file
        
        Returns:
            str: Path to exported file
        """
        output_path = Path(output_path)
        
        export_data = {
            'export_date': datetime.now().isoformat(),
            'message_count': len(messages),
            'messages': messages
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        return str(output_path)
    
    def auto_save(self, messages: List[Dict], keep_last: int = 10) -> str:
        """
        Auto-save conversation and clean up old auto-saves.
        
        Args:
            messages: List of message dicts
            keep_last: Number of auto-saves to keep
        
        Returns:
            str: Path to auto-saved file
        """
        # Save with auto_ prefix
        filepath = self.save_session("auto_session", messages, {
            'auto_save': True
        })
        
        # Clean up old auto-saves
        auto_saves = sorted(
            self.sessions_dir.glob("auto_session_*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        # Remove old auto-saves beyond keep_last
        for old_file in auto_saves[keep_last:]:
            try:
                old_file.unlink()
            except OSError:
                pass
        
        return filepath
    
    def update_last_code_block(self, message: str) -> None:
        """
        Extract and store last code block from message.
        
        Args:
            message: Message potentially containing code blocks
        """
        # Find all code blocks
        pattern = r'```(?:\w+)?\n(.*?)```'
        matches = re.findall(pattern, message, re.DOTALL)
        
        if matches:
            self.last_code_block = matches[-1].strip()
    
    def get_last_code_block(self) -> Optional[str]:
        """
        Get the last extracted code block.
        
        Returns:
            str: Last code block or None
        """
        return self.last_code_block
    
    def delete_session(self, name: str) -> bool:
        """
        Delete session by name.
        
        Args:
            name: Session name
        
        Returns:
            bool: True if deleted, False if not found
        """
        deleted = False
        for filepath in self.sessions_dir.glob("*.json"):
            if name.lower() in filepath.stem.lower():
                try:
                    filepath.unlink()
                    deleted = True
                except OSError:
                    pass
        
        return deleted
    
    def get_session_count(self) -> int:
        """
        Get total number of saved sessions.
        
        Returns:
            int: Number of sessions
        """
        return len(list(self.sessions_dir.glob("*.json")))
