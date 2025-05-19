Broetje Training System - Project Documentation
🚀 Quick Start Guide
Prerequisites

Windows 10/11
Python 3.11+ (for development)
Git

Development Setup

Clone Repository

bashgit clone https://github.com/your-org/broetje-training-system.git
cd broetje-training-system

Create Virtual Environment

bashpython -m venv venv
venv\Scripts\activate

Install Dependencies

bashpip install -r requirements.txt

Run Application

bashpython main.py
Building Executable

Run Build Script

bashpython deployment/build_exe.py

Find Installer


Executable: dist/BroetjeTrainingSystem.exe
Installer: dist/BroetjeTrainingSystem_Installer.exe

📁 Project Structure
broetje-training/
├── main.py                     # Main application entry
├── training_modules.py         # Module base classes
├── module_window.py           # Individual module execution
├── requirements.txt           # Dependencies
├── config/
│   ├── app_config.json        # Application configuration
│   └── github_config.json     # GitHub integration settings
├── resources/
│   ├── icons/                 # Application icons
│   ├── images/                # UI images
│   └── styles/               # Custom stylesheets
├── modules/                   # Training module implementations
│   ├── network_file_sharing/
│   ├── command_line_diagnostics/
│   ├── ip_configuration/
│   ├── hard_drive_management/
│   ├── backup_restore/
│   ├── hard_drive_replacement/
│   ├── remote_access/
│   ├── batch_scripting/
│   ├── powershell_scripting/
│   └── onedrive_integration/
├── data/                      # Database files
├── screenshots/               # Training screenshots
├── deployment/                # Build scripts
└── docs/                      # Documentation
🔧 Key Features
1. Modular Architecture

Each training module is a separate class
Easy to add new modules
Standardized interface for all modules

2. Database Integration

SQLite for local data storage
User progress tracking
Task completion verification
Digital signatures

3. GitHub Integration

Download modules from repository
Version control for training content
Automatic updates

4. Professional UI

Broetje brand colors and styling
Responsive design
Intuitive navigation

5. Admin Features

User management
Progress monitoring
System configuration
Export capabilities

6. Security

User authentication
Role-based access
Session management
Secure password storage

🎯 Training Modules
Network & System Administration

Network File Sharing & Mapping

Map network drives
Share folders
Access permissions


Command Line Network Diagnostics

ping, tracert, nslookup
Network troubleshooting
Command line basics


IP Address Configuration

Static IP setup
Network ranges (214.x, 213.x, 1.x)
Subnet configuration



Hardware Management

Hard Drive Management

Disk partitioning
File system management
Storage optimization


Backup/Restore Operations

Paragon software usage
Backup strategies
Restore procedures


Hard Drive Replacement

SSD installation
Torx tool usage
Hardware safety



Remote Access & Security

Remote Access Configuration

UltraVNC setup
Security configuration
Password management



Automation & Scripting

Batch File Scripting

Batch file creation
Automation tasks
File operations


PowerShell Scripting

Advanced scripting
System administration
Object-oriented concepts



Cloud Integration

OneDrive Integration

Cloud backup setup
Synchronization
File sharing



🔐 User Roles
Admin

Full system access
User management
Module configuration
Progress monitoring
System settings

Trainer

Verify trainee completions
View progress reports
Access all modules
Digital signature verification

Trainee

Access assigned modules
Complete training tasks
Submit digital signatures
View personal progress

📊 Progress Tracking
Individual Progress

Module completion status
Task-level tracking
Time spent per module
Score/performance metrics

Administrative Views

Company-wide statistics
Individual trainee reports
Completion rates
Training effectiveness

🛠️ Configuration
Application Settings (config/app_config.json)

Database configuration
GitHub integration
UI preferences
Security settings
Backup options

Module Configuration

Prerequisites
Estimated duration
Required tasks
Verification requirements

📥 Deployment
For Administrators

Download installer from shared drive
Run BroetjeTrainingSystem_Installer.exe
Follow installation wizard
Launch from desktop/start menu

For Developers

Use PyInstaller script for custom builds
Test on target systems
Create deployment packages
Distribute via network/USB

🔧 Customization
Adding New Modules

Create new module class inheriting from TrainingModule
Implement required methods
Add to MODULE_REGISTRY
Update database schema if needed

UI Customization

Modify StyleManager for theme changes
Update resource files for new icons/images
Adjust layout classes for UI changes

Integration Options

GitHub for module distribution
Network drives for file sharing
Email for completion notifications
LDAP for user authentication

📋 Best Practices
For Trainees

Complete prerequisites first
Take clear screenshots
Add meaningful notes
Verify all required tasks

For Trainers

Review completions promptly
Provide constructive feedback
Verify practical skills
Monitor progress regularly

For Administrators

Regular database backups
Keep modules updated
Monitor system performance
Review security logs

🐛 Troubleshooting
Common Issues
Module Won't Load

Check module files exist
Verify prerequisites met
Review error logs

Database Errors

Check file permissions
Verify database integrity
Restore from backup if needed

Network Issues

Verify drive mappings
Check network connectivity
Test with different user

Screenshot Problems

Check permissions
Verify storage space
Update graphics drivers

📞 Support
Internal Support

IT Department: ext. 1234
Training Coordinator: ext. 5678
System Administrator: ext. 9012

Documentation

User Manual: /docs/user_guide.pdf
Admin Guide: /docs/admin_guide.pdf
API Documentation: /docs/api_docs.html

🔄 Updates & Maintenance
Regular Tasks

Database backup (daily)
Log file rotation (weekly)
Module updates (as needed)
System health checks (monthly)

Version Control

GitHub for code management
Semantic versioning
Release notes maintenance
Rollback procedures


This documentation is maintained by the Broetje Automation Training Initiative Team