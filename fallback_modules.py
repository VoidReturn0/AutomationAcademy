#!/usr/bin/env python3
"""
Fallback modules for training items that don't have dedicated module directories
"""

from training_module import TrainingModule
from typing import List, Dict

class HardDriveManagementModule(TrainingModule):
    """Hard Drive Management training module"""
    
    def get_learning_objectives(self) -> List[str]:
        return [
            "Understand hard drive partitioning concepts",
            "Use Disk Management tool effectively",
            "Create and manage disk partitions",
            "Format drives with appropriate file systems",
            "Monitor disk health and performance",
            "Configure drive letters and mount points"
        ]
    
    def get_tasks(self) -> List[Dict]:
        return [
            {
                'name': 'Open Disk Management',
                'description': 'Access Windows Disk Management tool',
                'instructions': [
                    'Right-click on Start button',
                    'Select "Disk Management"',
                    'Alternatively, run diskmgmt.msc',
                    'Familiarize yourself with the interface'
                ],
                'required': True,
                'screenshot_required': True
            },
            {
                'name': 'View Disk Information',
                'description': 'Understand current disk configuration',
                'instructions': [
                    'Identify all connected drives',
                    'Check drive sizes and partitions',
                    'Note the system drive (C:)',
                    'Identify SSDs vs HDDs',
                    'Check available free space'
                ],
                'required': True,
                'screenshot_required': True
            }
        ]


class BatchFileScriptingModule(TrainingModule):
    """Batch File Scripting training module"""
    
    def get_learning_objectives(self) -> List[str]:
        return [
            "Write basic batch file scripts",
            "Use common batch file commands",
            "Create automation scripts for tasks",
            "Handle variables and parameters",
            "Implement error handling in scripts",
            "Schedule batch files with Task Scheduler"
        ]
    
    def get_tasks(self) -> List[Dict]:
        return [
            {
                'name': 'Create First Batch File',
                'description': 'Create a simple batch file',
                'instructions': [
                    'Open Notepad',
                    'Type: @echo off',
                    'Type: echo Hello, World!',
                    'Type: pause',
                    'Save as "hello.bat"',
                    'Run the batch file'
                ],
                'required': True,
                'screenshot_required': True
            },
            {
                'name': 'Network Drive Mapping Script',
                'description': 'Create script to map network drives',
                'instructions': [
                    'Create new batch file',
                    'Add commands to map drives',
                    'Use net use command',
                    'Add error checking',
                    'Test the script'
                ],
                'required': True,
                'screenshot_required': True
            }
        ]


class OneDriveIntegrationModule(TrainingModule):
    """OneDrive Integration training module"""
    
    def get_learning_objectives(self) -> List[str]:
        return [
            "Configure OneDrive for business use",
            "Sync folders with cloud storage",
            "Manage selective sync settings",
            "Handle version conflicts",
            "Set up automatic backups",
            "Share files and collaborate"
        ]
    
    def get_tasks(self) -> List[Dict]:
        return [
            {
                'name': 'Setup OneDrive',
                'description': 'Configure OneDrive client',
                'instructions': [
                    'Open OneDrive settings',
                    'Sign in with business account',
                    'Choose sync location',
                    'Configure sync options',
                    'Verify connection status'
                ],
                'required': True,
                'screenshot_required': True
            },
            {
                'name': 'Configure Selective Sync',
                'description': 'Choose folders to sync',
                'instructions': [
                    'Right-click OneDrive icon',
                    'Select Settings',
                    'Go to Account tab',
                    'Click "Choose folders"',
                    'Select required folders only'
                ],
                'required': True,
                'screenshot_required': True
            }
        ]