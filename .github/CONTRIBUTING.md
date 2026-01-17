# Contributing to Multi-Agent RLM

Thank you for your interest in contributing to Multi-Agent RLM! This document provides guidelines and instructions for contributing.

## Code of Conduct

Be respectful, constructive, and professional in all interactions. We're building this together.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/firfircelik/multi-agent-rlm/issues)
2. If not, create a new issue using the Bug Report template
3. Provide as much detail as possible:
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details
   - Error messages

### Suggesting Features

1. Check if the feature has already been requested
2. Create a new issue using the Feature Request template
3. Clearly describe:
   - The problem you're trying to solve
   - Your proposed solution
   - Use cases and benefits

### Submitting Pull Requests

1. **Fork the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/multi-agent-rlm.git
   cd multi-agent-rlm
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Write clean, readable code
   - Follow existing code style
   - Add comments for complex logic
   - Update documentation as needed

4. **Add tests**
   ```bash
   # Add tests in tests/ directory
   python -m pytest tests/
   ```

5. **Format your code**
   ```bash
   black src/
   flake8 src/
   ```

6. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add amazing feature"
   ```
   
   Use conventional commit messages:
   - `feat:` for new features
   - `fix:` for bug fixes
   - `docs:` for documentation
   - `test:` for tests
   - `refactor:` for code refactoring
   - `perf:` for performance improvements

7. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

8. **Create a Pull Request**
   - Go to the original repository
   - Click "New Pull Request"
   - Select your branch
   - Fill out the PR template
   - Submit for review

## Development Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Install development tools
pip install pytest black flake8 mypy

# Run tests
python -m pytest tests/ -v

# Format code
black src/

# Check code quality
flake8 src/
mypy src/
```

## Code Style

- Follow PEP 8 style guide
- Use type hints for function parameters and return values
- Write docstrings for classes and functions
- Keep functions small and focused
- Use meaningful variable names

## Testing

- Write tests for new features
- Ensure all tests pass before submitting PR
- Aim for high test coverage
- Test edge cases and error conditions

## Documentation

- Update README.md if adding new features
- Add docstrings to new functions and classes
- Update configuration examples if needed
- Keep documentation clear and concise

## Review Process

1. Maintainers will review your PR
2. Address any requested changes
3. Once approved, your PR will be merged
4. Your contribution will be acknowledged

## Questions?

If you have questions, feel free to:
- Open an issue for discussion
- Ask in pull request comments
- Contact maintainers

Thank you for contributing to Multi-Agent RLM!
