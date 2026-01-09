# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 2.0.x   | :white_check_mark: |
| 1.0.x   | :x:                |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security issue in ORC, please report it responsibly.

### How to Report

1. **DO NOT** open a public GitHub issue
2. Email security concerns to: [security@orc-project.dev] (or your team's security email)
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### What to Expect

- **Acknowledgment**: Within 48 hours
- **Initial Assessment**: Within 1 week
- **Fix Timeline**: Depends on severity
  - Critical: 1-3 days
  - High: 1-2 weeks
  - Medium: 2-4 weeks
  - Low: Next release

### Security Best Practices

When using ORC:

1. **Never commit API keys** - Use `.env` files (already in `.gitignore`)
2. **Use environment variables** for all secrets (see `.env.example`)
3. **Keep dependencies updated** - Run `pip install --upgrade -r requirements.txt`
4. **Limit file analysis scope** - Use `.orcignore` for sensitive directories
5. **Review AI responses** - Don't blindly trust AI suggestions for security-critical code
6. **Enable HTTPS** - When deploying the web interface in production
7. **Set strong SECRET_KEY** - Generate with: `python -c "import secrets; print(secrets.token_hex(32))"`

### Known Security Considerations

- **Local Analysis**: ORC analyzes your codebase locally by default
- **AI Features**: When enabled, code snippets are sent to third-party AI APIs
- **API Keys**: Stored in environment variables, never in code
- **Web Dashboard**: Should not be exposed to public internet without authentication
- **Docker Security**: Containers run as non-root user by default

### Environment Variables Security

Required environment variables for production:
```bash
ORC_SECRET_KEY=<generate-random-hex-string>
```

Optional AI provider keys (only set what you use):
```bash
GROQ_API_KEY=<your-key>
GEMINI_API_KEY=<your-key>
OPENAI_API_KEY=<your-key>
# etc.
```

### Dependency Security

ORC uses the following security measures:
- Regular dependency updates via Dependabot
- No known vulnerable dependencies in production build
- Minimal dependencies in production (`requirements-prod.txt`)

### Secure Deployment

For production deployments:
1. Use the provided `Dockerfile` which includes security best practices
2. Run containers as non-root user (already configured)
3. Enable health checks (already configured in Dockerfile)
4. Use environment variables for all secrets
5. Enable HTTPS via reverse proxy (nginx/Apache)
6. Regularly update base images

### Security Audit History

- **2026-01-09**: Initial security review completed
  - Hard-coded SECRET_KEY removed
  - Environment variable system implemented
  - Docker security hardening applied

## Credits

We appreciate responsible disclosure from the security community.
