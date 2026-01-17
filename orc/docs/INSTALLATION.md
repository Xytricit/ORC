# ORC Installation Guide

Complete installation instructions for the ORC codebase intelligence platform.

---

## 📋 Prerequisites

- **Python 3.8+** (Python 3.9, 3.10, 3.11, or 3.12 recommended)
- **pip** (Python package manager)
- **git** (for cloning the repository)

### Check Your Python Version

```bash
python --version
# or
python3 --version
```

---

## 🚀 Installation Methods

### Method 1: Install from Source (Recommended for Development)

#### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/orc.git
cd orc
```

#### Step 2: Install in Development Mode

```bash
# Install with all dependencies
pip install -e .

# Or with development dependencies (includes pytest)
pip install -e .[dev]
```

**What `-e` does:** Installs in "editable" mode, so changes to source code are immediately reflected without reinstalling.

#### Step 3: Verify Installation

```bash
# Check that orc command is available
orc --help

# Check version
python -c "import orc; print(orc.__version__)"
```

Expected output:
```
Usage: orc [OPTIONS] COMMAND [ARGS]...

  ORC - AI-powered codebase intelligence platform.

Options:
  --help  Show this message and exit.

Commands:
  check   Health check (config, database, parsers).
  config  Manage configuration (list, set, reset).
  ...
```

---

### Method 2: Install from PyPI (Coming Soon)

```bash
# Once published to PyPI
pip install orc-codebase
```

---

### Method 3: Manual Installation

If you only want to install dependencies without installing ORC as a package:

```bash
cd orc
pip install -r requirements.txt
```

Then run ORC using:
```bash
python -m orc.cli.cli_main --help
```

---

## 🔧 Platform-Specific Instructions

### Windows

#### Option 1: Using PowerShell

```powershell
# Clone repository
git clone https://github.com/yourusername/orc.git
cd orc

# Install
pip install -e .

# Verify
orc --help
```

#### Option 2: Using Command Prompt

```cmd
git clone https://github.com/yourusername/orc.git
cd orc
pip install -e .
orc --help
```

**Note:** On Windows, colorama will be installed automatically for colored output support.

---

### macOS

```bash
# Clone repository
git clone https://github.com/yourusername/orc.git
cd orc

# Install
pip3 install -e .

# Verify
orc --help
```

**Note:** On macOS, you may need to use `pip3` and `python3` instead of `pip` and `python`.

---

### Linux

#### Ubuntu/Debian

```bash
# Install Python and pip if not already installed
sudo apt update
sudo apt install python3 python3-pip git

# Clone and install ORC
git clone https://github.com/yourusername/orc.git
cd orc
pip3 install -e .

# Verify
orc --help
```

#### Fedora/RHEL/CentOS

```bash
# Install Python and pip
sudo dnf install python3 python3-pip git

# Clone and install ORC
git clone https://github.com/yourusername/orc.git
cd orc
pip3 install -e .

# Verify
orc --help
```

---

## 🐍 Virtual Environment (Recommended)

Using a virtual environment keeps ORC's dependencies isolated:

### Using venv (Built-in)

```bash
# Create virtual environment
python -m venv orc-env

# Activate (Linux/Mac)
source orc-env/bin/activate

# Activate (Windows)
orc-env\Scripts\activate

# Install ORC
cd orc
pip install -e .

# Verify
orc --help

# Deactivate when done
deactivate
```

### Using conda

```bash
# Create conda environment
conda create -n orc python=3.11

# Activate environment
conda activate orc

# Install ORC
cd orc
pip install -e .

# Verify
orc --help
```

---

## 📦 Dependencies

ORC requires the following packages:

### Required Dependencies

```
click>=8.0.0         # CLI framework
pyyaml>=5.4.0        # YAML configuration
networkx>=2.6.0      # Graph analysis
pygments>=2.10.0     # Syntax highlighting
prompt-toolkit>=3.0.0 # Interactive prompts
python-dotenv>=0.19.0 # Environment variables
```

### Optional Dependencies

```
pytest>=7.0.0        # Testing framework
pytest-cov>=2.12.0   # Code coverage
```

### Install Optional Dependencies

```bash
pip install -e .[dev]
```

---

## ✅ Verification Steps

### 1. Check Installation

```bash
# Method 1: Check orc command
orc --help

# Method 2: Check Python import
python -c "import orc; print('ORC version:', orc.__version__)"

# Method 3: Check module path
python -c "import orc; print('ORC location:', orc.__file__)"
```

### 2. Initialize Test Project

```bash
# Create test directory
mkdir test-orc
cd test-orc

# Initialize ORC
orc init
```

Expected output:
```
› Initializing ORC
  ✓ Created directory: .orc
  ✓ Created cache and sessions directories
  ✓ Created orc_config.yaml
  ✓ Created .orcignore
  ✓ ORC initialized successfully!
```

### 3. Check Health

```bash
orc check
```

Expected output:
```
› Running Health Check
  ✓ Config file exists
  [WARN] Database not found (run 'orc index')
  ✓ Indexer component available
  ✓ Database component available
  ✓ Analyzer component available
```

### 4. Run Tests (if dev dependencies installed)

```bash
cd orc
pytest
```

Expected output:
```
============================= test session starts =============================
...
======================== 61 passed in 4.23s ===============================
```

---

## 🔍 Troubleshooting

### Issue: `orc: command not found`

**Cause:** The `orc` command is not in your PATH.

**Solution:**

1. Check if pip's bin directory is in PATH:
   ```bash
   python -m site --user-base
   ```

2. Add to PATH (Linux/Mac):
   ```bash
   export PATH="$HOME/.local/bin:$PATH"
   # Add to ~/.bashrc or ~/.zshrc to make permanent
   ```

3. Alternative: Run using Python module:
   ```bash
   python -m orc.cli.cli_main --help
   ```

### Issue: `ModuleNotFoundError: No module named 'orc'`

**Cause:** ORC not installed or not in Python path.

**Solution:**

1. Ensure you're in the orc directory:
   ```bash
   cd orc
   ```

2. Install in editable mode:
   ```bash
   pip install -e .
   ```

3. Check installation:
   ```bash
   pip list | grep orc
   ```

### Issue: Permission Denied on Installation

**Cause:** Installing to system Python without admin rights.

**Solution 1:** Use `--user` flag:
```bash
pip install --user -e .
```

**Solution 2:** Use virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -e .
```

### Issue: `ImportError` for specific packages

**Cause:** Missing dependencies.

**Solution:**

```bash
# Reinstall all dependencies
pip install -r requirements.txt

# Or force reinstall
pip install --force-reinstall -e .
```

### Issue: Colors not showing on Windows

**Cause:** colorama not installed.

**Solution:**

```bash
pip install colorama
```

### Issue: Tests failing

**Cause:** Test dependencies not installed or stale cache.

**Solution:**

```bash
# Install dev dependencies
pip install -e .[dev]

# Clear pytest cache
pytest --cache-clear

# Run tests
pytest
```

---

## 🔄 Updating ORC

### From Source

```bash
cd orc
git pull origin main
pip install -e .
```

### From PyPI (when available)

```bash
pip install --upgrade orc-codebase
```

---

## 🗑️ Uninstallation

### Remove Package

```bash
pip uninstall orc-codebase
```

### Remove All Files

```bash
# Remove cloned repository
rm -rf orc

# Remove cache files (optional)
rm -rf ~/.orc
```

---

## 📞 Getting Help

If you encounter issues:

1. **Check GitHub Issues**: [https://github.com/yourusername/orc/issues](https://github.com/yourusername/orc/issues)
2. **Create New Issue**: Include Python version, OS, and error message
3. **Check Documentation**: Full docs at [https://orc-docs.example.com](https://orc-docs.example.com)

---

## ✨ Next Steps

After installation:

1. **Read the Quick Start**: See README.md
2. **Try the Tutorial**: 
   ```bash
   orc init
   orc index
   orc scan
   ```
3. **Explore Commands**: 
   ```bash
   orc --help
   orc find --help
   ```

---

**Installation Complete! 🎉**

You're ready to start analyzing codebases with ORC.
