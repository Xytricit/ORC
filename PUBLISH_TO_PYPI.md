# Publishing ORC to PyPI - Step by Step Guide

Your package is ready! Follow these steps to publish to PyPI.

## Prerequisites

### 1. Create PyPI Accounts

**Production PyPI:**
- Go to: https://pypi.org/account/register/
- Create account and verify email

**TestPyPI (for testing):**
- Go to: https://test.pypi.org/account/register/
- Create account and verify email

### 2. Generate API Tokens

**For TestPyPI:**
1. Go to https://test.pypi.org/manage/account/token/
2. Click "Add API token"
3. Token name: `orc-cli-upload`
4. Scope: "Entire account" (or specific to orc-cli later)
5. **COPY THE TOKEN** (you can't see it again!)

**For Production PyPI:**
1. Go to https://pypi.org/manage/account/token/
2. Click "Add API token"
3. Token name: `orc-cli-upload`
4. Scope: "Entire account"
5. **COPY THE TOKEN**

### 3. Configure Credentials

Create/edit `~/.pypirc`:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR-TEST-TOKEN-HERE

[pypi]
repository = https://pypi.org/legacy/
username = __token__
password = pypi-YOUR-PRODUCTION-TOKEN-HERE
```

**On Windows:** `C:\Users\YourUsername\.pypirc`

## Publishing Steps

### Step 1: Install Twine

```bash
pip install twine
```

### Step 2: Verify Package

```bash
# Check that packages are valid
twine check dist/*
```

Expected output:
```
Checking dist/orc_cli-1.0.0-py3-none-any.whl: PASSED
Checking dist/orc_cli-1.0.0.tar.gz: PASSED
```

### Step 3: Test on TestPyPI (RECOMMENDED)

```bash
# Upload to TestPyPI
twine upload --repository testpypi dist/*
```

You'll see:
```
Uploading distributions to https://test.pypi.org/legacy/
Uploading orc_cli-1.0.0-py3-none-any.whl
Uploading orc_cli-1.0.0.tar.gz
View at: https://test.pypi.org/project/orc-cli/
```

### Step 4: Test Installation from TestPyPI

```bash
# Create fresh test environment
python -m venv test_env
test_env\Scripts\activate  # Windows
# source test_env/bin/activate  # Linux/Mac

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ orc-cli

# Test it works
orc --version
orc --help

# Deactivate when done
deactivate
```

### Step 5: Publish to Production PyPI

**Once you verify TestPyPI works:**

```bash
# Upload to Production PyPI
twine upload dist/*
```

You'll see:
```
Uploading distributions to https://upload.pypi.org/legacy/
Uploading orc_cli-1.0.0-py3-none-any.whl
Uploading orc_cli-1.0.0.tar.gz
View at: https://pypi.org/project/orc-cli/
```

### Step 6: Verify on PyPI

1. Visit: https://pypi.org/project/orc-cli/
2. Check the page displays correctly
3. Test installation:

```bash
pip install orc-cli
orc --version
```

## After Publishing

### 1. Create GitHub Release

```bash
# Tag the release
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

Then on GitHub:
1. Go to https://github.com/xytricit/orc/releases/new
2. Choose tag: `v1.0.0`
3. Title: `ORC v1.0.0 - Initial Release`
4. Description: Copy from CHANGELOG.md
5. Attach: `dist/orc_cli-1.0.0.tar.gz` and `.whl` files
6. Publish release

### 2. Update Documentation

Add installation instructions to README.md:

```markdown
## Installation

```bash
pip install orc-cli
```

## Quick Start

```bash
# Start ORC
orc

# Or specific commands
orc stats
orc analyze
```
```

### 3. Announce

- Post on Twitter/X
- Post on Reddit (r/Python)
- Post on Discord communities
- LinkedIn update

## Troubleshooting

### "Package already exists"

If you already uploaded this version, you must bump the version:
1. Update version in `pyproject.toml`
2. Update version in `setup.py`
3. Update version in `orc/__init__.py`
4. Rebuild: `python setup.py sdist bdist_wheel`
5. Upload again

### "Invalid credentials"

- Check `~/.pypirc` has correct tokens
- Tokens start with `pypi-`
- Make sure no extra spaces

### "Package name not available"

If `orc-cli` is taken, you'll need to choose a different name like:
- `orc-analyzer`
- `orc-catalyst`
- `optimization-catalyst`

Check availability: https://pypi.org/search/?q=orc-cli

## Version Updates

For future updates:

1. Update version numbers everywhere
2. Update CHANGELOG.md
3. Rebuild package
4. Upload to TestPyPI first
5. Test thoroughly
6. Upload to Production PyPI
7. Create GitHub release

## Commands Quick Reference

```bash
# Build package
python setup.py sdist bdist_wheel

# Check package
twine check dist/*

# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Upload to Production PyPI
twine upload dist/*

# Test install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ orc-cli

# Production install
pip install orc-cli
```

---

**You're ready to publish!** 🚀

Start with TestPyPI to be safe, then go to production!
