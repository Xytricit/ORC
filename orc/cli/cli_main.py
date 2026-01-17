"""
ORC CLI Main Module

All CLI commands using Click framework.

Author: ORC Team
Date: 2026-01-14
"""

import sys
from pathlib import Path
from typing import Optional

import click
import yaml

# Import components from orc package
from orc.cli.cli_style import CLIOutput
from orc.session.session_manager import SessionManager
from orc.session.token_tracker import TokenTracker

# Import banner for aesthetic display
try:
    from orc.cli.banner import get_orc_banner
    from rich.console import Console
    BANNER_AVAILABLE = True
except ImportError:
    BANNER_AVAILABLE = False

# Import interactive chat
try:
    from orc.cli.cli_loop import ORCChatSession
    CHAT_AVAILABLE = True
except ImportError:
    CHAT_AVAILABLE = False

# Import core components
try:
    from orc.core.parallel_indexer import ParallelIndexer
    from orc.core.index_service import IndexService
    from orc.core.config import ORCConfig
    INDEXER_AVAILABLE = True
except ImportError:
    INDEXER_AVAILABLE = False

try:
    from orc.storage.graph_db import GraphDB
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False

try:
    from orc.analysis.all_analyzers import Analyzer
    ANALYZER_AVAILABLE = True
except ImportError:
    ANALYZER_AVAILABLE = False


class ORCCLIContext:
    """Context object for CLI commands."""
    
    def __init__(self):
        self.output = CLIOutput()
        self.root_path = Path.cwd()
        self.config = None
        self.db = None


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """ORC - AI-powered codebase intelligence platform."""
    # Create context
    ctx.obj = ORCCLIContext()
    
    # If no command provided, launch interactive chat
    if ctx.invoked_subcommand is None:
        if CHAT_AVAILABLE:
            # Launch interactive AI chat with banner
            chat = ORCChatSession()
            chat.run()
        else:
            # Fallback to help if chat not available
            if BANNER_AVAILABLE:
                console = Console()
                console.print(get_orc_banner())
                console.print()
            click.echo(ctx.get_help())


@cli.command()
@click.pass_context
def init(ctx):
    """Initialize ORC in current directory."""
    output = ctx.obj.output
    root_path = ctx.obj.root_path
    
    output.start_phase("Initializing ORC")
    
    try:
        # Create .orc directory
        orc_dir = root_path / ".orc"
        orc_dir.mkdir(exist_ok=True)
        output.success(f"Created directory: {orc_dir}")
        
        # Create subdirectories
        cache_dir = orc_dir / "cache"
        cache_dir.mkdir(exist_ok=True)
        
        sessions_dir = orc_dir / "sessions"
        sessions_dir.mkdir(exist_ok=True)
        
        output.success(f"Created cache and sessions directories")
        
        # Create default config file
        config_path = root_path / "orc_config.yaml"
        if not config_path.exists():
            default_config = {
                'project_root': '.',
                'db_path': '.orc/graph.db',
                'cache_dir': '.orc/cache',
                'sessions_dir': '.orc/sessions',
                'ai': {
                    'provider': 'groq',
                    'model': None,
                    'api_key': None
                },
                'analysis': {
                    'max_complexity_threshold': 10,
                    'max_coupling_threshold': 0.7,
                    'dead_code_confidence': 0.8
                },
                'parallel': {
                    'workers': None,
                    'cache_ttl': 3600
                },
                'ignored_patterns': [
                    '__pycache__',
                    '.git',
                    'node_modules',
                    'dist',
                    'build',
                    '*.pyc'
                ]
            }
            
            with open(config_path, 'w') as f:
                yaml.dump(default_config, f, default_flow_style=False, sort_keys=False)
            
            output.success(f"Created {config_path}")
        else:
            output.info(f"Config file already exists: {config_path}")
        
        # Create .orcignore template
        orcignore_path = root_path / ".orcignore"
        if not orcignore_path.exists():
            ignore_patterns = [
                "# ORC Ignore Patterns",
                "# Similar to .gitignore syntax",
                "",
                "__pycache__/",
                "*.pyc",
                "*.pyo",
                "*.pyd",
                ".git/",
                ".gitignore",
                "node_modules/",
                "dist/",
                "build/",
                "*.egg-info/",
                ".env",
                ".venv/",
                "venv/",
                ".idea/",
                ".vscode/",
                "*.swp",
                "*.swo",
                "*~",
                ".DS_Store"
            ]
            
            with open(orcignore_path, 'w') as f:
                f.write('\n'.join(ignore_patterns))
            
            output.success(f"Created {orcignore_path}")
        else:
            output.info(f"Ignore file already exists: {orcignore_path}")
        
        output.success("ORC initialized successfully!")
        
    except Exception as e:
        output.error(f"Initialization failed: {e}")
        sys.exit(1)


@cli.command()
@click.option('--force', is_flag=True, help='Force re-indexing')
@click.option('--quiet', is_flag=True, help='Minimal output')
@click.pass_context
def index(ctx, force, quiet):
    """Index project files and populate database."""
    output = ctx.obj.output
    root_path = ctx.obj.root_path
    
    if not INDEXER_AVAILABLE:
        output.error("Indexer component not available")
        sys.exit(1)
    
    if not DB_AVAILABLE:
        output.error("Database component not available")
        sys.exit(1)
    
    if not quiet:
        output.start_phase("Indexing Project")
    
    try:
        # Step 1: Scan files with ParallelIndexer
        indexer = ParallelIndexer(root_path=root_path)
        
        # Scan files first (don't parse yet)
        files_to_parse = indexer._scan_files()
        if not quiet:
            output.success(f"Scanned: {len(files_to_parse)} files")
        
        # Step 2: Initialize database
        db_path = root_path / '.orc' / 'graph.db'
        db_path.parent.mkdir(parents=True, exist_ok=True)
        db = GraphDB(str(db_path))
        
        if not quiet:
            output.success(f"Database: {db_path}")
        
        # Step 3: Import parsers and AI backend
        from orc.parsers import get_parser
        
        # Try to load AI backend (optional)
        ai_backend = None
        try:
            from orc.ai.ai_backend import AIBackend
            ai_backend = AIBackend(db)
            if not quiet:
                output.info("AI Backend loaded (will enhance results)")
        except Exception:
            if not quiet:
                output.info("AI Backend not available (indexing only)")
        
        # Step 4: Parse and store each file
        total_functions = 0
        total_classes = 0
        total_api_endpoints = 0
        total_security_risks = 0
        
        for file_path in files_to_parse:
            # Get appropriate parser
            parser = get_parser(file_path)
            if not parser:
                continue
            
            try:
                # Parse file
                parse_result = parser.parse_file(file_path)
                
                # Enhance with AI Backend (if available)
                if ai_backend:
                    try:
                        parse_result = ai_backend.enhance_parser_output(parse_result, file_path)
                    except Exception as e:
                        # Continue without AI enhancement
                        pass
                
                # Store file metadata
                file_str = str(file_path)
                language = file_path.suffix.lstrip('.')
                loc = parse_result.get('files', {}).get(file_str, {}).get('loc', 0)
                db.store_file(file_str, language, loc)
                
                # Store functions
                if parse_result.get('functions'):
                    for func_id, func_data in parse_result['functions'].items():
                        db.store_function(
                            func_id, 
                            func_data['name'], 
                            file_str,
                            func_data['line_start'], 
                            func_data['line_end'],
                            func_data.get('complexity', 0), 
                            func_data.get('code', ''),
                            ','.join(func_data.get('parameters', [])),
                            ','.join(func_data.get('calls', [])),
                            func_data.get('is_exported', False)
                        )
                        total_functions += 1
                
                # Store classes
                if parse_result.get('classes'):
                    for class_id, class_data in parse_result['classes'].items():
                        db.store_class(
                            class_id,
                            class_data['name'],
                            file_str,
                            class_data['line_start'],
                            class_data['line_end'],
                            ','.join(class_data.get('methods', [])),
                            ','.join(class_data.get('base_classes', []))
                        )
                        total_classes += 1
                
                # Store semantic data (Phase 4 tables)
                if parse_result.get('api_endpoints'):
                    db.store_api_endpoints(parse_result['api_endpoints'], file_str)
                    total_api_endpoints += len(parse_result['api_endpoints'])
                
                if parse_result.get('database_queries'):
                    db.store_database_queries(parse_result['database_queries'], file_str)
                
                if parse_result.get('error_handling'):
                    db.store_error_handlers(parse_result['error_handling'], file_str)
                
                if parse_result.get('configuration'):
                    db.store_config_usage(parse_result['configuration'], file_str)
                
                if parse_result.get('side_effects'):
                    db.store_side_effects(parse_result['side_effects'], file_str)
                
                if parse_result.get('cross_cutting'):
                    db.store_cross_cutting_concerns(parse_result['cross_cutting'], file_str)
                
                if parse_result.get('security'):
                    db.store_security_risks(parse_result['security'], file_str)
                    total_security_risks += len(parse_result['security'].get('sql_injection_risks', [])) + \
                                           len(parse_result['security'].get('secrets', []))
                
                if parse_result.get('data_models'):
                    db.store_data_models(parse_result['data_models'], file_str)
                
                if parse_result.get('concurrency'):
                    db.store_concurrency_patterns(parse_result['concurrency'], file_str)
                
            except Exception as e:
                if not quiet:
                    output.warning(f"Failed to parse {file_path}: {e}")
                continue
        
        # Step 5: Generate TOC
        if not quiet:
            output.info("Generating TOC...")
        
        try:
            from orc.core.toc_generator import TOCGenerator
            
            toc_gen = TOCGenerator(db)
            toc = toc_gen.generate_toc()
            
            toc_path = root_path / '.orc' / 'toc.json'
            toc_gen.save_toc(toc_path)
            
            if not quiet:
                output.success(f"TOC: {toc_path}")
        except Exception as e:
            if not quiet:
                output.warning(f"TOC generation failed: {e}")
        
        # Step 6: Show results
        if not quiet:
            output.success(f"Indexed: {len(files_to_parse)} files")
            output.success(f"Functions: {total_functions}")
            output.success(f"Classes: {total_classes}")
            if total_api_endpoints > 0:
                output.success(f"API Endpoints: {total_api_endpoints}")
            if total_security_risks > 0:
                output.warning(f"Security Risks: {total_security_risks}")
        
        return {
            'files': len(files_to_parse),
            'functions': total_functions,
            'classes': total_classes,
            'api_endpoints': total_api_endpoints,
            'security_risks': total_security_risks
        }
        
    except Exception as e:
        output.error(f"Indexing failed: {e}")
        import traceback
        if not quiet:
            traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.pass_context
def scan(ctx):
    """Quick health scan and analysis."""
    output = ctx.obj.output
    root_path = ctx.obj.root_path
    
    output.start_phase("Running Quick Scan")
    
    try:
        # Step 1: Index
        if INDEXER_AVAILABLE:
            indexer = ParallelIndexer(root_path=root_path)
            index_result = indexer.index()
            
            output.success(f"Files: {index_result.get('files_indexed', 0)}")
            output.success(f"Functions: {index_result.get('functions', 0)}")
            output.success(f"Classes: {index_result.get('classes', 0)}")
        else:
            output.warning("Indexer not available")
        
        # Step 2: Analyze
        if ANALYZER_AVAILABLE and DB_AVAILABLE:
            db = GraphDB(".orc/graph.db")
            analyzer = Analyzer()
            
            # Get some basic stats
            functions = db.query_functions()
            complex_funcs = [f for f in functions if f.get('complexity', 0) > 10]
            
            if complex_funcs:
                output.warning(f"Complex functions: {len(complex_funcs)}")
            else:
                output.success("No overly complex functions detected")
        else:
            output.info("Analysis components not available")
        
        output.success("Scan complete!")
        
    except Exception as e:
        output.error(f"Scan failed: {e}")
        sys.exit(1)


@cli.command()
@click.option('--output', '-o', help='Output file path')
@click.pass_context
def report(ctx, output):
    """Generate comprehensive analysis report."""
    cli_output = ctx.obj.output
    root_path = ctx.obj.root_path
    
    cli_output.start_phase("Generating Report")
    
    try:
        if not DB_AVAILABLE:
            cli_output.error("Database component not available")
            sys.exit(1)
        
        db = GraphDB(".orc/graph.db")
        
        # Build report
        report_lines = [
            "# ORC Analysis Report",
            "",
            f"**Generated:** {Path.cwd()}",
            "",
            "## Summary",
            ""
        ]
        
        # Get statistics
        files = db.get_all_files()
        functions = db.query_functions()
        classes = db.get_all_classes()
        
        report_lines.extend([
            f"- **Files:** {len(files)}",
            f"- **Functions:** {len(functions)}",
            f"- **Classes:** {len(classes)}",
            "",
            "## Complexity Analysis",
            ""
        ])
        
        # Complex functions
        complex_funcs = sorted(
            [f for f in functions if f.get('complexity', 0) > 10],
            key=lambda x: x.get('complexity', 0),
            reverse=True
        )
        
        if complex_funcs:
            report_lines.append("### High Complexity Functions")
            report_lines.append("")
            for func in complex_funcs[:10]:
                report_lines.append(
                    f"- `{func['name']}` in {func['file']} "
                    f"(complexity: {func.get('complexity', 0)})"
                )
        else:
            report_lines.append("No high complexity functions detected.")
        
        report_lines.append("")
        report_lines.append("---")
        report_lines.append("*Generated by ORC*")
        
        report_text = '\n'.join(report_lines)
        
        # Output
        if output:
            output_path = Path(output)
            output_path.write_text(report_text)
            cli_output.success(f"Report saved to: {output_path}")
        else:
            print(report_text)
        
    except Exception as e:
        cli_output.error(f"Report generation failed: {e}")
        sys.exit(1)


@cli.command()
@click.argument('what')
@click.pass_context
def find(ctx, what):
    """Find entities (dead code, complex functions, etc.)."""
    output = ctx.obj.output
    
    output.start_phase(f"Searching for: {what}")
    
    try:
        if not DB_AVAILABLE:
            output.error("Database component not available")
            sys.exit(1)
        
        db = GraphDB(".orc/graph.db")
        
        if what == 'dead':
            output.info("Searching for dead code...")
            # Placeholder - would use analyzer
            output.warning("Dead code analysis requires full analyzer")
        
        elif what == 'complex':
            output.info("Searching for complex functions...")
            functions = db.query_functions()
            complex_funcs = [f for f in functions if f.get('complexity', 0) > 10]
            
            if complex_funcs:
                for func in complex_funcs[:20]:
                    output.info(
                        f"{func['name']} - {func['file']}:{func.get('line', '?')} "
                        f"(complexity: {func.get('complexity', 0)})"
                    )
            else:
                output.success("No complex functions found")
        
        elif what == 'large':
            output.info("Searching for large functions (>200 LOC)...")
            functions = db.query_functions()
            large_funcs = [f for f in functions if f.get('lines', 0) > 200]
            
            if large_funcs:
                for func in large_funcs[:20]:
                    output.info(
                        f"{func['name']} - {func['file']} "
                        f"({func.get('lines', 0)} lines)"
                    )
            else:
                output.success("No large functions found")
        
        else:
            # Pattern search
            output.info(f"Searching for pattern: {what}")
            functions = db.query_functions(name_pattern=what)
            
            if functions:
                for func in functions[:20]:
                    output.info(f"{func['name']} - {func['file']}")
            else:
                output.warning("No matches found")
        
    except Exception as e:
        output.error(f"Search failed: {e}")
        sys.exit(1)


@cli.command()
@click.pass_context
def check(ctx):
    """Health check (config, database, parsers)."""
    output = ctx.obj.output
    root_path = ctx.obj.root_path
    
    output.start_phase("Running Health Check")
    
    issues = []
    
    # Check config
    config_path = root_path / "orc_config.yaml"
    if config_path.exists():
        output.success("Config file exists")
    else:
        output.warning("Config file not found (run 'orc init')")
        issues.append("config")
    
    # Check database
    db_path = root_path / ".orc" / "graph.db"
    if db_path.exists():
        output.success("Database exists")
    else:
        output.warning("Database not found (run 'orc index')")
        issues.append("database")
    
    # Check components
    if INDEXER_AVAILABLE:
        output.success("Indexer component available")
    else:
        output.warning("Indexer component not available")
        issues.append("indexer")
    
    if DB_AVAILABLE:
        output.success("Database component available")
    else:
        output.warning("Database component not available")
        issues.append("database_module")
    
    if ANALYZER_AVAILABLE:
        output.success("Analyzer component available")
    else:
        output.warning("Analyzer component not available")
        issues.append("analyzer")
    
    # Summary
    if not issues:
        output.success("All checks passed!")
    else:
        output.warning(f"Issues found: {', '.join(issues)}")


@cli.command()
@click.argument('pattern')
@click.pass_context
def ignore(ctx, pattern):
    """Add pattern to .orcignore."""
    output = ctx.obj.output
    root_path = ctx.obj.root_path
    
    orcignore_path = root_path / ".orcignore"
    
    try:
        # Read existing patterns
        if orcignore_path.exists():
            patterns = orcignore_path.read_text().splitlines()
        else:
            patterns = ["# ORC Ignore Patterns"]
        
        # Add new pattern
        if pattern not in patterns:
            patterns.append(pattern)
            orcignore_path.write_text('\n'.join(patterns) + '\n')
            output.success(f"Added '{pattern}' to .orcignore")
        else:
            output.info(f"Pattern '{pattern}' already in .orcignore")
    
    except Exception as e:
        output.error(f"Failed to update .orcignore: {e}")
        sys.exit(1)


@cli.command()
@click.argument('action', required=False, default='list')
@click.option('--key', help='Configuration key')
@click.option('--value', help='Configuration value')
@click.pass_context
def config(ctx, action, key, value):
    """Manage configuration (list, set, reset)."""
    output = ctx.obj.output
    root_path = ctx.obj.root_path
    
    config_path = root_path / "orc_config.yaml"
    
    try:
        if action == 'list':
            if config_path.exists():
                config_data = yaml.safe_load(config_path.read_text())
                output.start_phase("Current Configuration")
                print(yaml.dump(config_data, default_flow_style=False))
            else:
                output.warning("No config file found (run 'orc init')")
        
        elif action == 'set':
            if not key or not value:
                output.error("Both --key and --value required for 'set'")
                sys.exit(1)
            
            config_data = yaml.safe_load(config_path.read_text())
            # Simple key-value setting (would need nested key support)
            config_data[key] = value
            
            with open(config_path, 'w') as f:
                yaml.dump(config_data, f, default_flow_style=False)
            
            output.success(f"Set {key} = {value}")
        
        elif action == 'reset':
            if config_path.exists():
                config_path.unlink()
            output.info("Configuration reset (run 'orc init' to recreate)")
        
        else:
            output.error(f"Unknown action: {action}")
            sys.exit(1)
    
    except Exception as e:
        output.error(f"Config operation failed: {e}")
        sys.exit(1)


def main():
    """Entry point for CLI."""
    cli()


if __name__ == '__main__':
    main()
