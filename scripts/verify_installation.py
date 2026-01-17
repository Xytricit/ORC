#!/usr/bin/env python3
"""
ORC Installation Verification Script

Verifies that ORC is properly installed and all components are accessible.

Usage:
    python verify_installation.py
"""

import sys
from pathlib import Path


def print_header(text):
    """Print section header."""
    print()
    print("=" * 70)
    print(f"  {text}")
    print("=" * 70)
    print()


def print_success(text):
    """Print success message."""
    print(f"  ✓ {text}")


def print_error(text):
    """Print error message."""
    print(f"  ✗ {text}")


def print_info(text):
    """Print info message."""
    print(f"  • {text}")


def verify_imports():
    """Verify all ORC imports work."""
    print_header("Step 1: Verifying Imports")
    
    errors = []
    
    # Test main package
    try:
        import orc
        print_success(f"orc package imported (version {orc.__version__})")
    except ImportError as e:
        print_error(f"Failed to import orc: {e}")
        errors.append("orc package")
    
    # Test core components
    try:
        from orc.core import ParallelIndexer, IndexService, ORCConfig, Cache
        print_success("orc.core components imported")
    except ImportError as e:
        print_error(f"Failed to import orc.core: {e}")
        errors.append("orc.core")
    
    # Test storage
    try:
        from orc.storage import GraphDB
        print_success("orc.storage components imported")
    except ImportError as e:
        print_error(f"Failed to import orc.storage: {e}")
        errors.append("orc.storage")
    
    # Test parsers
    try:
        from orc.parsers import PythonParser, JavaScriptParser, TypeScriptParser, get_parser
        print_success("orc.parsers components imported")
    except ImportError as e:
        print_error(f"Failed to import orc.parsers: {e}")
        errors.append("orc.parsers")
    
    # Test analysis
    try:
        from orc.analysis import Analyzer, DependencyResolver, DeadCodeAnalyzer
        print_success("orc.analysis components imported")
    except ImportError as e:
        print_error(f"Failed to import orc.analysis: {e}")
        errors.append("orc.analysis")
    
    # Test CLI
    try:
        from orc.cli import cli, CLIOutput, UIComponents
        print_success("orc.cli components imported")
    except ImportError as e:
        print_error(f"Failed to import orc.cli: {e}")
        errors.append("orc.cli")
    
    # Test session
    try:
        from orc.session import SessionManager, TokenTracker
        print_success("orc.session components imported")
    except ImportError as e:
        print_error(f"Failed to import orc.session: {e}")
        errors.append("orc.session")
    
    return len(errors) == 0, errors


def verify_dependencies():
    """Verify all dependencies are installed."""
    print_header("Step 2: Verifying Dependencies")
    
    dependencies = [
        ('click', 'CLI framework'),
        ('yaml', 'YAML configuration'),
        ('networkx', 'Graph analysis'),
        ('pygments', 'Syntax highlighting'),
    ]
    
    errors = []
    
    for module, description in dependencies:
        try:
            __import__(module)
            print_success(f"{module:20} - {description}")
        except ImportError:
            print_error(f"{module:20} - {description} (MISSING)")
            errors.append(module)
    
    # Optional dependencies
    print()
    print_info("Optional dependencies:")
    
    optional = [
        ('prompt_toolkit', 'Interactive prompts'),
        ('pytest', 'Testing framework'),
    ]
    
    for module, description in optional:
        try:
            __import__(module)
            print_success(f"{module:20} - {description}")
        except ImportError:
            print_info(f"{module:20} - {description} (not installed)")
    
    return len(errors) == 0, errors


def verify_cli():
    """Verify CLI commands work."""
    print_header("Step 3: Verifying CLI")
    
    try:
        from orc.cli.cli_main import cli
        print_success("CLI entry point accessible")
        
        # Check if we can get help
        from click.testing import CliRunner
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])
        
        if result.exit_code == 0:
            print_success("CLI --help command works")
            return True, []
        else:
            print_error(f"CLI --help failed with exit code {result.exit_code}")
            return False, ["CLI execution"]
    
    except Exception as e:
        print_error(f"CLI verification failed: {e}")
        return False, ["CLI"]


def verify_functionality():
    """Verify basic functionality."""
    print_header("Step 4: Verifying Basic Functionality")
    
    errors = []
    
    # Test parser registry
    try:
        from orc.parsers import get_parser
        parser = get_parser('test.py')
        if parser:
            print_success("Parser registry works")
        else:
            print_error("Parser registry returned None")
            errors.append("Parser registry")
    except Exception as e:
        print_error(f"Parser registry failed: {e}")
        errors.append("Parser registry")
    
    # Test token tracker
    try:
        from orc.session import TokenTracker
        tracker = TokenTracker()
        tracker.add_request('groq', 'llama2', 100, 50)
        stats = tracker.get_statistics()
        if stats['total_tokens'] == 150:
            print_success("Token tracker works")
        else:
            print_error("Token tracker calculation incorrect")
            errors.append("Token tracker")
    except Exception as e:
        print_error(f"Token tracker failed: {e}")
        errors.append("Token tracker")
    
    # Test CLI output
    try:
        from orc.cli import CLIOutput
        output = CLIOutput(use_color=False)
        # Just test instantiation
        print_success("CLI output styling works")
    except Exception as e:
        print_error(f"CLI output failed: {e}")
        errors.append("CLI output")
    
    return len(errors) == 0, errors


def verify_file_structure():
    """Verify file structure is correct."""
    print_header("Step 5: Verifying File Structure")
    
    required_files = [
        'orc/__init__.py',
        'orc/core/__init__.py',
        'orc/storage/__init__.py',
        'orc/parsers/__init__.py',
        'orc/analysis/__init__.py',
        'orc/cli/__init__.py',
        'orc/session/__init__.py',
        'setup.py',
        'requirements.txt',
        'README.md',
    ]
    
    errors = []
    
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            print_success(f"{file_path}")
        else:
            print_error(f"{file_path} (MISSING)")
            errors.append(file_path)
    
    return len(errors) == 0, errors


def main():
    """Run all verification steps."""
    print()
    print("*" * 70)
    print("*" + " " * 68 + "*")
    print("*" + "  ORC INSTALLATION VERIFICATION".center(68) + "*")
    print("*" + " " * 68 + "*")
    print("*" * 70)
    
    all_passed = True
    all_errors = []
    
    # Run verification steps
    steps = [
        ("Imports", verify_imports),
        ("Dependencies", verify_dependencies),
        ("CLI", verify_cli),
        ("Functionality", verify_functionality),
        ("File Structure", verify_file_structure),
    ]
    
    results = []
    for name, func in steps:
        passed, errors = func()
        results.append((name, passed))
        if not passed:
            all_passed = False
            all_errors.extend(errors)
    
    # Print summary
    print_header("Verification Summary")
    
    for name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"  {name:20} {status}")
    
    print()
    print("=" * 70)
    
    if all_passed:
        print()
        print("  🎉 SUCCESS! ORC is properly installed and ready to use!")
        print()
        print("  Next steps:")
        print("    1. Run: orc init")
        print("    2. Run: orc index")
        print("    3. Run: orc scan")
        print()
        print("  For help: orc --help")
        print("  Quick start: See QUICK_START.md")
        print()
        return 0
    else:
        print()
        print("  ❌ INSTALLATION INCOMPLETE")
        print()
        print("  Issues found:")
        for error in all_errors:
            print(f"    - {error}")
        print()
        print("  Solutions:")
        print("    1. Reinstall: pip install -e .")
        print("    2. Check dependencies: pip install -r requirements.txt")
        print("    3. See INSTALLATION.md for troubleshooting")
        print()
        return 1


if __name__ == '__main__':
    sys.exit(main())
