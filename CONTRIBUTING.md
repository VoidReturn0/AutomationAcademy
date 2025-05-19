# Contributing to Broetje Training System

Thank you for your interest in contributing to the Broetje Training System! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/AutomationAcademy.git`
3. Create a new branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test your changes thoroughly
6. Submit a pull request

## Development Setup

1. Install Python 3.8 or higher
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Code Standards

- Follow PEP 8 Python style guide
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions focused and modular
- Add type hints where appropriate

## Testing

Before submitting changes:

1. Run the test suite:
   ```bash
   python test_modules.py
   python test_functionality.py
   ```
2. Test the GUI manually:
   ```bash
   python main.py
   ```
3. Verify database operations
4. Ensure all modules load correctly

## Creating New Modules

When adding a new training module:

1. Create a directory in `modules/` with your module name
2. Include the following files:
   - `__init__.py`
   - `module.py` (inheriting from `TrainingModule`)
   - `metadata.json` with module configuration
   - `resources/` directory for any assets

3. Module metadata structure:
   ```json
   {
     "name": "Module Name",
     "description": "Brief description",
     "category": "One of: PLCs, Networking, System Admin, HMI, Advanced",
     "difficulty": "One of: Beginner, Intermediate, Advanced",
     "estimated_time": "Time in minutes",
     "required": ["prerequisite", "modules"],
     "order": 1
   }
   ```

## Pull Request Process

1. Update the README.md with details of changes if needed
2. Update version numbers following semantic versioning
3. Ensure all tests pass
4. Include screenshots for UI changes
5. Link any related issues

## Bug Reports

When filing a bug report, include:

- Python version
- Operating system
- Full error traceback
- Steps to reproduce
- Expected behavior
- Actual behavior

## Feature Requests

When requesting features:

- Describe the use case
- Explain why it would benefit users
- Consider implementation approach
- Check if it aligns with project goals

## Commit Messages

Use conventional commit format:

- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `style:` Code style changes
- `refactor:` Code refactoring
- `test:` Test additions/changes
- `chore:` Maintenance tasks

Example: `feat: add remote desktop connection module`

## Code Review

All contributions require code review:

- Be respectful and constructive
- Focus on the code, not the person
- Suggest improvements
- Acknowledge good patterns
- Test locally before approving

## Module Categories

When creating modules, use these categories:

- **PLCs**: Allen Bradley, Siemens programming
- **Networking**: IP configuration, diagnostics
- **System Admin**: Backup, drive management
- **HMI**: PanelView, visualization systems
- **Advanced**: Robotics, vision systems

## Documentation

Update documentation for:

- New features in README.md
- API changes in code comments
- User-facing changes in module guides
- Architecture changes in CLAUDE.md

## Questions?

If you have questions:

1. Check existing issues
2. Review documentation
3. Ask in discussions
4. Contact the maintainers

Thank you for contributing to the Broetje Training System!