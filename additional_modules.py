#!/usr/bin/env python3
"""
Additional Training Modules
Implementation of specific training modules for Broetje systems
"""

from training_modules import TrainingModule
from typing import List, Dict

class CommandLineDiagnosticsModule(TrainingModule):
    """Command Line Network Diagnostics training module"""
    
    def get_learning_objectives(self) -> List[str]:
        return [
            "Master basic network diagnostic commands",
            "Understand ping command and its parameters",
            "Use tracert for network path analysis",
            "Perform DNS lookups with nslookup",
            "Diagnose network connectivity issues",
            "Interpret command output for troubleshooting"
        ]
    
    def get_tasks(self) -> List[Dict]:
        return [
            {
                'name': 'Open Command Prompt',
                'description': 'Open Windows Command Prompt with administrator privileges',
                'instructions': [
                    'Press Windows key + R to open Run dialog',
                    'Type "cmd" and press Ctrl+Shift+Enter',
                    'Click "Yes" when prompted for administrator access',
                    'Verify prompt shows "Administrator: Command Prompt"'
                ],
                'required': True,
                'screenshot_required': True
            },
            {
                'name': 'Basic Ping Test',
                'description': 'Test connectivity to production server',
                'instructions': [
                    'Type: ping 192.168.214.10',
                    'Press Enter and observe results',
                    'Note the reply times and packet loss',
                    'Try continuous ping: ping -t 192.168.214.10',
                    'Stop with Ctrl+C after 10-15 packets'
                ],
                'required': True,
                'screenshot_required': True
            },
            {
                'name': 'Advanced Ping Parameters',
                'description': 'Use ping with different parameters',
                'instructions': [
                    'Large packet test: ping -l 1400 192.168.214.10',
                    'Specific count: ping -n 10 192.168.214.10',
                    'Set timeout: ping -w 5000 192.168.214.10',
                    'Don\'t fragment: ping -f -l 1472 192.168.214.10'
                ],
                'required': True,
                'screenshot_required': True
            },
            {
                'name': 'Traceroute Analysis',
                'description': 'Trace network path to external server',
                'instructions': [
                    'Type: tracert google.com',
                    'Observe each hop in the path',
                    'Note response times for each hop',
                    'Try: tracert -h 15 8.8.8.8 (limit hops)'
                ],
                'required': True,
                'screenshot_required': True
            },
            {
                'name': 'DNS Lookup Testing',
                'description': 'Perform DNS resolution tests',
                'instructions': [
                    'Type: nslookup google.com',
                    'Note the DNS server used',
                    'Try reverse lookup: nslookup 8.8.8.8',
                    'Set specific DNS server: nslookup google.com 8.8.8.8'
                ],
                'required': True,
                'screenshot_required': True
            },
            {
                'name': 'Network Configuration Check',
                'description': 'Check local network configuration',
                'instructions': [
                    'Type: ipconfig /all',
                    'Note IP address, subnet mask, gateway',
                    'Check DNS servers',
                    'Type: ipconfig /release then ipconfig /renew',
                    'Verify configuration after renewal'
                ],
                'required': True,
                'screenshot_required': True
            },
            {
                'name': 'Network Troubleshooting Scenario',
                'description': 'Complete troubleshooting workflow',
                'instructions': [
                    'Test local connectivity: ping 127.0.0.1',
                    'Test gateway: ping [gateway-ip]',
                    'Test external: ping 8.8.8.8',
                    'Test DNS: ping google.com',
                    'Document results and identify any issues'
                ],
                'required': True,
                'screenshot_required': True
            }
        ]

class IPConfigurationModule(TrainingModule):
    """IP Address Configuration training module"""
    
    def get_learning_objectives(self) -> List[str]:
        return [
            "Understand Broetje network architecture",
            "Configure static IP addresses",
            "Set appropriate subnet masks",
            "Configure gateway and DNS settings",
            "Understand network segmentation",
            "Verify network connectivity"
        ]
    
    def get_tasks(self) -> List[Dict]:
        return [
            {
                'name': 'Understand Network Ranges',
                'description': 'Learn about Broetje network segmentation',
                'instructions': [
                    'Production Network: 192.168.214.x',
                    'Engineering Network: 192.168.213.x',
                    'Management Network: 192.168.1.x',
                    'Note the purpose of each network',
                    'Identify which devices belong where'
                ],
                'required': True,
                'screenshot_required': False
            },
            {
                'name': 'Access Network Adapter Settings',
                'description': 'Navigate to network configuration',
                'instructions': [
                    'Right-click network icon in system tray',
                    'Select "Open Network & Internet settings"',
                    'Click "Change adapter options"',
                    'Right-click active network adapter',
                    'Select "Properties"'
                ],
                'required': True,
                'screenshot_required': True
            },
            {
                'name': 'Configure Production Network IP',
                'description': 'Set static IP for production network',
                'instructions': [
                    'Select "Internet Protocol Version 4 (TCP/IPv4)"',
                    'Click "Properties"',
                    'Select "Use the following IP address"',
                    'IP: 192.168.214.[your-number] (e.g., 192.168.214.100)',
                    'Subnet mask: 255.255.255.0',
                    'Gateway: 192.168.214.1'
                ],
                'required': True,
                'screenshot_required': True
            },
            {
                'name': 'Configure DNS Settings',
                'description': 'Set DNS servers for the network',
                'instructions': [
                    'Select "Use the following DNS server addresses"',
                    'Preferred DNS: 192.168.214.10',
                    'Alternate DNS: 8.8.8.8',
                    'Click "Advanced..." for additional DNS',
                    'Click "OK" to save settings'
                ],
                'required': True,
                'screenshot_required': True
            },
            {
                'name': 'Verify IP Configuration',
                'description': 'Confirm network settings are applied',
                'instructions': [
                    'Open Command Prompt',
                    'Type: ipconfig /all',
                    'Verify IP address matches configuration',
                    'Check subnet mask and gateway',
                    'Confirm DNS servers are correct'
                ],
                'required': True,
                'screenshot_required': True
            },
            {
                'name': 'Test Network Connectivity',
                'description': 'Verify network communication',
                'instructions': [
                    'Ping gateway: ping 192.168.214.1',
                    'Ping production server: ping 192.168.214.10',
                    'Ping engineering network: ping 192.168.213.10',
                    'Test internet: ping google.com',
                    'Document any failed connections'
                ],
                'required': True,
                'screenshot_required': True
            },
            {
                'name': 'Configure Alternative Network',
                'description': 'Set up engineering network access',
                'instructions': [
                    'Create new network profile',
                    'Configure IP: 192.168.213.[your-number]',
                    'Subnet: 255.255.255.0',
                    'Gateway: 192.168.213.1',
                    'Test connectivity to both networks'
                ],
                'required': False,
                'screenshot_required': True
            }
        ]

class HardDriveManagementModule(TrainingModule):
    """Hard Drive Management training module"""
    
    def get_learning_objectives(self) -> List[str]:
        return [
            "Use Disk Management utility effectively",
            "Create and manage disk partitions",
            "Understand file system types",
            "Monitor disk health and performance",
            "Manage disk space efficiently",
            "Configure disk quotas and permissions"
        ]
    
    def get_tasks(self) -> List[Dict]:
        return [
            {
                'name': 'Open Disk Management',
                'description': 'Access Windows Disk Management utility',
                'instructions': [
                    'Right-click "This PC" on desktop',
                    'Select "Manage"',
                    'In Computer Management, click "Disk Management"',
                    'Wait for disk scan to complete',
                    'Observe current disk layout'
                ],
                'required': True,
                'screenshot_required': True
            },
            {
                'name': 'Analyze Current Disk Setup',
                'description': 'Review existing disk configuration',
                'instructions': [
                    'Identify system disk (usually Disk 0)',
                    'Note partition layout (System, C:, Recovery)',
                    'Check available free space',
                    'Identify any unallocated space',
                    'Note disk sizes and types (SSD/HDD)'
                ],
                'required': True,
                'screenshot_required': True
            },
            {
                'name': 'Check Disk Properties',
                'description': 'Examine disk properties and health',
                'instructions': [
                    'Right-click on C: drive',
                    'Select "Properties"',
                    'Review used/free space',
                    'Click "Tools" tab',
                    'Note disk check and optimization options'
                ],
                'required': True,
                'screenshot_required': True
            },
            {
                'name': 'Create New Partition (if space available)',
                'description': 'Create partition from unallocated space',
                'instructions': [
                    'Right-click unallocated space (if available)',
                    'Select "New Simple Volume"',
                    'Follow New Simple Volume Wizard',
                    'Set size (e.g., 10 GB for test)',
                    'Assign drive letter (e.g., D:)',
                    'Format as NTFS with volume label'
                ],
                'required': False,
                'screenshot_required': True
            },
            {
                'name': 'Disk Cleanup Operation',
                'description': 'Clean up unnecessary files',
                'instructions': [
                    'Right-click C: drive, select Properties',
                    'Click "Disk Cleanup" button',
                    'Select file types to delete',
                    'Click "Clean up system files"',
                    'Review additional cleanup options',
                    'Execute cleanup (if instructor approves)'
                ],
                'required': True,
                'screenshot_required': True
            },
            {
                'name': 'Check Disk Errors',
                'description': 'Scan for and fix disk errors',
                'instructions': [
                    'Go to C: Properties > Tools',
                    'Click "Check" under Error checking',
                    'Select "Scan drive" if prompted',
                    'Wait for scan completion',
                    'Review scan results'
                ],
                'required': True,
                'screenshot_required': True
            },
            {
                'name': 'Disk Defragmentation',
                'description': 'Optimize disk performance',
                'instructions': [
                    'In Tools tab, click "Optimize"',
                    'Select C: drive',
                    'Click "Analyze" to check fragmentation',
                    'Review fragmentation percentage',
                    'Click "Optimize" if needed (instructor permission)'
                ],
                'required': True,
                'screenshot_required': True
            }
        ]

class BackupRestoreModule(TrainingModule):
    """Backup/Restore Operations using Paragon training module"""
    
    def get_learning_objectives(self) -> List[str]:
        return [
            "Understand backup vs. imaging concepts",
            "Use Paragon software for system backup",
            "Create and manage backup schedules",
            "Perform system restore operations",
            "Verify backup integrity",
            "Follow Broetje backup naming conventions"
        ]
    
    def get_tasks(self) -> List[Dict]:
        return [
            {
                'name': 'Launch Paragon Backup Software',
                'description': 'Start Paragon Backup & Recovery',
                'instructions': [
                    'Double-click Paragon Backup icon on desktop',
                    'Wait for application to load',
                    'Review main interface layout',
                    'Note available backup and restore options'
                ],
                'required': True,
                'screenshot_required': True
            },
            {
                'name': 'Create System Backup',
                'description': 'Backup system partition',
                'instructions': [
                    'Click "Backup" in main menu',
                    'Select "System Backup" option',
                    'Choose source (System partition)',
                    'Set destination (external drive or network)',
                    'Use naming: Machine#_Initials_System_YYYYMMDD'
                ],
                'required': True,
                'screenshot_required': True
            },
            {
                'name': 'Configure Backup Settings',
                'description': 'Set backup parameters and options',
                'instructions': [
                    'Select compression level (Medium recommended)',
                    'Choose encryption if required',
                    'Set backup validation options',
                    'Configure post-backup actions',
                    'Review all settings before proceeding'
                ],
                'required': True,
                'screenshot_required': True
            },
            {
                'name': 'Execute Backup Process',
                'description': 'Run the backup operation',
                'instructions': [
                    'Click "Start Backup" to begin',
                    'Monitor progress and estimated time',
                    'Do not interrupt the process',
                    'Wait for completion confirmation',
                    'Review backup log for any errors'
                ],
                'required': True,
                'screenshot_required': True
            },
            {
                'name': 'Verify Backup Integrity',
                'description': 'Confirm backup was successful',
                'instructions': [
                    'Navigate to backup destination',
                    'Check file size matches expectation',
                    'Use Paragon "Verify Backup" function',
                    'Review verification results',
                    'Document backup details'
                ],
                'required': True,
                'screenshot_required': True
            },
            {
                'name': 'Create Data Backup',
                'description': 'Backup user data and documents',
                'instructions': [
                    'Select "File Backup" option',
                    'Choose specific folders (Documents, Desktop)',
                    'Set destination with naming convention',
                    'Configure incremental backup settings',
                    'Schedule automatic backups if needed'
                ],
                'required': True,
                'screenshot_required': True
            },
            {
                'name': 'Restore Test File',
                'description': 'Practice file restoration',
                'instructions': [
                    'Create a test file on desktop',
                    'Delete the test file',
                    'Use Paragon "Restore" function',
                    'Navigate to backup containing the file',
                    'Restore file to original location',
                    'Verify file restoration success'
                ],
                'required': True,
                'screenshot_required': True
            },
            {
                'name': 'Schedule Automatic Backup',
                'description': 'Set up scheduled backup tasks',
                'instructions': [
                    'Access Paragon Scheduler',
                    'Create new backup task',
                    'Set daily backup at non-work hours',
                    'Configure retention policy',
                    'Test scheduled task execution'
                ],
                'required': False,
                'screenshot_required': True
            }
        ]

class PowerShellScriptingModule(TrainingModule):
    """PowerShell Scripting training module"""
    
    def get_learning_objectives(self) -> List[str]:
        return [
            "Understand PowerShell vs Command Prompt",
            "Work with PowerShell cmdlets and syntax",
            "Create and execute PowerShell scripts",
            "Use PowerShell for system administration",
            "Handle PowerShell objects and pipelines",
            "Implement error handling and logging"
        ]
    
    def get_tasks(self) -> List[Dict]:
        return [
            {
                'name': 'Open PowerShell ISE',
                'description': 'Launch PowerShell Integrated Scripting Environment',
                'instructions': [
                    'Press Windows key + R',
                    'Type "powershell_ise" and press Enter',
                    'Click "Yes" if prompted for elevation',
                    'Familiarize yourself with the interface',
                    'Note script pane, command pane, and output'
                ],
                'required': True,
                'screenshot_required': True
            },
            {
                'name': 'Basic PowerShell Commands',
                'description': 'Execute fundamental PowerShell cmdlets',
                'instructions': [
                    'Type: Get-Process',
                    'Type: Get-Service',
                    'Type: Get-ChildItem C:\\',
                    'Type: Get-Help Get-Process',
                    'Observe object-based output'
                ],
                'required': True,
                'screenshot_required': True
            },
            {
                'name': 'Working with Variables',
                'description': 'Create and manipulate PowerShell variables',
                'instructions': [
                    'Create variable: $name = "Broetje"',
                    'Display variable: Write-Host $name',
                    'Create array: $numbers = 1,2,3,4,5',
                    'Access array element: $numbers[0]',
                    'Get variable type: $name.GetType()'
                ],
                'required': True,
                'screenshot_required': True
            },
            {
                'name': 'PowerShell Pipelines',
                'description': 'Use pipes to combine commands',
                'instructions': [
                    'Get-Process | Where-Object {$_.CPU -gt 100}',
                    'Get-ChildItem C:\\ | Sort-Object Name',
                    'Get-Service | Select-Object Name,Status',
                    'Get-EventLog System | Select-Object -First 5'
                ],
                'required': True,
                'screenshot_required': True
            },
            {
                'name': 'Create System Info Script',
                'description': 'Write a script to gather system information',
                'instructions': [
                    'Create new script file',
                    'Get computer name, OS version, memory',
                    'Get disk space information',
                    'Export results to CSV file',
                    'Add date/time stamp'
                ],
                'required': True,
                'screenshot_required': True
            },
            {
                'name': 'Network Monitoring Script',
                'description': 'Create script for network monitoring',
                'instructions': [
                    'Write script to ping multiple servers',
                    'Check if servers are responsive',
                    'Log results with timestamps',
                    'Send email alert for failures',
                    'Schedule script to run automatically'
                ],
                'required': True,
                'screenshot_required': True
            },
            {
                'name': 'Error Handling and Logging',
                'description': 'Implement robust error handling',
                'instructions': [
                    'Use Try-Catch-Finally blocks',
                    'Write errors to log file',
                    'Create detailed error messages',
                    'Test error scenarios',
                    'Implement proper cleanup'
                ],
                'required': True,
                'screenshot_required': True
            },
            {
                'name': 'Advanced Script Features',
                'description': 'Use advanced PowerShell capabilities',
                'instructions': [
                    'Create PowerShell functions',
                    'Use parameters and validation',
                    'Implement command-line arguments',
                    'Create PowerShell modules',
                    'Use PowerShell remoting'
                ],
                'required': False,
                'screenshot_required': True
            }
        ]

# Update the module registry
from training_modules import MODULE_REGISTRY

MODULE_REGISTRY.update({
    'Command Line Network Diagnostics': CommandLineDiagnosticsModule,
    'IP Address Configuration': IPConfigurationModule,
    'Hard Drive Management': HardDriveManagementModule,
    'Backup/Restore Operations': BackupRestoreModule,
    'PowerShell Scripting': PowerShellScriptingModule,
})