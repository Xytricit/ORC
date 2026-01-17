# ORC Troubleshooting Guide

Common issues and their solutions.

## Table of Contents
- [Installation Issues](#installation-issues)
- [Import Errors](#import-errors)
- [API Key Issues](#api-key-issues)
- [Docker Issues](#docker-issues)
- [Performance Issues](#performance-issues)
- [Web Interface Issues](#web-interface-issues)
- [Debug Mode](#debug-mode)

---

## Installation Issues

### Problem: `pip install -e .` fails

**Symptoms:**
```
ERROR: Failed building wheel for package
```

**Solutions:**

1. **Upgrade pip and setuptools:**
```bash
python -m pip install --upgrade pip setuptools wheel
```

2. **Install with verbose output:**
```bash
pip install -e . -v
```

3. **Check Python version:**
```bash
python --version  # Should be 3.8+
```

### Problem: Missing dependencies

**Symptoms:**
```
ModuleNotFoundError: No module named 'click'
```

**Solution:**
```bash
cd orc
pip install -r requirements.txt
```

For AI features:
```bash
pip install -e .[ai]
```

---

## Import Errors

### Problem: `ModuleNotFoundError: No module named 'orc'`

**Symptoms:**
```
ImportError: attempted relative import with no known parent package
```

**Solutions:**

1. **Install ORC in development mode:**
```bash
pip install -e .
```

2. **Check PYTHONPATH:**
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

3. **Run from correct directory:**
```bash
# Run from project root, not orc/ subdirectory
cd /path/to/ORC
orc --help
```

### Problem: `ModuleNotFoundError: No module named 'storage'`

**Cause:** Incorrect import paths (should be fixed in v2.0.0)

**Solution:** Update to latest version or fix imports:
```python
# Wrong:
from storage.cache import Cache

# Correct:
from orc.storage.cache import Cache
```

---

## API Key Issues

### Problem: No AI provider available

**Symptoms:**
```
Error: No AI provider configured
```

**Solutions:**

1. **Set up environment variables:**
```bash
cd orc
cp .env.example .env
# Edit .env and add your API key
```

2. **For Ollama (free, local):**
```bash
# Install Ollama from https://ollama.ai
ollama pull llama3.1
export OLLAMA_BASE_URL=http://localhost:11434
export OLLAMA_MODEL=llama3.1
```

3. **For Groq (free tier):**
```bash
# Get key from https://console.groq.com/
export GROQ_API_KEY=your_key_here
```

4. **Check environment variables:**
```bash
env | grep -E "(GROQ|OLLAMA|GEMINI|OPENAI)"
```

### Problem: API rate limiting

**Symptoms:**
```
Error 429: Rate limit exceeded
```

**Solutions:**

1. **Switch providers:**
```bash
export ORC_AI_PROVIDER=ollama  # Use local Ollama instead
```

2. **Use context compression:**
```bash
orc chat --compress
```

3. **Reduce analysis scope:**
```bash
# Add to .orcignore
tests/
docs/
*.md
```

---

## Docker Issues

### Problem: Docker build fails

**Symptoms:**
```
ERROR: failed to solve: failed to copy files
```

**Solutions:**

1. **Check Dockerfile path:**
```bash
docker build -t orc:latest -f orc/Dockerfile .
```
Note: Run from project root, not `orc/` directory

2. **Check requirements-prod.txt exists:**
```bash
ls orc/requirements-prod.txt
```

3. **Clean Docker cache:**
```bash
docker system prune -a
docker build --no-cache -t orc:latest -f orc/Dockerfile .
```

### Problem: Container exits immediately

**Symptoms:**
```
docker run orc:latest
# Container exits with code 1
```

**Solutions:**

1. **Check logs:**
```bash
docker logs <container-id>
```

2. **Run interactively:**
```bash
docker run -it orc:latest /bin/bash
```

3. **Check entry point:**
```bash
docker run orc:latest orc --help
```

### Problem: Permission denied in container

**Symptoms:**
```
PermissionError: [Errno 13] Permission denied: '/app/.orc'
```

**Solution:** Mount volume with correct permissions:
```bash
docker run -v $(pwd):/workspace -w /workspace orc:latest
```

---

## Performance Issues

### Problem: Indexing takes too long

**Symptoms:**
- Indexing hangs on large codebases
- High memory usage

**Solutions:**

1. **Add ignore patterns:**
```bash
# Create .orcignore
echo "node_modules/" >> .orcignore
echo ".venv/" >> .orcignore
echo "dist/" >> .orcignore
```

2. **Increase parallel workers:**
```bash
export ORC_PARALLEL_WORKERS=8
```

3. **Clear cache and reindex:**
```bash
rm -rf .orc/
orc index .
```

### Problem: High memory usage

**Solutions:**

1. **Use streaming mode (if available):**
```bash
orc index . --stream
```

2. **Process in batches:**
```bash
# Index specific directories
orc index ./src
orc index ./lib
```

3. **Limit file size:**
```bash
export MAX_FILE_SIZE_MB=5
```

---

## Web Interface Issues

### Problem: Web server won't start

**Symptoms:**
```
Error: Address already in use
```

**Solutions:**

1. **Check if port is in use:**
```bash
# Linux/Mac
lsof -i :8000

# Windows
netstat -ano | findstr :8000
```

2. **Use different port:**
```bash
orc serve --port 8001
```

3. **Kill existing process:**
```bash
# Linux/Mac
kill -9 <PID>

# Windows
taskkill /PID <PID> /F
```

### Problem: 500 Internal Server Error

**Solutions:**

1. **Check SECRET_KEY is set:**
```bash
export ORC_SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
```

2. **Check logs:**
```bash
tail -f orc_web.log
```

3. **Enable debug mode (development only):**
```bash
export ORC_DEBUG=true
orc serve
```

---

## Debug Mode

### Enable Debug Logging

**Method 1: Environment variable**
```bash
export ORC_DEBUG=true
orc chat
```

**Method 2: CLI flag**
```bash
orc --debug chat
```

**Method 3: Config file**
```python
# orc/config/settings.py
DEBUG = True
```

### Verbose Output

```bash
orc -v index .    # Verbose
orc -vv index .   # Very verbose
```

### Check Configuration

```bash
orc config show
```

### Test AI Connection

```bash
orc test-ai
```

---

## Common Error Messages

### `SyntaxError: invalid escape sequence`

**Cause:** Python 3.12+ stricter regex handling

**Solution:** Update to ORC v2.0.0+ (fixed)

### `ImportError: cannot import name 'Cache'`

**Cause:** Incorrect import paths

**Solution:** Update to ORC v2.0.0+ (fixed)

### `RuntimeError: Event loop is closed`

**Cause:** Async issues with AI providers

**Solution:**
```bash
export PYTHONWARNINGS=ignore::DeprecationWarning
```

---

## Getting Help

### Check Version

```bash
orc --version
```

### Run Tests

```bash
cd orc
pytest tests/ -v
```

### Generate Debug Report

```bash
orc debug-report > debug_output.txt
```

### Report an Issue

Include in your bug report:
1. ORC version (`orc --version`)
2. Python version (`python --version`)
3. Operating system
4. Full error message
5. Steps to reproduce
6. Debug output

---

## FAQs

### Q: Can I use ORC without AI features?

**A:** Yes! ORC works great for static analysis without AI:
```bash
orc index .
orc dead
orc deps
orc metrics
```

### Q: Which AI provider is recommended?

**A:** 
- **Free & Local:** Ollama (best for privacy)
- **Free & Cloud:** Groq (fast, good quality)
- **Paid & Best:** Claude 3.5 Sonnet (via Anthropic)

### Q: How do I update ORC?

**A:**
```bash
git pull
pip install -e . --upgrade
```

### Q: Is my code sent to AI providers?

**A:** Only when you use `orc chat` or AI features. Regular analysis is 100% local.

### Q: Can I analyze private repositories?

**A:** Yes! ORC runs locally. For cloud AI features, only relevant code snippets are sent (never full files).

---

## Still Having Issues?

1. Check [DEPLOYMENT.md](DEPLOYMENT.md) for setup instructions
2. Review [SECURITY.md](SECURITY.md) for security best practices
3. Search existing [GitHub Issues](https://github.com/yourusername/orc/issues)
4. Open a new issue with debug information
