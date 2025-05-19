#!/usr/bin/env python3
"""
PowerShell Scripting Training Module
Interactive module for teaching advanced PowerShell scripting
"""

import os
import subprocess
from datetime import datetime
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QLineEdit, QMessageBox, QGroupBox, QCheckBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QRadioButton, QButtonGroup, QSpinBox, QListWidget,
    QListWidgetItem, QFileDialog
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QTextCharFormat, QTextCursor, QColor
from training_module import TrainingModule

class PowerShellScriptingModule(TrainingModule):
    """PowerShell Scripting Training Module"""
    
    def __init__(self, module_data, user_data, db_manager=None):
        self.db_manager = db_manager
        self.script_outputs = {}
        self.created_scripts = []
        self.cmdlet_history = []
        super().__init__(module_data, user_data)
        
    def get_learning_objectives(self) -> list:
        return [
            "Write PowerShell scripts for automation",
            "Use PowerShell cmdlets effectively", 
            "Create maintenance scripts",
            "Automate routine tasks"
        ]
    
    def get_tasks(self) -> list:
        return self.module_data.get('tasks', [])
    
    # Remove custom setup_overview_tab - it's causing issues
        
    def setup_custom_ui(self, parent):
        """Setup module-specific UI elements"""
        layout = QVBoxLayout(parent)
        
        # PowerShell Console section
        console_group = QGroupBox("PowerShell Console")
        console_layout = QVBoxLayout()
        
        # Command input
        command_layout = QHBoxLayout()
        command_layout.addWidget(QLabel("PS> "))
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Enter PowerShell command here...")
        self.command_input.returnPressed.connect(self.execute_command)
        command_layout.addWidget(self.command_input)
        
        execute_button = QPushButton("Execute")
        execute_button.clicked.connect(self.execute_command)
        command_layout.addWidget(execute_button)
        console_layout.addLayout(command_layout)
        
        # Console output
        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)
        self.console_output.setFont(QFont("Consolas", 10))
        self.console_output.setStyleSheet("background-color: #012456; color: #F0F0F0;")
        console_layout.addWidget(self.console_output)
        
        # Clear console button
        clear_button = QPushButton("Clear Console")
        clear_button.clicked.connect(lambda: self.console_output.clear())
        console_layout.addWidget(clear_button)
        
        console_group.setLayout(console_layout)
        layout.addWidget(console_group)
        
        # Script Editor section
        editor_group = QGroupBox("Script Editor")
        editor_layout = QVBoxLayout()
        
        # Script name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Script Name:"))
        self.script_name_input = QLineEdit()
        self.script_name_input.setPlaceholderText("e.g., OpenHelloWorld.ps1")
        name_layout.addWidget(self.script_name_input)
        editor_layout.addLayout(name_layout)
        
        # Script editor
        self.script_editor = QTextEdit()
        self.script_editor.setFont(QFont("Consolas", 10))
        self.script_editor.setPlaceholderText(
            "# PowerShell Script\n"
            "# Clear screen\n"
            "Clear-Host\n\n"
            "# Your code here...\n"
        )
        editor_layout.addWidget(self.script_editor)
        
        # Editor buttons
        editor_buttons = QHBoxLayout()
        
        save_script_button = QPushButton("Save Script")
        save_script_button.clicked.connect(self.save_script)
        editor_buttons.addWidget(save_script_button)
        
        run_script_button = QPushButton("Run Script")
        run_script_button.clicked.connect(self.run_current_script)
        editor_buttons.addWidget(run_script_button)
        
        load_template_button = QPushButton("Load Template")
        load_template_button.clicked.connect(self.load_script_template)
        editor_buttons.addWidget(load_template_button)
        
        editor_layout.addLayout(editor_buttons)
        
        editor_group.setLayout(editor_layout)
        layout.addWidget(editor_group)
        
        # Script Templates section
        templates_group = QGroupBox("Script Templates")
        templates_layout = QVBoxLayout()
        
        template_combo = QComboBox()
        template_combo.addItems([
            "Basic Hello World Script",
            "Network Diagnostic Script",
            "Backup Management Script",
            "File Transfer Script",
            "Startup Automation Script"
        ])
        templates_layout.addWidget(template_combo)
        
        insert_template_button = QPushButton("Insert Template")
        insert_template_button.clicked.connect(
            lambda: self.insert_template(template_combo.currentText())
        )
        templates_layout.addWidget(insert_template_button)
        
        templates_group.setLayout(templates_layout)
        layout.addWidget(templates_group)
        
        # Cmdlet Reference section
        cmdlet_group = QGroupBox("Common Cmdlets")
        cmdlet_layout = QVBoxLayout()
        
        self.cmdlet_list = QListWidget()
        cmdlets = [
            "Get-Help - Get help for cmdlets",
            "Get-Command - List available commands",
            "Get-ChildItem - List directory contents",
            "Set-Location - Change directory",
            "Test-Connection - Ping network device",
            "Get-NetAdapter - Show network adapters",
            "New-Item - Create file/folder",
            "Copy-Item - Copy files",
            "Remove-Item - Delete files",
            "Start-Process - Launch programs"
        ]
        self.cmdlet_list.addItems(cmdlets)
        self.cmdlet_list.itemDoubleClicked.connect(self.insert_cmdlet)
        cmdlet_layout.addWidget(self.cmdlet_list)
        
        cmdlet_help_button = QPushButton("Get Help for Selected")
        cmdlet_help_button.clicked.connect(self.get_cmdlet_help)
        cmdlet_layout.addWidget(cmdlet_help_button)
        
        cmdlet_group.setLayout(cmdlet_layout)
        layout.addWidget(cmdlet_group)
        
        # Broetje-specific section
        broetje_group = QGroupBox("Broetje Network Devices")
        broetje_layout = QVBoxLayout()
        
        self.device_table = QTableWidget()
        self.device_table.setColumnCount(3)
        self.device_table.setHorizontalHeaderLabels(["Device", "IP Address", "Status"])
        
        # Add Broetje devices
        devices = [
            ("NCU Controller", "192.168.214.1"),
            ("Service PC", "192.168.214.34"),
            ("Operator PC", "192.168.214.35"),
            ("Scale PC", "192.168.214.37"),
            ("Riveter PC", "192.168.214.60"),
            ("RTX System", "192.168.213.33")
        ]
        
        for i, (device, ip) in enumerate(devices):
            self.device_table.insertRow(i)
            self.device_table.setItem(i, 0, QTableWidgetItem(device))
            self.device_table.setItem(i, 1, QTableWidgetItem(ip))
            self.device_table.setItem(i, 2, QTableWidgetItem("Unknown"))
        
        broetje_layout.addWidget(self.device_table)
        
        test_devices_button = QPushButton("Test All Devices")
        test_devices_button.clicked.connect(self.test_all_devices)
        broetje_layout.addWidget(test_devices_button)
        
        broetje_group.setLayout(broetje_layout)
        layout.addWidget(broetje_group)
        
        # Script Management section
        management_group = QGroupBox("Script Management")
        management_layout = QVBoxLayout()
        
        self.scripts_list = QListWidget()
        management_layout.addWidget(QLabel("Created Scripts:"))
        management_layout.addWidget(self.scripts_list)
        
        script_buttons_layout = QHBoxLayout()
        
        schedule_button = QPushButton("Schedule Script")
        schedule_button.clicked.connect(self.schedule_script)
        script_buttons_layout.addWidget(schedule_button)
        
        export_button = QPushButton("Export Scripts")
        export_button.clicked.connect(self.export_scripts)
        script_buttons_layout.addWidget(export_button)
        
        management_layout.addLayout(script_buttons_layout)
        
        management_group.setLayout(management_layout)
        layout.addWidget(management_group)
    
    def execute_command(self):
        """Execute PowerShell command"""
        command = self.command_input.text().strip()
        if not command:
            return
        
        # Add to history
        self.cmdlet_history.append(command)
        
        # Display command
        self.console_output.append(f"PS> {command}")
        
        # Simulate command execution
        try:
            if command.lower().startswith("get-help"):
                self.show_help_output(command)
            elif command.lower().startswith("test-connection"):
                self.simulate_test_connection(command)
            elif command.lower() == "get-location":
                self.console_output.append("Path\n----\nD:\\Temp\\YourInitials\\PowerShellScripts")
            elif command.lower() == "get-childitem":
                self.simulate_dir_listing()
            else:
                # Generic command simulation
                self.console_output.append(f"Executing: {command}")
                self.console_output.append("Command completed successfully.")
            
            self.task_widgets.get("powershell_basics").set_completed(True)
            
        except Exception as e:
            self.console_output.append(f"Error: {str(e)}")
        
        self.command_input.clear()
        self.console_output.append("")
    
    def show_help_output(self, command):
        """Show help output for cmdlet"""
        parts = command.split()
        if len(parts) > 1:
            cmdlet = parts[1]
            help_text = f"""
NAME
    {cmdlet}

SYNOPSIS
    Gets help information for PowerShell cmdlets

SYNTAX
    {cmdlet} [[-Name] <String>] [-Full] [-Examples]

DESCRIPTION
    The {cmdlet} cmdlet displays information about PowerShell concepts and commands.

EXAMPLES
    {cmdlet} Get-Process
    {cmdlet} Get-Process -Full
            """
            self.console_output.append(help_text)
    
    def simulate_test_connection(self, command):
        """Simulate Test-Connection output"""
        import re
        match = re.search(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', command)
        
        if match:
            ip = match.group()
            output = f"""
Source        Destination     IPV4Address      IPV6Address                              Bytes    Time(ms)
------        -----------     -----------      -----------                              -----    --------
LOCALHOST     {ip}      {ip}                                               32       1       
LOCALHOST     {ip}      {ip}                                               32       1       
LOCALHOST     {ip}      {ip}                                               32       1       
LOCALHOST     {ip}      {ip}                                               32       1       
            """
            self.console_output.append(output)
    
    def simulate_dir_listing(self):
        """Simulate directory listing"""
        output = """
    Directory: D:\\Temp\\YourInitials\\PowerShellScripts

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a----         1/19/2025   2:30 PM            250 OpenHelloWorld.ps1
-a----         1/19/2025   2:45 PM            512 NetworkDiagnostic.ps1
-a----         1/19/2025   3:00 PM             42 Hello_World.txt
        """
        self.console_output.append(output)
    
    def save_script(self):
        """Save current script"""
        script_name = self.script_name_input.text().strip()
        if not script_name:
            QMessageBox.warning(self, "No Script Name", 
                              "Please enter a script name.")
            return
        
        if not script_name.endswith('.ps1'):
            script_name += '.ps1'
        
        script_content = self.script_editor.toPlainText()
        
        # Save to virtual environment
        self.script_outputs[script_name] = script_content
        self.created_scripts.append(script_name)
        
        # Update scripts list
        self.scripts_list.clear()
        self.scripts_list.addItems(self.created_scripts)
        
        # Mark task complete based on script name
        if "OpenHelloWorld" in script_name:
            self.task_widgets.get("create_directory_script").set_completed(True)
        elif "NetworkDiagnostic" in script_name:
            self.task_widgets.get("network_diagnostic_script").set_completed(True)
        elif "Backup" in script_name:
            self.task_widgets.get("backup_management_script").set_completed(True)
        elif "Startup" in script_name:
            self.task_widgets.get("startup_automation").set_completed(True)
        
        QMessageBox.information(self, "Script Saved", 
                              f"Script '{script_name}' has been saved.")
    
    def run_current_script(self):
        """Run the current script in the editor"""
        script_content = self.script_editor.toPlainText()
        
        if not script_content.strip():
            QMessageBox.warning(self, "Empty Script", 
                              "Please write a script before running.")
            return
        
        self.console_output.append("\n=== Running Script ===\n")
        
        # Simulate script execution based on content
        if "Hello_World.txt" in script_content:
            self.console_output.append("Opening Hello World file...")
            self.console_output.append("File opened successfully!")
        elif "Test-Connection" in script_content:
            self.console_output.append("Testing connectivity to Broetje devices...")
            self.test_all_devices()
        elif "New-BroetjeBackup" in script_content:
            self.console_output.append("Creating backup: AP1741_R1_NC_20250119")
            self.console_output.append("Backup completed successfully.")
        else:
            self.console_output.append("Script executed successfully.")
        
        self.console_output.append("\n=== Script Complete ===\n")
    
    def load_script_template(self):
        """Load a script template"""
        templates = {
            "Basic": self.get_basic_template(),
            "Network": self.get_network_template(),
            "Backup": self.get_backup_template(),
            "Startup": self.get_startup_template()
        }
        
        # For demonstration, load the basic template
        self.script_editor.setText(self.get_basic_template())
    
    def insert_template(self, template_name):
        """Insert selected template"""
        if "Hello World" in template_name:
            self.script_editor.setText(self.get_basic_template())
        elif "Network Diagnostic" in template_name:
            self.script_editor.setText(self.get_network_template())
        elif "Backup Management" in template_name:
            self.script_editor.setText(self.get_backup_template())
        elif "File Transfer" in template_name:
            self.script_editor.setText(self.get_file_transfer_template())
        elif "Startup" in template_name:
            self.script_editor.setText(self.get_startup_template())
    
    def get_basic_template(self):
        """Get basic PowerShell template"""
        return """# OpenHelloWorld.ps1
# Clear screen
Clear-Host

# Display message
Write-Host "Opening Hello World file..." -ForegroundColor Green

# Define file path
$filePath = "D:\\Temp\\$env:USERNAME\\PowerShellScripts\\Hello_World.txt"

# Check if file exists
if (Test-Path $filePath) {
    # Open file in Notepad
    Start-Process notepad.exe -ArgumentList $filePath
    Write-Host "File opened successfully!" -ForegroundColor Green
} else {
    Write-Host "File not found: $filePath" -ForegroundColor Red
}

# Pause for user input
Read-Host "Press Enter to exit"
"""
    
    def get_network_template(self):
        """Get network diagnostic template"""
        return """# Broetje-NetworkDiagnostics.ps1
param(
    [string]$OutputPath = "D:\\Temp\\$env:USERNAME\\NetworkDiagnostics.txt"
)

# Define Broetje network devices
$broetjeDevices = @{
    "NCU Controller" = "192.168.214.1"
    "Service PC" = "192.168.214.34"
    "Operator PC" = "192.168.214.35"
    "Scale PC (Vision)" = "192.168.214.37"
    "Riveter PC" = "192.168.214.60"
    "RTX System" = "192.168.213.33"
}

# Initialize report
$report = @()
$report += "=================================="
$report += "Broetje Network Diagnostic Report"
$report += "Date: $(Get-Date)"
$report += "=================================="

# Test each device
foreach ($device in $broetjeDevices.GetEnumerator()) {
    Write-Host "Testing $($device.Key)..." -ForegroundColor Yellow
    
    try {
        $ping = Test-Connection -ComputerName $device.Value -Count 1 -ErrorAction Stop
        $status = "ONLINE"
        $responseTime = "$($ping.ResponseTime)ms"
        $color = "Green"
    }
    catch {
        $status = "OFFLINE"
        $responseTime = "N/A"
        $color = "Red"
    }
    
    $line = "$($device.Key.PadRight(20)) $($device.Value.PadRight(15)) $status $responseTime"
    $report += $line
    Write-Host $line -ForegroundColor $color
}

# Save report
$report | Out-File -FilePath $OutputPath -Encoding utf8
Write-Host "`nReport saved to: $OutputPath" -ForegroundColor Cyan

# Open report
Start-Process notepad.exe -ArgumentList $OutputPath
"""
    
    def get_backup_template(self):
        """Get backup management template"""
        return """# Broetje-BackupManager.ps1
function New-BroetjeBackup {
    param(
        [Parameter(Mandatory)]
        [string]$MachineNumber,
        
        [Parameter(Mandatory)]
        [string]$MachineInitials,
        
        [Parameter(Mandatory)]
        [ValidateSet('NC','DD','HMI','PLC','S7')]
        [string]$BackupType,
        
        [string]$SourcePath = "C:\\Data",
        [string]$DestinationPath = "\\\\server\\backups"
    )
    
    # Generate backup filename
    $date = Get-Date -Format "yyyyMMdd"
    $backupName = "${MachineNumber}_${MachineInitials}_${BackupType}_${date}"
    
    # Create destination directory
    $destDir = Join-Path $DestinationPath $MachineNumber
    if (!(Test-Path $destDir)) {
        New-Item -Path $destDir -ItemType Directory -Force
    }
    
    # Define backup destination
    $destFile = Join-Path $destDir "${backupName}.zip"
    
    Write-Host "Creating backup: $backupName" -ForegroundColor Green
    
    try {
        # Compress source to destination
        Compress-Archive -Path $SourcePath -DestinationPath $destFile -Force
        
        Write-Host "Backup completed: $destFile" -ForegroundColor Green
        return $destFile
    }
    catch {
        Write-Host "Backup failed: $_" -ForegroundColor Red
        return $null
    }
}

# Example usage
New-BroetjeBackup -MachineNumber "AP1741" -MachineInitials "R1" -BackupType "NC"
"""
    
    def get_file_transfer_template(self):
        """Get file transfer template"""
        return """# Broetje-FileTransfer.ps1
function Copy-ToMachine {
    param(
        [Parameter(Mandatory)]
        [string]$SourceFile,
        
        [Parameter(Mandatory)]
        [string]$TargetIP,
        
        [string]$RemotePath = "C:\\Temp",
        [PSCredential]$Credential
    )
    
    Write-Host "Transferring file to $TargetIP..." -ForegroundColor Cyan
    
    try {
        # Test network connectivity
        if (!(Test-Connection -ComputerName $TargetIP -Count 1 -Quiet)) {
            throw "Cannot reach target machine: $TargetIP"
        }
        
        # Build UNC path
        $uncPath = "\\\\$TargetIP\\$(($RemotePath).Replace(':', '$'))"
        
        # Copy file
        Copy-Item -Path $SourceFile -Destination $uncPath -Force
        
        Write-Host "File transferred successfully!" -ForegroundColor Green
    }
    catch {
        Write-Host "Transfer failed: $_" -ForegroundColor Red
    }
}

# Example usage
Copy-ToMachine -SourceFile "D:\\Temp\\test.txt" -TargetIP "192.168.214.35"
"""
    
    def get_startup_template(self):
        """Get startup script template"""
        return """# Startup-BroetjeTasks.ps1
# This runs when user logs in

# Set up logging
$logFile = "D:\\Temp\\$env:USERNAME\\startup_log.txt"
Add-Content $logFile "$(Get-Date): Startup script initiated"

# Wait for network
Start-Sleep -Seconds 5

# Test critical connections
$criticalIPs = @("192.168.214.1", "192.168.214.34", "192.168.214.60")
foreach ($ip in $criticalIPs) {
    if (Test-Connection -ComputerName $ip -Count 1 -Quiet) {
        Add-Content $logFile "$(Get-Date): $ip - ONLINE"
    } else {
        Add-Content $logFile "$(Get-Date): $ip - OFFLINE"
    }
}

# Open Hello World file
$helloFile = "D:\\Temp\\$env:USERNAME\\PowerShellScripts\\Hello_World.txt"
if (Test-Path $helloFile) {
    Start-Process notepad.exe -ArgumentList $helloFile
    Add-Content $logFile "$(Get-Date): Opened Hello World file"
}

Add-Content $logFile "$(Get-Date): Startup script completed"
"""
    
    def insert_cmdlet(self, item):
        """Insert cmdlet into console"""
        cmdlet = item.text().split(' - ')[0]
        self.command_input.setText(cmdlet)
    
    def get_cmdlet_help(self):
        """Get help for selected cmdlet"""
        current_item = self.cmdlet_list.currentItem()
        if current_item:
            cmdlet = current_item.text().split(' - ')[0]
            self.command_input.setText(f"Get-Help {cmdlet}")
            self.execute_command()
    
    def test_all_devices(self):
        """Test all Broetje devices"""
        self.console_output.append("\nTesting all Broetje devices...\n")
        
        for row in range(self.device_table.rowCount()):
            device = self.device_table.item(row, 0).text()
            ip = self.device_table.item(row, 1).text()
            
            # Simulate test
            import random
            success = random.choice([True, True, True, False])  # 75% success rate
            
            if success:
                status = "Online"
                color = Qt.green
                self.console_output.append(f"{device} ({ip}) - ONLINE (1ms)")
            else:
                status = "Offline"
                color = Qt.red
                self.console_output.append(f"{device} ({ip}) - OFFLINE")
            
            status_item = QTableWidgetItem(status)
            status_item.setForeground(color)
            self.device_table.setItem(row, 2, status_item)
        
        self.console_output.append("\nDevice testing complete.\n")
    
    def schedule_script(self):
        """Schedule selected script"""
        current_item = self.scripts_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Script Selected", 
                              "Please select a script to schedule.")
            return
        
        script_name = current_item.text()
        
        # Simulate scheduling
        schedule_cmd = f"""
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-File '{script_name}'"
$trigger = New-ScheduledTaskTrigger -AtLogOn
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries

Register-ScheduledTask -TaskName "BroetjeStartup" -Action $action -Trigger $trigger -Principal $principal -Settings $settings
"""
        
        self.console_output.append("\n=== Scheduling Script ===")
        self.console_output.append(schedule_cmd)
        self.console_output.append("Task scheduled successfully.\n")
        
        QMessageBox.information(self, "Script Scheduled", 
                              f"Script '{script_name}' has been scheduled to run at logon.")
    
    def export_scripts(self):
        """Export all created scripts"""
        if not self.created_scripts:
            QMessageBox.warning(self, "No Scripts", 
                              "No scripts to export.")
            return
        
        export_dir = QFileDialog.getExistingDirectory(
            self, "Select Export Directory"
        )
        
        if export_dir:
            for script_name in self.created_scripts:
                script_content = self.script_outputs.get(script_name, "")
                
                # Simulate export
                self.console_output.append(f"Exported: {script_name} to {export_dir}")
            
            QMessageBox.information(self, "Export Complete", 
                                  f"Exported {len(self.created_scripts)} scripts to {export_dir}")
    
    def validate_task(self, task_id: str) -> bool:
        """Validate specific task completion"""
        if task_id == "powershell_basics":
            # Check if basic commands were executed
            return len(self.cmdlet_history) >= 3
        
        elif task_id == "create_directory_script":
            # Check if OpenHelloWorld script was created
            return any("OpenHelloWorld" in script for script in self.created_scripts)
        
        elif task_id == "network_diagnostic_script":
            # Check if network diagnostic script was created
            return any("NetworkDiagnostic" in script for script in self.created_scripts)
        
        elif task_id == "backup_management_script":
            # Check if backup script was created
            return any("Backup" in script for script in self.created_scripts)
        
        elif task_id == "startup_automation":
            # Check if startup script was created and scheduled
            return any("Startup" in script for script in self.created_scripts)
        
        return True
    
    def get_additional_resources(self):
        """Get additional resources for this module"""
        return {
            "documents": [
                {
                    "title": "PowerShell Scripting Guide",
                    "path": "resources/powershell_guide.md",
                    "type": "markdown"
                }
            ],
            "links": [
                {
                    "title": "PowerShell Documentation",
                    "url": "https://docs.microsoft.com/en-us/powershell/",
                    "description": "Official Microsoft PowerShell documentation"
                },
                {
                    "title": "PowerShell Gallery",
                    "url": "https://www.powershellgallery.com/",
                    "description": "PowerShell module and script repository"
                }
            ],
            "tips": [
                "Use Get-Help for any cmdlet documentation",
                "Always use try/catch for error handling",
                "Comment your code thoroughly",
                "Test scripts in ISE before deployment",
                "Use approved verbs for functions",
                "Set execution policy appropriately"
            ],
            "common_errors": {
                "Execution Policy": "Run Set-ExecutionPolicy RemoteSigned",
                "Path Not Found": "Use Test-Path before file operations",
                "Access Denied": "Run PowerShell as Administrator",
                "Module Not Found": "Use Import-Module or Install-Module"
            }
        }

# Export the module class
MODULE_CLASS = PowerShellScriptingModule