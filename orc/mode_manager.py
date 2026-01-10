"""
Mode Manager for ORC - Handles auto-switching between chat and work modes
"""

from typing import List, Dict, Any, Optional


class ModeManager:
    """
    Manages ORC's operational modes:
    - auto: Automatically switches between chat and work based on context
    - chat: No tools, just conversation (faster, cheaper)
    - work: Full tool access for codebase analysis
    """
    
    def __init__(self):
        self.mode = "auto"
        self.current_effective_mode = "work"
        self.messages_since_tool_use = 0
        self.conversation_context = []
        
    def should_use_tools(self, user_message: str, tools_used_recently: List[str]) -> bool:
        """
        Determine if tools should be available based on mode and context
        
        Returns:
            bool: True if tools should be enabled
        """
        if self.mode == "work":
            return True
        
        if self.mode == "chat":
            return False
        
        # Auto mode - intelligent detection
        return self._auto_detect_needs_tools(user_message, tools_used_recently)
    
    def _auto_detect_needs_tools(self, user_message: str, tools_used_recently: List[str]) -> bool:
        """
        Auto-detect if user's question needs codebase tools
        
        Tool indicators:
        - Questions about specific code/files
        - Requests for analysis (complexity, dead code, etc.)
        - Searching or finding things
        - "Show me", "Find", "Analyze", etc.
        
        Chat indicators:
        - General questions after context is established
        - Follow-up questions about previous answers
        - Conceptual or how-to questions
        - No specific code references
        """
        message_lower = user_message.lower()
        
        # Strong tool indicators
        tool_keywords = [
            "analyze", "find", "search", "show me", "what's in",
            "list", "get", "check", "scan", "look for",
            "functions", "classes", "files", "modules",
            "complexity", "dead code", "dependencies",
            "file:", "function:", "class:", ".py", ".js",
            "codebase", "project", "repository"
        ]
        
        # Strong chat indicators
        chat_keywords = [
            "what is", "how do", "can you explain", "tell me about",
            "why", "what does", "help me understand",
            "thanks", "thank you", "ok", "okay", "got it",
            "what do you think", "should i", "is it"
        ]
        
        # Check for tool indicators
        for keyword in tool_keywords:
            if keyword in message_lower:
                return True
        
        # Check for chat indicators
        for keyword in chat_keywords:
            if keyword in message_lower:
                # If no tools used recently, probably just chatting
                if not tools_used_recently or self.messages_since_tool_use > 3:
                    return False
        
        # Default based on recent activity
        if tools_used_recently and self.messages_since_tool_use < 3:
            # Recently used tools, probably still working
            return True
        elif self.messages_since_tool_use > 5:
            # Long time without tools, probably just chatting
            return False
        
        # Default to work mode for ambiguous cases
        return True
    
    def get_mode_suggestion(self, user_message: str, tools_used_recently: List[str]) -> Optional[str]:
        """
        Get a suggestion for mode switch if auto-mode detects a change
        
        Returns:
            Optional[str]: "chat" or "work" if mode should change, None otherwise
        """
        if self.mode != "auto":
            return None
        
        needs_tools = self._auto_detect_needs_tools(user_message, tools_used_recently)
        suggested_mode = "work" if needs_tools else "chat"
        
        if suggested_mode != self.current_effective_mode:
            return suggested_mode
        
        return None
    
    def set_mode(self, mode: str):
        """Set the operational mode"""
        if mode not in ["auto", "chat", "work"]:
            raise ValueError(f"Invalid mode: {mode}. Must be auto, chat, or work")
        self.mode = mode
        
        # Update effective mode based on new setting
        if mode == "chat":
            self.current_effective_mode = "chat"
        elif mode == "work":
            self.current_effective_mode = "work"
        # auto mode keeps current effective mode until context changes
    
    def update_effective_mode(self, new_mode: str):
        """Update the current effective mode (what's actually being used)"""
        self.current_effective_mode = new_mode
    
    def increment_message_count(self):
        """Track messages since last tool use"""
        self.messages_since_tool_use += 1
    
    def reset_message_count(self):
        """Reset counter when tools are used"""
        self.messages_since_tool_use = 0
    
    def get_mode_description(self) -> Dict[str, Any]:
        """Get current mode status"""
        return {
            "mode": self.mode,
            "effective_mode": self.current_effective_mode,
            "messages_since_tools": self.messages_since_tool_use,
            "description": self._get_mode_description_text()
        }
    
    def _get_mode_description_text(self) -> str:
        """Get human-readable description of current mode"""
        if self.mode == "auto":
            return f"Auto (currently using {self.current_effective_mode} mode)"
        elif self.mode == "chat":
            return "Chat only (no tools, faster responses)"
        elif self.mode == "work":
            return "Work mode (full tool access)"
        return "Unknown"
