# Contributing to ORC

Thank you for your interest in contributing to ORC! We're excited to have you as part of our community.

## 🌟 Ways to Contribute

- 🐛 **Report Bugs**: Found a bug? Let us know!
- 💡 **Suggest Features**: Have an idea? We'd love to hear it!
- 📝 **Improve Documentation**: Help others understand ORC better
- 💻 **Submit Code**: Fix bugs or implement new features
- 🎨 **Design**: Improve UI/UX
- 🧪 **Write Tests**: Help us maintain quality

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Git
- Basic understanding of Python and web development

### Setting Up Development Environment

1. **Fork and Clone**
   ```bash
   git clone https://github.com/xytricit/orc.git
   cd orc
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Development Dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Run Tests**
   ```bash
   pytest
   ```

5. **Start Development Server**
   ```bash
   python orc/web/app_new.py
   ```

## 📋 Development Guidelines

### Code Style

We follow these conventions:
- **Python**: [PEP 8](https://pep8.org/) with Black formatter
- **Line Length**: 100 characters
- **Imports**: Organized with isort
- **Type Hints**: Use them where appropriate

Run formatters before committing:
```bash
black orc/
isort orc/
```

### Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
feat: add new feature
fix: resolve bug in analysis
docs: update README
style: format code
refactor: restructure module
test: add unit tests
chore: update dependencies
```

Examples:
```
feat(cli): add new dead code detection algorithm
fix(web): resolve login redirect issue
docs(api): update endpoint documentation
```

### Branch Naming

Use descriptive branch names:
```
feature/add-java-support
fix/login-redirect-bug
docs/improve-readme
refactor/cleanup-parsers
```

## 🧪 Testing

### Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest orc/tests/test_analyzer.py

# Run with coverage
pytest --cov=orc --cov-report=html
```

### Writing Tests
- Place tests in `orc/tests/`
- Name test files `test_*.py`
- Use descriptive test names
- Include docstrings
- Test both success and failure cases

Example:
```python
def test_dead_code_detection_finds_unused_function():
    """Test that dead code detector identifies unused functions."""
    # Arrange
    code = "def unused(): pass"
    
    # Act
    result = detect_dead_code(code)
    
    # Assert
    assert len(result) == 1
    assert result[0]['name'] == 'unused'
```

## 📝 Documentation

### Code Documentation
- Use docstrings for all public functions/classes
- Follow [Google Style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)

Example:
```python
def analyze_complexity(code: str) -> Dict[str, Any]:
    """
    Analyze code complexity and return metrics.
    
    Args:
        code: Python source code as string
        
    Returns:
        Dictionary containing complexity metrics
        
    Raises:
        SyntaxError: If code is invalid
    """
    pass
```

### User Documentation
- Place in `docs/` directory
- Use Markdown format
- Include code examples
- Add screenshots for UI features

## 🐛 Bug Reports

Use the [Bug Report Template](.github/ISSUE_TEMPLATE/bug_report.md):

**Required Information:**
- ORC version
- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Error messages/logs

## 💡 Feature Requests

Use the [Feature Request Template](.github/ISSUE_TEMPLATE/feature_request.md):

**Required Information:**
- Problem description
- Proposed solution
- Alternative solutions considered
- Use cases
- Impact assessment

## 🔄 Pull Request Process

### Before Submitting
- [ ] Tests pass (`pytest`)
- [ ] Code is formatted (`black`, `isort`)
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Branch is up to date with main

### PR Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How to test these changes

## Checklist
- [ ] Tests pass
- [ ] Documentation updated
- [ ] Code formatted
- [ ] No console errors
```

### Review Process
1. Submit PR with clear description
2. Automated tests run
3. Code review by maintainers
4. Address feedback
5. Approval and merge

## 🎨 UI/UX Contributions

### Design Guidelines
- Follow existing black & green theme
- Ensure accessibility (WCAG 2.1 AA)
- Test on multiple browsers
- Mobile-friendly design
- Consistent spacing and typography

### CSS Style
- Use CSS custom properties
- Follow BEM naming convention
- Keep specificity low
- Document complex styles

## 🔒 Security

### Reporting Security Issues
**Do NOT** open public issues for security vulnerabilities.

Email: andohbempahnanaakwasi@gmail.com

Include:
- Description of vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

## 📜 Code of Conduct

### Our Standards
- Be respectful and inclusive
- Welcome diverse perspectives
- Accept constructive criticism
- Focus on what's best for the community
- Show empathy towards others

### Unacceptable Behavior
- Harassment or discrimination
- Trolling or inflammatory comments
- Personal attacks
- Publishing private information
- Other unprofessional conduct

## 💬 Communication

### Channels
- **GitHub Issues**: Bug reports, feature requests
- **GitHub Discussions**: Questions, ideas, general discussion
- **Discord**: Real-time chat (coming soon)
- **Email**: Direct contact with maintainers

### Response Times
- Bug reports: 1-3 days
- Feature requests: 1 week
- Pull requests: 3-5 days
- Security issues: 24 hours

## 🏆 Recognition

Contributors are recognized in:
- README.md contributors section
- Release notes
- Project website
- Annual contributor highlights

## 📚 Resources

### Helpful Links
- [Python Style Guide](https://pep8.org/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [Rich Documentation](https://rich.readthedocs.io/)

### Learning Resources
- [Git Tutorial](https://git-scm.com/docs/gittutorial)
- [pytest Guide](https://docs.pytest.org/)
- [Python AST Module](https://docs.python.org/3/library/ast.html)

## ❓ Questions?

Don't hesitate to ask! We're here to help:
- Open a [Discussion](https://github.com/xytricit/orc/discussions)
- Check existing [Issues](https://github.com/xytricit/orc/issues)
- Read the [Documentation](docs/)

---

**Thank you for contributing to ORC!** 💚

Your contributions make ORC better for everyone.
