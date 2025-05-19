#!/usr/bin/env python3
"""
Command Line Interface Diagnostics Training Module
Interactive module for teaching network diagnostic commands
"""

import os
import subprocess
import re
from datetime import datetime
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QLineEdit, QMessageBox, QGroupBox, QCheckBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QSplitter,
    QComboBox, QSpinBox
)
from PySide6.QtCore import Qt, QTimer, Signal, QThread
from PySide6.QtGui import QFont, QColor, QTextCharFormat, QTextCursor
from training_module import TrainingModule

class CommandExecutor(QThread):
    """Thread for executing commands without blocking UI"""
    output_ready = Signal(str)
    error_occurred = Signal(str)
    execution_complete = Signal()
    
    def __init__(self, command):
        super().__init__()
        self.command = command
        
    def run(self):
        try:
            process = subprocess.Popen(
                self.command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Read output in real-time
            for line in process.stdout:
                self.output_ready.emit(line.strip())
            
            # Get any errors
            stderr = process.stderr.read()
            if stderr:
                self.error_occurred.emit(stderr)
            
            process.wait()
            self.execution_complete.emit()
            
        except Exception as e:
            self.error_occurred.emit(str(e))
            self.execution_complete.emit()

class CLIDiagnosticsModule(TrainingModule):
    """Command Line Interface Diagnostics Training Module"""
    
    def __init__(self, module_data, user_data, db_manager=None):
        self.db_manager = db_manager
        self.command_history = []
        self.network_log = []
        super().__init__(module_data, user_data)
        
    def get_learning_objectives(self) -> list:
        return [
            "Master command line interface navigation",
            "Execute network diagnostic commands",
            "Interpret command output for troubleshooting",
            "Verify network connectivity"
        ]
    
    def get_tasks(self) -> list:
        return self.module_data.get('tasks', [])
    
    # Remove the custom setup_overview_tab - it's causing issues
        
    def setup_custom_ui(self, parent):
        """Setup module-specific UI elements"""
        layout = QVBoxLayout(parent)
        
        # Command terminal section
        terminal_group = QGroupBox("Command Terminal")
        terminal_layout = QVBoxLayout()
        
        # Command input
        command_layout = QHBoxLayout()
        command_layout.addWidget(QLabel("Command:"))
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Enter command here (e.g., ping 192.168.214.1)")
        self.command_input.returnPressed.connect(self.execute_command)
        command_layout.addWidget(self.command_input)
        
        self.execute_button = QPushButton("Execute")
        self.execute_button.clicked.connect(self.execute_command)
        command_layout.addWidget(self.execute_button)
        
        terminal_layout.addLayout(command_layout)
        
        # Output display
        self.output_display = QTextEdit()
        self.output_display.setReadOnly(True)
        self.output_display.setFont(QFont("Consolas", 10))
        self.output_display.setStyleSheet("background-color: black; color: white;")
        terminal_layout.addWidget(self.output_display)
        
        terminal_group.setLayout(terminal_layout)
        layout.addWidget(terminal_group)
        
        # Quick commands section
        quick_cmd_group = QGroupBox("Quick Commands")
        quick_cmd_layout = QVBoxLayout()
        
        # Network selection
        network_layout = QHBoxLayout()
        network_layout.addWidget(QLabel("Network:"))
        self.network_combo = QComboBox()
        self.network_combo.addItems([
            "Machine Network (192.168.214.x)",
            "Riveter Network (192.168.213.x)",
            "Video Network (192.168.1.x)"
        ])
        network_layout.addWidget(self.network_combo)
        quick_cmd_layout.addLayout(network_layout)
        
        # Device selection
        device_layout = QHBoxLayout()
        device_layout.addWidget(QLabel("Device:"))
        self.device_combo = QComboBox()
        self.update_device_list()
        self.network_combo.currentChanged.connect(self.update_device_list)
        device_layout.addWidget(self.device_combo)
        quick_cmd_layout.addLayout(device_layout)
        
        # Quick ping button
        ping_button = QPushButton("Ping Selected Device")
        ping_button.clicked.connect(self.quick_ping)
        quick_cmd_layout.addWidget(ping_button)
        
        # Continuous ping option
        continuous_layout = QHBoxLayout()
        self.continuous_check = QCheckBox("Continuous Ping")
        continuous_layout.addWidget(self.continuous_check)
        
        continuous_layout.addWidget(QLabel("Count:"))
        self.ping_count = QSpinBox()
        self.ping_count.setMinimum(1)
        self.ping_count.setMaximum(100)
        self.ping_count.setValue(4)
        continuous_layout.addWidget(self.ping_count)
        continuous_layout.addStretch()
        
        quick_cmd_layout.addLayout(continuous_layout)
        
        # Common commands buttons
        common_buttons_layout = QVBoxLayout()
        
        ipconfig_button = QPushButton("Show IP Configuration")
        ipconfig_button.clicked.connect(lambda: self.run_command("ipconfig /all"))
        common_buttons_layout.addWidget(ipconfig_button)
        
        arp_button = QPushButton("Show ARP Table")
        arp_button.clicked.connect(lambda: self.run_command("arp -a"))
        common_buttons_layout.addWidget(arp_button)
        
        tracert_button = QPushButton("Trace Route to Google")
        tracert_button.clicked.connect(lambda: self.run_command("tracert google.com"))
        common_buttons_layout.addWidget(tracert_button)
        
        quick_cmd_layout.addLayout(common_buttons_layout)
        quick_cmd_group.setLayout(quick_cmd_layout)
        layout.addWidget(quick_cmd_group)
        
        # Network log section
        log_group = QGroupBox("Network Log")
        log_layout = QVBoxLayout()
        
        self.log_table = QTableWidget()
        self.log_table.setColumnCount(6)
        self.log_table.setHorizontalHeaderLabels([
            "Time", "Command", "Target", "Status", "Response Time", "Notes"
        ])
        self.log_table.horizontalHeader().setStretchLastSection(True)
        log_layout.addWidget(self.log_table)
        
        log_buttons_layout = QHBoxLayout()
        save_log_button = QPushButton("Save Log")
        save_log_button.clicked.connect(self.save_network_log)
        log_buttons_layout.addWidget(save_log_button)
        
        clear_log_button = QPushButton("Clear Log")
        clear_log_button.clicked.connect(self.clear_network_log)
        log_buttons_layout.addWidget(clear_log_button)
        
        log_buttons_layout.addStretch()
        log_layout.addLayout(log_buttons_layout)
        
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
    def update_device_list(self):
        """Update device combo box based on selected network"""
        self.device_combo.clear()
        
        network = self.network_combo.currentText()
        if "192.168.214" in network:
            devices = [
                "192.168.214.1 (NCU Controller)",
                "192.168.214.34 (Service PC)",
                "192.168.214.35 (Operator PC)",
                "192.168.214.37 (Scale PC/Vision)",
                "192.168.214.60 (Riveter PC)"
            ]
        elif "192.168.213" in network:
            devices = [
                "192.168.213.33 (RTX System)",
                "192.168.213.60 (Riveter PLC)"
            ]
        else:  # Video network
            devices = ["192.168.1.1 (Video Gateway)"]
        
        self.device_combo.addItems(devices)
    
    def quick_ping(self):
        """Execute quick ping command"""
        device_text = self.device_combo.currentText()
        if not device_text:
            return
        
        # Extract IP address
        ip_match = re.match(r'(\d+\.\d+\.\d+\.\d+)', device_text)
        if ip_match:
            ip_address = ip_match.group(1)
            
            if self.continuous_check.isChecked():
                count = self.ping_count.value()
                command = f"ping -n {count} {ip_address}"
            else:
                command = f"ping {ip_address}"
            
            self.run_command(command)
    
    def execute_command(self):
        """Execute command from input"""
        command = self.command_input.text().strip()
        if command:
            self.run_command(command)
            self.command_input.clear()
    
    def run_command(self, command):
        """Run a command and display output"""
        self.output_display.append(f"\n> {command}\n")
        self.command_history.append(command)
        
        # Disable execute button during execution
        self.execute_button.setEnabled(False)
        
        # Create and run command executor thread
        self.executor = CommandExecutor(command)
        self.executor.output_ready.connect(self.append_output)
        self.executor.error_occurred.connect(self.append_error)
        self.executor.execution_complete.connect(self.command_complete)
        self.executor.start()
        
        # Log the command
        self.add_to_network_log(command)
    
    def append_output(self, text):
        """Append output to display"""
        cursor = self.output_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text + '\n')
        self.output_display.setTextCursor(cursor)
        
        # Parse ping results for logging
        if "Reply from" in text:
            match = re.search(r'Reply from ([\d.]+).*time=(\d+)ms', text)
            if match:
                self.update_last_log_entry("Success", match.group(2) + "ms")
        elif "Request timed out" in text:
            self.update_last_log_entry("Timeout", "N/A")
        elif "Destination host unreachable" in text:
            self.update_last_log_entry("Unreachable", "N/A")
    
    def append_error(self, text):
        """Append error to display"""
        cursor = self.output_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        # Set red color for errors
        format = QTextCharFormat()
        format.setForeground(QColor("red"))
        cursor.setCharFormat(format)
        cursor.insertText(text + '\n')
        
        # Reset format
        format.setForeground(QColor("white"))
        cursor.setCharFormat(format)
        self.output_display.setTextCursor(cursor)
    
    def command_complete(self):
        """Handle command completion"""
        self.execute_button.setEnabled(True)
        self.output_display.append("\nCommand completed.\n")
    
    def add_to_network_log(self, command):
        """Add entry to network log"""
        row = self.log_table.rowCount()
        self.log_table.insertRow(row)
        
        # Time
        time_str = datetime.now().strftime("%H:%M:%S")
        self.log_table.setItem(row, 0, QTableWidgetItem(time_str))
        
        # Command
        self.log_table.setItem(row, 1, QTableWidgetItem(command))
        
        # Target (extract IP if available)
        ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', command)
        target = ip_match.group(1) if ip_match else "N/A"
        self.log_table.setItem(row, 2, QTableWidgetItem(target))
        
        # Status, Response Time, Notes - will be updated later
        self.log_table.setItem(row, 3, QTableWidgetItem("Executing..."))
        self.log_table.setItem(row, 4, QTableWidgetItem(""))
        self.log_table.setItem(row, 5, QTableWidgetItem(""))
        
        # Scroll to new row
        self.log_table.scrollToBottom()
        
        # Store log entry
        self.network_log.append({
            "time": time_str,
            "command": command,
            "target": target,
            "status": "Executing...",
            "response_time": "",
            "notes": ""
        })
    
    def update_last_log_entry(self, status, response_time):
        """Update the last log entry with results"""
        if self.log_table.rowCount() > 0:
            row = self.log_table.rowCount() - 1
            self.log_table.setItem(row, 3, QTableWidgetItem(status))
            self.log_table.setItem(row, 4, QTableWidgetItem(response_time))
            
            # Update stored log
            if self.network_log:
                self.network_log[-1]["status"] = status
                self.network_log[-1]["response_time"] = response_time
    
    def save_network_log(self):
        """Save network log to file"""
        from PySide6.QtWidgets import QFileDialog
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Network Log", 
            f"network_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Text Files (*.txt)"
        )
        
        if filename:
            with open(filename, 'w') as f:
                f.write("Broetje Automation Network Diagnostics Log\n")
                f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("="*50 + "\n\n")
                
                for entry in self.network_log:
                    f.write(f"Time: {entry['time']}\n")
                    f.write(f"Command: {entry['command']}\n")
                    f.write(f"Target: {entry['target']}\n")
                    f.write(f"Status: {entry['status']}\n")
                    f.write(f"Response Time: {entry['response_time']}\n")
                    f.write(f"Notes: {entry['notes']}\n")
                    f.write("-"*30 + "\n")
                
                f.write(f"\nTotal Commands: {len(self.network_log)}\n")
            
            QMessageBox.information(self, "Log Saved", f"Network log saved to {filename}")
    
    def clear_network_log(self):
        """Clear the network log"""
        self.log_table.setRowCount(0)
        self.network_log.clear()
    
    def validate_task(self, task_id: str) -> bool:
        """Validate specific task completion"""
        if task_id == "open_cmd":
            # Check if command prompt screenshot exists
            return self.check_screenshot_exists(task_id)
        
        elif task_id in ["ping_machine_network", "ping_riveter_network", "ping_video_network"]:
            # Check if appropriate ping commands were executed
            task_config = next((t for t in self.module_data.get('tasks', []) if t['id'] == task_id), None)
            if task_config and 'network_targets' in task_config:
                for target in task_config['network_targets']:
                    if any(target in entry['command'] for entry in self.network_log):
                        return True
            return False
        
        elif task_id == "advanced_commands":
            # Check if various commands were executed
            task_config = next((t for t in self.module_data.get('tasks', []) if t['id'] == task_id), None)
            if task_config and 'commands' in task_config:
                executed_commands = [entry['command'].lower() for entry in self.network_log]
                required_commands = [cmd.split()[0].lower() for cmd in task_config['commands']]
                return all(any(req in cmd for cmd in executed_commands) for req in required_commands)
            return False
        
        return True
    
    def check_screenshot_exists(self, task_id: str) -> bool:
        """Check if screenshot for task exists"""
        screenshot_dir = Path("screenshots") / self.module_data['id']
        screenshot_path = screenshot_dir / f"{task_id}.png"
        return screenshot_path.exists()
    
    def get_additional_resources(self):
        """Get additional resources for this module"""
        return {
            "documents": [
                {
                    "title": "Windows CLI Guide",
                    "path": "resources/cli_guide.md",
                    "type": "markdown"
                }
            ],
            "links": [
                {
                    "title": "Windows Command Reference",
                    "url": "https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/windows-commands",
                    "description": "Official Microsoft command line reference"
                }
            ],
            "tips": [
                "Use Ctrl+C to stop a running command",
                "Use 'ping -t' for continuous ping",
                "Save command output with '>' redirection",
                "Use Tab key for command completion",
                "Up/Down arrows cycle through command history"
            ],
            "common_commands": {
                "ping": "Test network connectivity",
                "tracert": "Trace route to destination",
                "ipconfig": "Display IP configuration",
                "arp": "Display ARP cache",
                "nslookup": "Query DNS records",
                "netstat": "Display network connections",
                "pathping": "Combined ping and tracert"
            }
        }

# Export the module class
MODULE_CLASS = CLIDiagnosticsModule