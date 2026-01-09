"""
CLI Authentication and Web Integration - Updated
"""
import json
import httpx
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
import webbrowser

console = Console()

# Configuration
CONFIG_DIR = Path.home() / '.orc'
CONFIG_FILE = CONFIG_DIR / 'config.json'
DEFAULT_WEB_URL = 'http://127.0.0.1:5000'


def get_config():
    """Load CLI configuration"""
    if not CONFIG_FILE.exists():
        return {}
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}


def save_config(config):
    """Save CLI configuration"""
    CONFIG_DIR.mkdir(exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)


def is_authenticated():
    """Check if user is authenticated"""
    config = get_config()
    return 'web_token' in config and config.get('web_token')


def get_web_url():
    """Get web URL from config"""
    import os
    config = get_config()
    return config.get('web_url', os.getenv('ORC_WEB_URL', DEFAULT_WEB_URL))


def get_token():
    """Get authentication token"""
    config = get_config()
    return config.get('web_token')


def require_auth():
    """Require authentication - show prompt and exit if not authenticated"""
    if not is_authenticated():
        console.print()
        console.print(Panel.fit(
            "[bold yellow]Authentication Required[/bold yellow]\n\n"
            "ORC requires a free account to use AI features.\n\n"
            "[cyan]To get started:[/cyan]\n"
            "  1. Run: [bold]orc login[/bold]\n"
            "  2. Browser will open to create account\n"
            "  3. Generate CLI token\n"
            "  4. Paste token when prompted\n\n"
            "[dim]Basic commands like 'orc index' work without login[/dim]",
            title="[bold red]Not Authenticated[/bold red]",
            border_style="red"
        ))
        console.print()
        raise SystemExit(1)


def login_flow(token=None, web_url=None):
    """Interactive login flow with browser opening"""
    console.print()
    console.print(Panel.fit(
        "[bold cyan]ORC CLI - Authentication[/bold cyan]\n\n"
        "Connecting to ORC web interface...",
        border_style="cyan"
    ))
    console.print()
    
    # Get web URL
    if not web_url:
        web_url = Prompt.ask("[cyan]Web URL[/cyan]", default=DEFAULT_WEB_URL)
    
    # Get token
    if not token:
        console.print()
        console.print("[yellow]Opening browser to get your token...[/yellow]")
        console.print()
        
        # Open browser to account settings
        try:
            webbrowser.open(f"{web_url}/auth/signin")
            console.print(f"[cyan]→[/cyan] Browser opened to: {web_url}")
            console.print()
            console.print("[yellow]Steps:[/yellow]")
            console.print("  1. Sign in (or create account)")
            console.print("  2. Go to Account page")
            console.print("  3. Click 'Generate Token'")
            console.print("  4. Copy the token")
            console.print()
        except:
            console.print(f"[yellow]Please visit:[/yellow] {web_url}/settings/account")
            console.print()
        
        token = Prompt.ask("[cyan]Enter your CLI token[/cyan]", password=True)
    
    # Test token with spinner
    console.print()
    with console.status("[cyan]Authenticating...[/cyan]", spinner="dots"):
        try:
            response = httpx.get(
                f'{web_url}/api/configs',
                headers={'X-CLI-Token': token},
                timeout=10.0
            )
        except httpx.ConnectError:
            console.print()
            console.print(f"[red]Cannot connect to {web_url}[/red]")
            console.print("[yellow]Make sure the web server is running:[/yellow]")
            console.print("  python orc/web/app_new.py")
            console.print()
            return False
        except Exception as e:
            console.print()
            console.print(f"[red]Error: {str(e)}[/red]")
            console.print()
            return False
    
    if response.status_code == 200:
        data = response.json()
        user = data.get('user', {})
        configs = data.get('configs', [])
        
        # Save configuration
        save_config({'web_url': web_url, 'web_token': token})
        
        console.print()
        console.print(Panel.fit(
            f"[bold green]Successfully authenticated![/bold green]\n\n"
            f"User: [cyan]{user.get('username')}[/cyan]\n"
            f"Email: [cyan]{user.get('email')}[/cyan]\n"
            f"API Configs: [cyan]{len(configs)}[/cyan]",
            title="[bold green]Connected[/bold green]",
            border_style="green"
        ))
        console.print()
        return True
    else:
        console.print()
        console.print("[red]Invalid token. Please check and try again.[/red]")
        console.print()
        return False


def logout():
    """Logout (remove token)"""
    if CONFIG_FILE.exists():
        CONFIG_FILE.unlink()
    console.print()
    console.print("[green]Signed out successfully[/green]")
    console.print()


def get_api_config(provider=None):
    """Get API configuration from web"""
    if not is_authenticated():
        return None
    
    token = get_token()
    web_url = get_web_url()
    
    try:
        if provider:
            url = f'{web_url}/api/config/{provider}'
        else:
            url = f'{web_url}/api/default-config'
        
        response = httpx.get(url, headers={'X-CLI-Token': token}, timeout=5.0)
        
        if response.status_code == 200:
            return response.json()
    except:
        pass
    
    return None
