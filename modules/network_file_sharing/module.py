#!/usr/bin/env python3
"""
Network File Sharing & Mapping Training Module
Interactive module for teaching network drive mapping and file sharing
"""

import os
import subprocess
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QLineEdit, QMessageBox, QGroupBox, QCheckBox,
    QFileDialog, QComboBox
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QPixmap
from training_module import TrainingModule

class NetworkFileSharingModule(TrainingModule):
    """Network File Sharing & Mapping Training Module"""
    
    def __init__(self, module_data, user_data, db_manager=None):
        self.db_manager = db_manager
        super().__init__(module_data, user_data)
        
    def get_learning_objectives(self) -> list:
        """Get learning objectives for this module"""
        return [
            "Understand Windows file sharing concepts",
            "Create and configure shared folders",
            "Map network drives to remote shares",
            "Test file transfers between networked computers",
            "Troubleshoot common sharing issues"
        ]
    
    def get_tasks(self) -> list:
        """Get tasks for this module from metadata"""
        return self.module_data.get('tasks', [])
    
    def setup_overview_tab(self):
        """Setup overview tab with custom content"""
        super().setup_overview_tab()
        
        # Get the scroll area widget (first tab)
        scroll_area = self.tab_widget.widget(0)
        
        # Get the content widget from the scroll area
        overview_widget = scroll_area.widget()
        layout = overview_widget.layout()
        
        # Add module-specific content
        network_group = QGroupBox("Network Configuration Helper")
        network_layout = QVBoxLayout()
        network_layout.setSpacing(10)  # Add spacing
        
        # Computer name input
        computer_layout = QHBoxLayout()
        computer_layout.addWidget(QLabel("Computer Name:"))
        self.computer_name_input = QLineEdit()
        self.computer_name_input.setPlaceholderText("e.g., PC-001")
        self.computer_name_input.setMinimumHeight(30)  # Ensure minimum height
        computer_layout.addWidget(self.computer_name_input)
        network_layout.addLayout(computer_layout)
        
        # Share name input
        share_layout = QHBoxLayout()
        share_layout.addWidget(QLabel("Share Name:"))
        self.share_name_input = QLineEdit()
        self.share_name_input.setPlaceholderText("e.g., SharedFolder")
        self.share_name_input.setMinimumHeight(30)  # Ensure minimum height
        share_layout.addWidget(self.share_name_input)
        network_layout.addLayout(share_layout)
        
        # Network path display
        self.network_path_label = QLabel("Network Path: ")
        self.network_path_label.setStyleSheet("font-weight: bold; color: #2c3e50; font-size: 14px;")
        self.network_path_label.setMinimumHeight(30)
        network_layout.addWidget(self.network_path_label)
        
        # Update network path when inputs change
        self.computer_name_input.textChanged.connect(self.update_network_path)
        self.share_name_input.textChanged.connect(self.update_network_path)
        
        network_group.setLayout(network_layout)
        layout.addWidget(network_group)
        
        # Add drive mapping section
        drive_group = QGroupBox("Drive Mapping Assistant")
        drive_layout = QVBoxLayout()
        
        # Drive letter selection
        drive_letter_layout = QHBoxLayout()
        drive_letter_layout.addWidget(QLabel("Drive Letter:"))
        self.drive_letter_combo = QComboBox()
        available_drives = self.get_available_drive_letters()
        self.drive_letter_combo.addItems(available_drives)
        drive_letter_layout.addWidget(self.drive_letter_combo)
        drive_layout.addLayout(drive_letter_layout)
        
        # Map drive button
        self.map_drive_button = QPushButton("Map Network Drive")
        self.map_drive_button.clicked.connect(self.map_network_drive)
        drive_layout.addWidget(self.map_drive_button)
        
        drive_group.setLayout(drive_layout)
        layout.addWidget(drive_group)
        
        # Add quick actions
        actions_group = QGroupBox("Quick Actions")
        actions_layout = QVBoxLayout()
        actions_layout.setSpacing(8)  # Add proper spacing
        
        open_sharing_button = QPushButton("Open Network Sharing Center")
        open_sharing_button.setMinimumHeight(35)
        open_sharing_button.clicked.connect(self.open_sharing_center)
        actions_layout.addWidget(open_sharing_button)
        
        open_disk_mgmt_button = QPushButton("Open Disk Management")
        open_disk_mgmt_button.setMinimumHeight(35)
        open_disk_mgmt_button.clicked.connect(self.open_disk_management)
        actions_layout.addWidget(open_disk_mgmt_button)
        
        test_connection_button = QPushButton("Test Network Connection")
        test_connection_button.setMinimumHeight(35)
        test_connection_button.clicked.connect(self.test_network_connection)
        actions_layout.addWidget(test_connection_button)
        
        actions_group.setLayout(actions_layout)
        layout.addWidget(actions_group)
        
    def update_network_path(self):
        """Update the network path display"""
        computer_name = self.computer_name_input.text().strip()
        share_name = self.share_name_input.text().strip()
        
        if computer_name and share_name:
            network_path = f"\\\\{computer_name}\\{share_name}"
            self.network_path_label.setText(f"Network Path: {network_path}")
        else:
            self.network_path_label.setText("Network Path: ")
    
    def get_available_drive_letters(self):
        """Get list of available drive letters"""
        import string
        used_drives = []
        
        try:
            # Windows only - get used drive letters
            if os.name == 'nt':
                import win32api
                drives = win32api.GetLogicalDriveStrings()
                drives = drives.split('\000')[:-1]
                used_drives = [d[0].upper() for d in drives]
        except:
            # Fallback if win32api not available
            used_drives = ['C', 'D']
        
        # Return available letters
        all_letters = list(string.ascii_uppercase)
        available = [f"{letter}:" for letter in all_letters 
                    if letter not in used_drives and letter not in ['A', 'B']]
        return available
    
    def map_network_drive(self):
        """Map a network drive using Windows net use command"""
        drive_letter = self.drive_letter_combo.currentText()
        computer_name = self.computer_name_input.text().strip()
        share_name = self.share_name_input.text().strip()
        
        if not all([drive_letter, computer_name, share_name]):
            QMessageBox.warning(self, "Missing Information", 
                              "Please fill in all fields before mapping a drive.")
            return
        
        network_path = f"\\\\{computer_name}\\{share_name}"
        
        try:
            # Windows net use command
            cmd = f'net use {drive_letter} "{network_path}" /persistent:yes'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                QMessageBox.information(self, "Success", 
                                      f"Successfully mapped {network_path} to {drive_letter}")
                # Mark task as complete
                for task_id, widget in self.task_widgets.items():
                    if "map_network_drive" in task_id:
                        widget.set_completed(True)
            else:
                QMessageBox.warning(self, "Mapping Failed", 
                                  f"Failed to map drive: {result.stderr}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error mapping drive: {str(e)}")
    
    def open_sharing_center(self):
        """Open Windows Network and Sharing Center"""
        try:
            if os.name == 'nt':
                os.system('control.exe /name Microsoft.NetworkAndSharingCenter')
            QMessageBox.information(self, "Opening", 
                                  "Network and Sharing Center should now be open.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not open sharing center: {str(e)}")
    
    def open_disk_management(self):
        """Open Windows Disk Management"""
        try:
            if os.name == 'nt':
                os.system('diskmgmt.msc')
            QMessageBox.information(self, "Opening", 
                                  "Disk Management should now be open.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not open disk management: {str(e)}")
    
    def test_network_connection(self):
        """Test network connection to specified computer"""
        computer_name = self.computer_name_input.text().strip()
        
        if not computer_name:
            QMessageBox.warning(self, "No Computer Name", 
                              "Please enter a computer name to test.")
            return
        
        try:
            # Ping test
            cmd = f"ping -n 4 {computer_name}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if "Reply from" in result.stdout:
                QMessageBox.information(self, "Connection Test", 
                                      f"Successfully connected to {computer_name}")
            else:
                QMessageBox.warning(self, "Connection Test", 
                                  f"Could not reach {computer_name}\n\n{result.stdout}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error testing connection: {str(e)}")
    
    def validate_task(self, task_id: str) -> bool:
        """Validate specific task completion"""
        if task_id == "share_folder":
            # Check if user has taken screenshot showing shared folder
            return self.check_screenshot_exists(task_id)
        
        elif task_id == "create_temp_directory":
            # Check if D:\Temp directory exists
            temp_path = Path("D:/Temp")
            if temp_path.exists() and temp_path.is_dir():
                # Check for user initials subdirectory
                user_dirs = list(temp_path.iterdir())
                return len(user_dirs) > 0
            return False
        
        elif task_id == "map_network_drive":
            # Check if any network drives are mapped
            try:
                result = subprocess.run("net use", shell=True, capture_output=True, text=True)
                return "OK" in result.stdout
            except:
                return False
        
        elif task_id == "test_file_transfer":
            # Check if test file exists
            return self.check_screenshot_exists(task_id)
        
        return True
    
    def check_screenshot_exists(self, task_id: str) -> bool:
        """Check if screenshot for task exists"""
        screenshot_dir = Path("screenshots") / self.module_data['id']
        screenshot_path = screenshot_dir / f"{task_id}.png"
        return screenshot_path.exists()

# Must be at module level
MODULE_CLASS = NetworkFileSharingModule