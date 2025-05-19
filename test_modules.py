#!/usr/bin/env python3
"""
Test script to check if all modules load correctly
"""

import sys
import os
sys.path.append('/media/ros2_ws/cross_platform/Projects Folder/AutomationAcademy')

from training_module import get_module_class

# List of all modules to test
modules = [
    'Network File Sharing & Mapping',
    'Command Line Network Diagnostics',
    'IP Address Configuration',
    'Hard Drive Management',
    'Backup/Restore Operations',
    'Hard Drive Replacement',
    'Remote Access Configuration',
    'Batch File Scripting',
    'PowerShell Scripting',
    'OneDrive Integration'
]

# Test each module
for module_name in modules:
    print(f"\nTesting module: {module_name}")
    try:
        module_class = get_module_class(module_name)
        if module_class:
            print(f"✓ Module loaded successfully: {module_class.__name__}")
        else:
            print(f"✗ Module failed to load")
    except Exception as e:
        print(f"✗ Error loading module: {e}")