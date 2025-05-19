# Broetje Training System - File Structure Documentation

This document describes the comprehensive file structure created for the Broetje Training System.

## Directory Structure Overview

```
/media/ros2_ws/cross_platform/Projects Folder/AutomationAcademy/
├── modules/                      # Training modules directory
│   ├── module_loader/           # Dynamic module loading system
│   │   └── __init__.py         # Module loader implementation
│   ├── basic_plc/              # Basic PLC module
│   │   ├── metadata.json       # Module configuration
│   │   ├── module.py          # Module implementation
│   │   └── resources/         # Module resources
│   ├── advanced_plc/          # Advanced PLC module
│   │   ├── metadata.json
│   │   └── resources/
│   ├── hmi_development/       # HMI Development module
│   │   ├── metadata.json
│   │   └── resources/
│   ├── vision_systems/        # Vision Systems module
│   │   └── resources/
│   └── robotics_integration/  # Robotics Integration module
│       └── resources/
├── progress_tracking/         # Progress tracking system
│   ├── __init__.py           # Package initialization
│   ├── progress_manager.py   # Progress management logic
│   ├── report_generator.py   # Report generation
│   ├── progress_visualizer.py # Progress visualization
│   ├── reports/              # Generated reports directory
│   └── visualizations/       # Progress charts directory
└── user_management/          # User management system
    ├── __init__.py          # Package initialization
    ├── authentication.py    # Authentication & sessions
    ├── profile_manager.py   # User profile management
    ├── role_manager.py      # Role & permission management
    ├── profiles/            # User profile storage
    ├── authentication/      # Auth-related files
    └── roles/              # Role definitions

```

## Component Descriptions

### Module Loading Structure (`modules/`)

The module system provides dynamic loading and management of training modules:

- **module_loader**: Core module loading functionality
  - `ModuleLoader`: Dynamically loads modules from directory
  - `ModuleInfo`: Metadata container for modules
  - Version checking and dependency management
  - Module instance caching

- **Individual Modules**: Each module directory contains:
  - `metadata.json`: Module configuration including tasks, prerequisites, resources
  - `module.py`: Module implementation inheriting from TrainingModule
  - `resources/`: Module-specific resources (PDFs, videos, examples)

### Progress Tracking Structure (`progress_tracking/`)

Comprehensive progress tracking and reporting system:

- **ProgressManager**: 
  - Database operations for progress tracking
  - Task completion recording
  - Session management
  - Certification tracking

- **ReportGenerator**:
  - User progress reports (JSON, CSV, PDF)
  - Module statistics reports
  - Department-wide reports
  - Multiple export formats

- **ProgressVisualizer**:
  - User progress charts
  - Time spent visualizations
  - Learning timeline
  - Department comparisons
  - Module statistics

### User Management Structure (`user_management/`)

Complete user management with authentication and roles:

- **AuthenticationManager**:
  - User authentication
  - Session management
  - Password reset functionality
  - Two-factor authentication support
  - Login attempt tracking
  - Account lockout protection

- **ProfileManager**:
  - User profile management
  - Preference storage
  - Training history
  - Skill profiling
  - Achievement tracking
  - GDPR compliance (data export)

- **RoleManager**:
  - Role-based access control
  - Permission management
  - Role assignment/revocation
  - Custom role creation
  - Audit logging
  - Permission overrides

## Database Schema Extensions

The following tables have been added to support the new functionality:

### Progress Tracking Tables
- `user_progress`: Extended with more tracking fields
- `task_completions`: Detailed task completion tracking
- `training_sessions`: Session duration tracking
- `certifications`: Certification records

### User Management Tables
- `users`: Extended with profile fields
- `sessions`: Active session tracking
- `login_attempts`: Security monitoring
- `password_reset_tokens`: Password recovery

### Role Management Tables
- `roles`: Role definitions
- `user_roles`: Role assignments
- `permission_overrides`: Custom permissions
- `role_audit_log`: Role change tracking

## Key Features Implemented

### Module System
- Dynamic module loading
- Version management
- Prerequisite checking
- Resource management
- Task definitions with points

### Progress Tracking
- Real-time progress updates
- Task completion verification
- Time tracking
- Point accumulation
- Certification issuance

### User Management
- Secure authentication
- Session management
- Role-based permissions
- Profile customization
- Achievement system

### Reporting
- Multiple format support (JSON, CSV, PDF)
- User reports
- Module reports
- Department reports
- Visual progress charts

## Usage Examples

### Loading Modules
```python
from modules.module_loader import get_module_loader

loader = get_module_loader('/path/to/modules')
modules = loader.scan_modules()
module_instance = loader.get_module_instance('basic_plc')
```

### Tracking Progress
```python
from progress_tracking import ProgressManager

progress_mgr = ProgressManager('training_data.db')
progress_mgr.start_module(user_id, 'basic_plc')
progress_mgr.complete_task(user_id, 'basic_plc', 'task_1', points=10)
```

### Managing Users
```python
from user_management import AuthenticationManager, RoleManager

auth_mgr = AuthenticationManager('training_data.db')
success, user_info, error = auth_mgr.authenticate('username', 'password')

role_mgr = RoleManager('training_data.db')
role_mgr.assign_role(user_id, 'instructor')
```

### Generating Reports
```python
from progress_tracking import ReportGenerator

report_gen = ReportGenerator('training_data.db')
report_path = report_gen.generate_user_report(user_id, format='pdf')
```

## Configuration

Each component can be configured through:
- Database connection settings
- File storage paths  
- Security parameters
- Report output directories
- Module resource paths

## Security Considerations

- Password hashing with salts
- Session token management
- Login attempt monitoring
- Account lockout protection
- Permission-based access control
- Audit logging for compliance

## Future Enhancements

- Module marketplace integration
- Collaborative learning features
- Advanced analytics dashboard
- Mobile app synchronization
- Cloud backup functionality
- AI-powered recommendations

## Integration Points

The new structures integrate with existing code through:
- Database Manager class
- Training module base classes
- Main dashboard interface
- Configuration system
- Logging framework

This comprehensive structure provides a solid foundation for the Broetje Training System with scalability, security, and maintainability in mind.