"""
ORC SubAgents System - Create specialized AI agents for your dev team
Each agent has custom training, tools, and personality
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
from rich.console import Console

console = Console()


class SubAgent:
    """
    Represents a specialized ORC subagent with custom training and tools.
    Each agent has its own orc_<name>.md file for persistent memory.
    """
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        self.name = name
        self.config = config or {}
        self.memory_file = Path(f"orc_{name}.md")
        self.config_file = Path(f".orc/agents/{name}.json")
        
        # Agent attributes
        self.role = self.config.get("role", "General Assistant")
        self.expertise = self.config.get("expertise", [])
        self.personality = self.config.get("personality", "professional")
        self.system_prompt = self.config.get("system_prompt", "")
        self.enabled_tools = self.config.get("enabled_tools", "all")
        self.temperature = self.config.get("temperature", 0.7)
        self.max_tokens = self.config.get("max_tokens", 4096)
        
    def get_system_prompt(self) -> str:
        """Generate system prompt for this agent"""
        expertise_str = ', '.join(self.expertise) if self.expertise else 'General development'
        
        base_prompt = f"""You are {self.name}, a specialized AI agent.

Role: {self.role}
Expertise: {expertise_str}
Personality: {self.personality}

Custom Instructions:
{self.system_prompt}

You have access to codebase analysis tools. Use them to provide expert assistance in your specialization.
Always stay focused on your area of expertise and provide actionable, specific recommendations.
"""
        return base_prompt
    
    def save_config(self):
        """Save agent configuration to .orc/agents/<name>.json"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        config_data = {
            "name": self.name,
            "role": self.role,
            "expertise": self.expertise,
            "personality": self.personality,
            "system_prompt": self.system_prompt,
            "enabled_tools": self.enabled_tools,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "created": datetime.now().isoformat(),
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
    
    def initialize_memory(self):
        """Create orc_<name>.md file for this agent"""
        if not self.memory_file.exists():
            content = f"""# ORC SubAgent: {self.name}

## Agent Profile

- **Role**: {self.role}
- **Expertise**: {', '.join(self.expertise) if self.expertise else 'General'}
- **Personality**: {self.personality}
- **Created**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Custom Training

{self.system_prompt or 'No custom training provided.'}

## Agent Memory (Auto-Updated)

*This section is automatically maintained to remember context.*

### Last Active
- Date: Never
- Tasks Completed: 0

### Recent Work
No work history yet.

### Knowledge Base
No knowledge stored yet.

## Notes

Add any agent-specific notes here:

- 

---
*This agent is part of your ORC dev team.*
"""
            self.memory_file.write_text(content, encoding='utf-8')
    
    @classmethod
    def load(cls, name: str) -> Optional['SubAgent']:
        """Load an existing agent from config"""
        config_file = Path(f".orc/agents/{name}.json")
        
        if not config_file.exists():
            return None
        
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            return cls(name, config)
        except Exception:
            return None
    
    def update_memory(self, activity: str, details: str = ""):
        """Update agent's memory file with recent activity"""
        if not self.memory_file.exists():
            self.initialize_memory()
        
        try:
            content = self.memory_file.read_text(encoding='utf-8')
            
            # Update Last Active
            timestamp = datetime.now().isoformat()
            content = content.replace(
                "- Date: Never",
                f"- Date: {timestamp}"
            )
            
            # Add to Recent Work
            work_entry = f"\n- [{datetime.now().strftime('%Y-%m-%d %H:%M')}] {activity}"
            if details:
                work_entry += f"\n  Details: {details}"
            
            if "No work history yet." in content:
                content = content.replace("No work history yet.", work_entry.strip())
            else:
                # Insert after "### Recent Work"
                recent_work_pos = content.find("### Recent Work")
                if recent_work_pos != -1:
                    next_section = content.find("###", recent_work_pos + 1)
                    if next_section != -1:
                        content = content[:next_section] + work_entry + "\n" + content[next_section:]
            
            self.memory_file.write_text(content, encoding='utf-8')
        except Exception:
            pass


class AgentManager:
    """Manages all subagents in the system"""
    
    def __init__(self):
        self.agents_dir = Path(".orc/agents")
        self.agents_dir.mkdir(parents=True, exist_ok=True)
        self.current_agent: Optional[SubAgent] = None
        self.agents: Dict[str, SubAgent] = {}
        self._load_all_agents()
    
    def _load_all_agents(self):
        """Load all existing agents"""
        if not self.agents_dir.exists():
            return
        
        for config_file in self.agents_dir.glob("*.json"):
            agent_name = config_file.stem
            agent = SubAgent.load(agent_name)
            if agent:
                self.agents[agent_name] = agent
    
    def create_agent(self, name: str, config: Dict[str, Any]) -> SubAgent:
        """Create a new subagent"""
        # Validate name
        if not name or not name.replace('_', '').replace('-', '').isalnum():
            raise ValueError("Agent name must be alphanumeric (underscores and hyphens allowed)")
        
        if name.lower() in ['main', 'orc', 'default']:
            raise ValueError("Reserved agent name")
        
        if name in self.agents:
            raise ValueError(f"Agent '{name}' already exists")
        
        # Create agent
        agent = SubAgent(name, config)
        agent.save_config()
        agent.initialize_memory()
        
        self.agents[name] = agent
        return agent
    
    def get_agent(self, name: str) -> Optional[SubAgent]:
        """Get an agent by name"""
        return self.agents.get(name)
    
    def list_agents(self) -> List[SubAgent]:
        """List all agents"""
        return list(self.agents.values())
    
    def switch_agent(self, name: str) -> Optional[SubAgent]:
        """Switch to a different agent"""
        agent = self.get_agent(name)
        if agent:
            self.current_agent = agent
        return agent
    
    def delete_agent(self, name: str) -> bool:
        """Delete an agent"""
        if name not in self.agents:
            return False
        
        agent = self.agents[name]
        
        # Delete config file
        if agent.config_file.exists():
            agent.config_file.unlink()
        
        # Delete memory file
        if agent.memory_file.exists():
            agent.memory_file.unlink()
        
        del self.agents[name]
        
        if self.current_agent and self.current_agent.name == name:
            self.current_agent = None
        
        return True
    
    def parse_mentions(self, message: str) -> List[str]:
        """Parse @agent mentions from a message"""
        import re
        mentions = re.findall(r'@(\w+)', message)
        return [m for m in mentions if m in self.agents]


def interactive_agent_creation(console: Console) -> Dict[str, Any]:
    """Interactive wizard to create a new agent"""
    console.print("\n[bold cyan]Create New SubAgent[/bold cyan]\n")
    
    # Get agent name
    console.print("[yellow]Agent Name:[/yellow] [dim](e.g., security_auditor, code_reviewer)[/dim]")
    name = console.input("[green]>[/green] ").strip()
    
    if not name:
        raise ValueError("Agent name is required")
    
    # Get role
    console.print("\n[yellow]Role/Title:[/yellow] [dim](e.g., Security Auditor, Performance Expert)[/dim]")
    role = console.input("[green]>[/green] ").strip() or "Specialist"
    
    # Get expertise areas
    console.print("\n[yellow]Expertise Areas:[/yellow] [dim](comma-separated, e.g., security,authentication,encryption)[/dim]")
    expertise_input = console.input("[green]>[/green] ").strip()
    expertise = [e.strip() for e in expertise_input.split(',')] if expertise_input else []
    
    # Get personality
    console.print("\n[yellow]Personality:[/yellow]")
    console.print("  1. Professional (formal, detailed)")
    console.print("  2. Friendly (casual, encouraging)")
    console.print("  3. Strict (critical, thorough)")
    console.print("  4. Teacher (explanatory, patient)")
    personality_choice = console.input("[green]Choice (1-4):[/green] ").strip()
    
    personality_map = {
        '1': 'professional',
        '2': 'friendly',
        '3': 'strict',
        '4': 'teacher'
    }
    personality = personality_map.get(personality_choice, 'professional')
    
    # Get custom training/system prompt
    console.print("\n[yellow]Custom Training Instructions:[/yellow]")
    console.print("[dim]Enter custom instructions for this agent (press Enter twice when done):[/dim]")
    
    lines = []
    while True:
        line = console.input()
        if not line and lines and not lines[-1]:
            break
        lines.append(line)
    
    system_prompt = '\n'.join(lines).strip()
    
    # Tool selection
    console.print("\n[yellow]Tool Access:[/yellow]")
    console.print("  1. All tools")
    console.print("  2. Read-only (stats, search, query)")
    console.print("  3. Custom selection")
    tool_choice = console.input("[green]Choice (1-3):[/green] ").strip()
    
    if tool_choice == '2':
        enabled_tools = ['get_codebase_stats', 'query_functions', 'query_classes', 'search_code']
    elif tool_choice == '3':
        console.print("[dim]Enter tool names (comma-separated):[/dim]")
        tool_input = console.input("[green]>[/green] ").strip()
        enabled_tools = [t.strip() for t in tool_input.split(',')] if tool_input else 'all'
    else:
        enabled_tools = 'all'
    
    # Temperature
    console.print("\n[yellow]Creativity Level (0.0-1.0):[/yellow] [dim](0.3=focused, 0.7=balanced, 1.0=creative)[/dim]")
    temp_input = console.input("[green]>[/green] ").strip()
    try:
        temperature = float(temp_input) if temp_input else 0.7
        temperature = max(0.0, min(1.0, temperature))
    except:
        temperature = 0.7
    
    return {
        "name": name,
        "role": role,
        "expertise": expertise,
        "personality": personality,
        "system_prompt": system_prompt,
        "enabled_tools": enabled_tools,
        "temperature": temperature,
        "max_tokens": 4096,
    }
