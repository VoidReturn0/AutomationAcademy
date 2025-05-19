# Broetje Automation Training System

<div align="center">

![Broetje Logo](resources/images/broetje_logo.png)

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![PySide6](https://img.shields.io/badge/PySide6-6.0+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux-lightgrey.svg)
[![Tests](https://github.com/VoidReturn0/AutomationAcademy/actions/workflows/tests.yml/badge.svg)](https://github.com/VoidReturn0/AutomationAcademy/actions/workflows/tests.yml)
[![GitHub Issues](https://img.shields.io/github/issues/VoidReturn0/AutomationAcademy)](https://github.com/VoidReturn0/AutomationAcademy/issues)
[![GitHub Stars](https://img.shields.io/github/stars/VoidReturn0/AutomationAcademy)](https://github.com/VoidReturn0/AutomationAcademy/stargazers)

</div>

A comprehensive training platform designed for controls engineers at Broetje Automation USA, specializing in aerospace manufacturing systems.

## 📑 Table of Contents

- [🎯 Overview](#-overview)
- [✨ Features](#-features)
- [🚀 Quick Start](#-quick-start)
- [📚 Training Modules](#-training-modules)
- [🏗️ Architecture](#️-architecture)
- [🔧 Configuration](#-configuration)
- [🛠️ Development](#️-development)
- [🤝 Contributing](#-contributing)
- [📋 Testing](#-testing)
- [📝 License](#-license)
- [🙏 Acknowledgments](#-acknowledgments)

## 🎯 Overview

The Broetje Training System provides interactive training modules for aerospace manufacturing equipment, including:
- PowerRACe Systems - Robotic assembly cells for precision drilling and riveting
- MPAC Systems - Multi Panel Assembly Cells for large aircraft structures  
- IPAC Systems - Integrated Panel Assembly Cells with quality control

## ✨ Features

- **Interactive Training Modules** - Hands-on exercises for real-world scenarios
- **Progress Tracking** - Monitor training completion and performance metrics
- **User Management** - Multi-role support (Admin, Instructor, Trainee)
- **Screenshot Verification** - Document task completion with visual evidence
- **GitHub Integration** - Automatic backup of training records
- **Offline Capability** - Works without internet connectivity
- **Certificate Generation** - Issue completion certificates with QR codes

## 🚀 Quick Start

### Requirements

- Python 3.8+
- Windows 10/11 or Linux
- 4GB RAM minimum
- 1GB disk space

### Installation

1. Clone the repository:
```bash
git clone https://github.com/VoidReturn0/AutomationAcademy.git
cd AutomationAcademy
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python main.py
```

Default admin credentials:
- Username: `admin`
- Password: `admin123`

## 📚 Training Modules

### Basic Computer Skills
- **Network File Sharing & Mapping** - Map network drives across automation networks
- **Command Line Diagnostics** - Master network troubleshooting tools
- **IP Address Configuration** - Configure IPs for production/engineering networks

### System Maintenance
- **Backup/Restore Operations** - System imaging with Paragon software
- **Hard Drive Replacement** - SSD replacement procedures for Siemens IPCs  
- **Remote Access Configuration** - Setup UltraVNC for remote support

### Advanced Topics
- **PowerShell Scripting** - Automation scripts for system administration
- **PLC Programming** - Basic and advanced PLC programming concepts
- **HMI Development** - Create operator interfaces

## 🏗️ Architecture

```
AutomationAcademy/
├── main.py                 # Main application entry point
├── training_module.py      # Base module classes
├── module_window.py        # Module execution window
├── module_loader.py        # Dynamic module loading
├── user_manager.py         # User authentication
├── github_integration.py   # GitHub API integration
├── modules/               # Training module plugins
│   ├── network_file_sharing/
│   ├── cli_diagnostics/
│   └── ...
├── resources/             # Images, icons, guides
├── config/               # Configuration files
└── docs/                # Documentation
```

## 🔧 Configuration

### Network Settings
Configure network ranges in `config/app_config.json`:
- Production: `192.168.214.x`
- Engineering: `192.168.213.x`  
- Management: `192.168.1.x`

### GitHub Integration
Set up automatic backups in `config/github_config.json`:
```json
{
  "repository_url": "https://github.com/your-org/training-records",
  "api_token": "your-github-token",
  "auto_upload": true
}
```

## 🛠️ Development

### Building Executable
Create a standalone Windows executable:
```bash
python build.py
```

The executable will be created in `dist/BroetjeTrainingSystem.exe`

### Creating New Modules

1. Create module directory: `modules/your_module/`
2. Add `metadata.json` with module information
3. Create `module.py` extending `TrainingModule` class
4. Define tasks and learning objectives

Example module structure:
```python
class YourModule(TrainingModule):
    def get_learning_objectives(self):
        return ["Objective 1", "Objective 2"]
    
    def get_tasks(self):
        return [
            {
                'name': 'Task Name',
                'description': 'Task description',
                'instructions': ['Step 1', 'Step 2'],
                'required': True,
                'screenshot_required': True
            }
        ]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -m 'Add your feature'`
4. Push to branch: `git push origin feature/your-feature`
5. Submit a pull request

## 📋 Testing

Run the test suite:
```bash
# Run module tests
python test_modules.py

# Test core functionality  
python test_functionality.py

# Test database operations
python test_reset_progress.py
```

For UI testing, run the application in test mode:
```bash
python main.py --test-mode
```

## 🐛 Known Issues

- Windows Defender may flag the executable - add to exclusions
- Screenshots require proper display permissions on Linux
- VPN connections may interfere with network module exercises

## 📞 Support

For assistance, contact:
- Site Manager: [your-email@broetje.com]
- Training Department: [training@broetje.com]

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 🏢 About Broetje Automation

Broetje Automation USA provides advanced automation solutions for the aerospace industry, specializing in automated drilling, riveting, and assembly systems for aircraft manufacturers worldwide.

Locations:
- Savannah, GA (Main Training Facility)
- Lake Charles, LA
- Wichita, KS

## 🙏 Acknowledgments

- Broetje Automation Engineering Team
- Site management for supporting continuous training initiatives
- All technicians who contributed to module development
- Open source community for providing robust development tools

---

<div align="center">

**Broetje Automation USA** - *Engineering the Future of Aerospace Manufacturing*

[![Made with Love](https://img.shields.io/badge/Made%20with-❤️-red)](https://broetje-automation.com)

</div>