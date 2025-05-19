# GitHub Setup Guide for Broetje Training System

## Installing GitHub CLI

### Ubuntu/Linux
```bash
# Add GitHub CLI repository
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null

# Update and install
sudo apt update
sudo apt install gh
```

### Windows
```powershell
# Using Chocolatey
choco install gh

# Or using Scoop
scoop install gh
```

### macOS
```bash
# Using Homebrew
brew install gh
```

## Authenticating with GitHub

```bash
# Login to GitHub
gh auth login

# Follow the prompts to authenticate via browser or token
```

## Repository Setup

### 1. Create a New Repository
```bash
# Create repository on GitHub
gh repo create broetje-training-system --public --description "Broetje Automation Training System"

# Initialize local repository
cd "/media/ros2_ws/cross_platform/Projects Folder/AutomationAcademy"
git init
git add .
git commit -m "Initial commit"

# Add remote and push
git remote add origin https://github.com/your-username/broetje-training-system.git
git push -u origin main
```

### 2. Clone Existing Repository
```bash
# Clone repository
gh repo clone your-username/broetje-training-system

# Or with git
git clone https://github.com/your-username/broetje-training-system.git
```

## Module Structure

The system uses a modular architecture with the following structure:

```
modules/
├── template/                  # Module template
│   ├── __init__.py
│   ├── metadata.json         # Module configuration
│   ├── module.py            # Module implementation
│   └── resources/           # Module resources
├── network_file_sharing/
├── cli_diagnostics/
├── ip_configuration/
└── ... (other modules)
```

### Module Metadata Format
```json
{
  "id": "module_id",
  "name": "Module Name",
  "version": "1.0.0",
  "description": "Module description",
  "category": "networking",
  "difficulty": "beginner|intermediate|advanced",
  "estimated_time": "30 minutes",
  "dependencies": [],
  "prerequisites": [],
  "learning_objectives": [],
  "tags": [],
  "tasks": [
    {
      "id": "task_1",
      "title": "Task Title",
      "description": "Task description",
      "type": "practical",
      "estimated_time": "10 minutes",
      "points": 25,
      "validation": {
        "type": "screenshot",
        "required": true
      }
    }
  ]
}
```

## Creating New Modules

1. Copy the template module:
```bash
cp -r modules/template modules/your_module_name
```

2. Update metadata.json with your module information

3. Implement module.py with your training content

4. Add resources to the resources/ directory

5. Test the module:
```python
from module_loader import ModuleLoader
loader = ModuleLoader("modules")
module = loader.load_module("your_module_name")
```

## Progress Tracking

The system tracks user progress automatically:

```python
from progress_tracker import ProgressTracker

tracker = ProgressTracker("training_data.db")

# Start a task
tracker.start_task("task_1", "module_id", "user_id")

# Complete a task
tracker.complete_task("task_1", "module_id", "user_id", score=95.0)

# Get progress report
progress = tracker.get_user_progress("user_id")
```

## User Management

Manage users with different roles:

```python
from user_manager import UserManager, UserRole

user_mgr = UserManager("training_data.db")

# Create user
user = user_mgr.create_user(
    username="john_doe",
    email="john@company.com",
    password="secure_pass",
    full_name="John Doe",
    role=UserRole.TRAINEE
)

# Authenticate
session = user_mgr.authenticate("john_doe", "secure_pass")

# Check permissions
has_perm = user_mgr.has_permission(user.user_id, "view_progress")
```

## Deployment

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Initialize database:
```python
python main.py --init-db
```

3. Run the application:
```python
python main.py
```

4. Build executable (Windows):
```bash
python build.py
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-module`
3. Make your changes
4. Test thoroughly
5. Commit: `git commit -m "Add new module"`
6. Push: `git push origin feature/new-module`
7. Create a Pull Request using GitHub CLI:
```bash
gh pr create --title "Add new module" --body "Description of changes"
```

## GitHub Actions (CI/CD)

Create `.github/workflows/test.yml`:

```yaml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    - name: Run tests
      run: |
        python test_modules.py
```

## License

[Add your license here]

## Support

For issues or questions:
- Create an issue: `gh issue create`
- View issues: `gh issue list`
- Contact: training@broetje-automation.com