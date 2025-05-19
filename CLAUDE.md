# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

The Broetje Training System is a comprehensive training application for controls engineers at Broetje Automation USA. It's a PySide6-based desktop application that provides interactive training modules, progress tracking, and user management capabilities.

## Key Architecture

### Core Components

1. **Main Application** (`main.py`): Contains the main dashboard window (`TrainingDashboard`) with tabs for:
   - Dashboard overview
   - Training modules
   - Progress tracking
   - Admin panel (role-based)

2. **Database Manager** (`DatabaseManager` in `main.py`): Handles all SQLite database operations including:
   - User authentication
   - Progress tracking
   - Module management
   - System settings

3. **Module System**:
   - `training_module.py`: Base classes and module registry
   - `module_window.py`: Individual module execution window
   - `additional_modules.py`: Additional module implementations
   - `modules/`: Directory for dynamically loaded modules

4. **GitHub Integration** (`github_integration.py`): Handles module downloads and updates from GitHub repository

5. **User Management** (`user_managment.py`): User administration functionality

## Development Commands

### Run the Application
```bash
python main.py
```

### Build Executable (Production)
```bash
python build.py
```

### Quick Build (Testing)
```bash
python deployment/build_exe.py
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Database Operations

The database is SQLite-based (`training_data.db`) with tables for:
- users
- modules
- user_progress
- module_tasks
- task_completions
- settings

Default admin credentials: username: `admin`, password: `admin123`

## Key Configuration

Configuration files are stored in `config/`:
- `app_config.json`: Main application settings (database, network, UI, logging)
- `github_config.json`: GitHub repository settings for module downloads

Important network configurations:
- Production network: `192.168.214.x`
- Engineering network: `192.168.213.x`
- Management network: `192.168.1.x`
- VNC password: `ae746`

## Deployment

The application uses PyInstaller for creating Windows executables:
- Full build script: `build.py` (includes icons, version info, installer)
- Quick build: `deployment/build_exe.py` (basic executable)
- Output locations:
  - Executable: `dist/BroetjeTrainingSystem.exe`
  - Installer: `dist/BroetjeTrainingSystem_Installer.exe`

## Module Development

Training modules inherit from `TrainingModule` base class and should implement:
- Task definitions
- Progress tracking
- Screenshot capture
- Verification requirements

Modules are loaded dynamically from the `modules/` directory and can be downloaded from GitHub.

## Testing

The application uses SQLite database for testing. Create a test database by running the application - it will initialize the schema automatically.

## Logging

Application logs are written to `training_app.log` with configurable levels. Logging configuration is in `config/app_config.json`.