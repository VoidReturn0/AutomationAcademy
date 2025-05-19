#!/usr/bin/env python3
"""
Remote Access Configuration Training Module
Interactive module for teaching UltraVNC and Teams remote access setup
"""

import os
import subprocess
from datetime import datetime
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QLineEdit, QMessageBox, QGroupBox, QCheckBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QRadioButton, QButtonGroup, QSpinBox
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont
from training_module import TrainingModule

class RemoteAccessModule(TrainingModule):
    """Remote Access Configuration Training Module"""
    
    def __init__(self, module_data, user_data, db_manager=None):
        self.db_manager = db_manager
        self.vnc_config = {}
        self.teams_config = {}
        self.connection_history = []
        super().__init__(module_data, user_data)
        
    def get_learning_objectives(self) -> list:
        return [
            "Configure UltraVNC for remote access",
            "Use secure VNC passwords",
            "Test remote connections",
            "Configure Teams for remote support"
        ]
    
    def get_tasks(self) -> list:
        return self.module_data.get('tasks', [])
    
    # Remove custom setup_overview_tab - it's causing issues
        
    def setup_custom_ui(self, parent):
        """Setup module-specific UI elements"""
        layout = QVBoxLayout(parent)
        
        # VNC Installation section
        vnc_install_group = QGroupBox("UltraVNC Installation")
        vnc_install_layout = QVBoxLayout()
        
        install_status_layout = QHBoxLayout()
        install_status_layout.addWidget(QLabel("Installation Status:"))
        self.install_status_label = QLabel("Not Installed")
        self.install_status_label.setStyleSheet("font-weight: bold; color: #e74c3c;")
        install_status_layout.addWidget(self.install_status_label)
        vnc_install_layout.addLayout(install_status_layout)
        
        # Installation checklist
        self.install_checklist = {
            'download': QCheckBox("Downloaded UltraVNC installer"),
            'admin': QCheckBox("Running as Administrator"),
            'server': QCheckBox("VNC Server component selected"),
            'service': QCheckBox("Registered as system service"),
            'firewall': QCheckBox("Windows Firewall exception added")
        }
        
        for step, checkbox in self.install_checklist.items():
            vnc_install_layout.addWidget(checkbox)
            checkbox.stateChanged.connect(self.update_install_status)
        
        simulate_install_button = QPushButton("Simulate Installation")
        simulate_install_button.clicked.connect(self.simulate_installation)
        vnc_install_layout.addWidget(simulate_install_button)
        
        vnc_install_group.setLayout(vnc_install_layout)
        layout.addWidget(vnc_install_group)
        
        # VNC Configuration section
        vnc_config_group = QGroupBox("VNC Server Configuration")
        vnc_config_layout = QVBoxLayout()
        
        # Password configuration
        password_layout = QHBoxLayout()
        password_layout.addWidget(QLabel("VNC Password:"))
        self.vnc_password_input = QLineEdit()
        self.vnc_password_input.setText("ae746")
        self.vnc_password_input.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(self.vnc_password_input)
        
        show_password_button = QPushButton("Show")
        show_password_button.setCheckable(True)
        show_password_button.clicked.connect(
            lambda checked: self.vnc_password_input.setEchoMode(
                QLineEdit.Normal if checked else QLineEdit.Password
            )
        )
        password_layout.addWidget(show_password_button)
        vnc_config_layout.addLayout(password_layout)
        
        # View-only password
        view_password_layout = QHBoxLayout()
        view_password_layout.addWidget(QLabel("View-Only Password:"))
        self.view_password_input = QLineEdit()
        self.view_password_input.setPlaceholderText("Optional")
        self.view_password_input.setEchoMode(QLineEdit.Password)
        view_password_layout.addWidget(self.view_password_input)
        vnc_config_layout.addLayout(view_password_layout)
        
        # Network settings
        network_settings_label = QLabel("Network Settings:")
        network_settings_label.setFont(QFont("Arial", 10, QFont.Bold))
        vnc_config_layout.addWidget(network_settings_label)
        
        # Port configuration
        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("VNC Port:"))
        self.vnc_port_spin = QSpinBox()
        self.vnc_port_spin.setRange(5900, 5999)
        self.vnc_port_spin.setValue(5900)
        port_layout.addWidget(self.vnc_port_spin)
        vnc_config_layout.addLayout(port_layout)
        
        # Display number
        display_layout = QHBoxLayout()
        display_layout.addWidget(QLabel("Display Number:"))
        self.display_combo = QComboBox()
        self.display_combo.addItems([":0", ":1", ":2"])
        self.display_combo.setCurrentIndex(0)
        display_layout.addWidget(self.display_combo)
        vnc_config_layout.addLayout(display_layout)
        
        # Options
        self.loopback_check = QCheckBox("Enable loopback connections")
        self.loopback_check.setChecked(True)
        vnc_config_layout.addWidget(self.loopback_check)
        
        self.all_interfaces_check = QCheckBox("Listen on all interfaces")
        self.all_interfaces_check.setChecked(True)
        vnc_config_layout.addWidget(self.all_interfaces_check)
        
        apply_config_button = QPushButton("Apply Configuration")
        apply_config_button.clicked.connect(self.apply_vnc_config)
        vnc_config_layout.addWidget(apply_config_button)
        
        vnc_config_group.setLayout(vnc_config_layout)
        layout.addWidget(vnc_config_group)
        
        # Connection Testing section
        test_group = QGroupBox("Connection Testing")
        test_layout = QVBoxLayout()
        
        # Current IP display
        ip_layout = QHBoxLayout()
        ip_layout.addWidget(QLabel("Server IP:"))
        self.server_ip_label = QLabel("192.168.214.35")
        self.server_ip_label.setStyleSheet("font-weight: bold;")
        ip_layout.addWidget(self.server_ip_label)
        
        detect_ip_button = QPushButton("Detect IP")
        detect_ip_button.clicked.connect(self.detect_server_ip)
        ip_layout.addWidget(detect_ip_button)
        test_layout.addLayout(ip_layout)
        
        # Local test
        local_test_button = QPushButton("Test Local Connection")
        local_test_button.clicked.connect(self.test_local_connection)
        test_layout.addWidget(local_test_button)
        
        # Remote test
        remote_test_layout = QHBoxLayout()
        remote_test_layout.addWidget(QLabel("Remote IP:"))
        self.remote_ip_input = QLineEdit()
        self.remote_ip_input.setPlaceholderText("Enter remote PC IP")
        remote_test_layout.addWidget(self.remote_ip_input)
        test_layout.addLayout(remote_test_layout)
        
        remote_test_button = QPushButton("Test Remote Connection")
        remote_test_button.clicked.connect(self.test_remote_connection)
        test_layout.addWidget(remote_test_button)
        
        # Connection status
        self.connection_status_text = QTextEdit()
        self.connection_status_text.setReadOnly(True)
        self.connection_status_text.setMaximumHeight(100)
        test_layout.addWidget(self.connection_status_text)
        
        test_group.setLayout(test_layout)
        layout.addWidget(test_group)
        
        # Teams Configuration section (optional)
        teams_group = QGroupBox("Microsoft Teams Configuration (Optional)")
        teams_layout = QVBoxLayout()
        
        teams_info_label = QLabel("Configure Teams for additional remote support:")
        teams_info_label.setWordWrap(True)
        teams_layout.addWidget(teams_info_label)
        
        self.teams_checklist = {
            'teams_installed': QCheckBox("Teams installed and logged in"),
            'camera_configured': QCheckBox("Camera configured"),
            'microphone_configured': QCheckBox("Microphone configured"),
            'screen_sharing_tested': QCheckBox("Screen sharing tested"),
            'remote_control_enabled': QCheckBox("Remote control permissions set")
        }
        
        for step, checkbox in self.teams_checklist.items():
            teams_layout.addWidget(checkbox)
        
        teams_test_button = QPushButton("Test Teams Configuration")
        teams_test_button.clicked.connect(self.test_teams_config)
        teams_layout.addWidget(teams_test_button)
        
        teams_group.setLayout(teams_layout)
        layout.addWidget(teams_group)
        
        # Connection History
        history_group = QGroupBox("Connection History")
        history_layout = QVBoxLayout()
        
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels([
            "Time", "Type", "IP Address", "Status"
        ])
        self.history_table.horizontalHeader().setStretchLastSection(True)
        history_layout.addWidget(self.history_table)
        
        clear_history_button = QPushButton("Clear History")
        clear_history_button.clicked.connect(self.clear_connection_history)
        history_layout.addWidget(clear_history_button)
        
        history_group.setLayout(history_layout)
        layout.addWidget(history_group)
    
    def update_install_status(self):
        """Update installation status based on checklist"""
        all_checked = all(cb.isChecked() for cb in self.install_checklist.values())
        if all_checked:
            self.install_status_label.setText("Installed")
            self.install_status_label.setStyleSheet("font-weight: bold; color: #27ae60;")
            self.task_widgets.get("install_vnc_server").set_completed(True)
    
    def simulate_installation(self):
        """Simulate VNC installation process"""
        steps = [
            "Downloading UltraVNC installer...",
            "Launching installer with admin privileges...",
            "Installing VNC Server component...",
            "Registering as Windows service...",
            "Configuring firewall exception...",
            "Installation complete!"
        ]
        
        for i, step in enumerate(steps):
            QTimer.singleShot(i * 500, lambda s=step: self.connection_status_text.append(s))
        
        QTimer.singleShot(len(steps) * 500, self.installation_complete)
    
    def installation_complete(self):
        """Handle installation completion"""
        for checkbox in self.install_checklist.values():
            checkbox.setChecked(True)
        
        QMessageBox.information(self, "Installation Complete",
                              "UltraVNC has been successfully installed.")
    
    def apply_vnc_config(self):
        """Apply VNC configuration"""
        self.vnc_config = {
            'password': self.vnc_password_input.text(),
            'view_password': self.view_password_input.text(),
            'port': self.vnc_port_spin.value(),
            'display': self.display_combo.currentText(),
            'loopback': self.loopback_check.isChecked(),
            'all_interfaces': self.all_interfaces_check.isChecked()
        }
        
        # Verify password
        if self.vnc_config['password'] != 'ae746':
            QMessageBox.warning(self, "Password Mismatch",
                              "Please use the standard Broetje password: ae746")
            return
        
        self.task_widgets.get("configure_vnc_password").set_completed(True)
        self.task_widgets.get("network_configuration").set_completed(True)
        
        QMessageBox.information(self, "Configuration Applied",
                              "VNC server configuration has been applied.")
    
    def detect_server_ip(self):
        """Detect server IP address"""
        # Simulated IP detection
        import random
        network_prefix = "192.168.214"
        host = random.randint(30, 40)
        self.server_ip_label.setText(f"{network_prefix}.{host}")
    
    def test_local_connection(self):
        """Test local VNC connection"""
        self.connection_status_text.append(
            f"Testing local connection to localhost:{self.vnc_port_spin.value()}..."
        )
        
        # Simulate connection test
        QTimer.singleShot(1000, lambda: self.connection_test_result(
            "localhost", self.vnc_port_spin.value(), True
        ))
    
    def test_remote_connection(self):
        """Test remote VNC connection"""
        remote_ip = self.remote_ip_input.text().strip()
        if not remote_ip:
            QMessageBox.warning(self, "No IP Address",
                              "Please enter a remote IP address.")
            return
        
        self.connection_status_text.append(
            f"Testing remote connection to {remote_ip}:{self.vnc_port_spin.value()}..."
        )
        
        # Simulate connection test
        QTimer.singleShot(1500, lambda: self.connection_test_result(
            remote_ip, self.vnc_port_spin.value(), True
        ))
    
    def connection_test_result(self, ip, port, success):
        """Handle connection test result"""
        status = "Success" if success else "Failed"
        color = "#27ae60" if success else "#e74c3c"
        
        self.connection_status_text.append(
            f'<span style="color: {color};">Connection to {ip}:{port} - {status}</span>'
        )
        
        # Add to history
        self.add_connection_history(ip, f"VNC Test", status)
        
        if success and ip == "localhost":
            self.task_widgets.get("test_local_connection").set_completed(True)
        elif success and ip != "localhost":
            self.task_widgets.get("remote_connection_test").set_completed(True)
    
    def test_teams_config(self):
        """Test Teams configuration"""
        all_checked = all(cb.isChecked() for cb in self.teams_checklist.values())
        
        if all_checked:
            self.task_widgets.get("teams_configuration").set_completed(True)
            QMessageBox.information(self, "Teams Configuration",
                                  "Microsoft Teams is properly configured for remote support.")
            self.add_connection_history("Teams", "Configuration Test", "Success")
        else:
            QMessageBox.warning(self, "Teams Configuration",
                              "Please complete all Teams configuration steps.")
    
    def add_connection_history(self, ip, conn_type, status):
        """Add entry to connection history"""
        row = self.history_table.rowCount()
        self.history_table.insertRow(row)
        
        time_item = QTableWidgetItem(datetime.now().strftime("%H:%M:%S"))
        type_item = QTableWidgetItem(conn_type)
        ip_item = QTableWidgetItem(ip)
        status_item = QTableWidgetItem(status)
        
        if status == "Success":
            status_item.setForeground(Qt.green)
        else:
            status_item.setForeground(Qt.red)
        
        self.history_table.setItem(row, 0, time_item)
        self.history_table.setItem(row, 1, type_item)
        self.history_table.setItem(row, 2, ip_item)
        self.history_table.setItem(row, 3, status_item)
        
        # Store in history
        self.connection_history.append({
            'time': datetime.now(),
            'type': conn_type,
            'ip': ip,
            'status': status
        })
    
    def clear_connection_history(self):
        """Clear connection history"""
        self.history_table.setRowCount(0)
        self.connection_history.clear()
    
    def validate_task(self, task_id: str) -> bool:
        """Validate specific task completion"""
        if task_id == "install_vnc_server":
            return all(cb.isChecked() for cb in self.install_checklist.values())
        
        elif task_id == "configure_vnc_password":
            return self.vnc_config.get('password') == 'ae746'
        
        elif task_id == "network_configuration":
            return bool(self.vnc_config)
        
        elif task_id == "test_local_connection":
            return any(h['type'] == "VNC Test" and h['ip'] == "localhost" 
                      and h['status'] == "Success" for h in self.connection_history)
        
        elif task_id == "remote_connection_test":
            return any(h['type'] == "VNC Test" and h['ip'] != "localhost" 
                      and h['status'] == "Success" for h in self.connection_history)
        
        elif task_id == "teams_configuration":
            return all(cb.isChecked() for cb in self.teams_checklist.values())
        
        return True
    
    def get_additional_resources(self):
        """Get additional resources for this module"""
        return {
            "documents": [
                {
                    "title": "Remote Access Guide",
                    "path": "resources/remote_access_guide.md",
                    "type": "markdown"
                }
            ],
            "links": [
                {
                    "title": "UltraVNC Documentation",
                    "url": "https://uvnc.com/docs/",
                    "description": "Official UltraVNC documentation"
                },
                {
                    "title": "Teams Remote Control",
                    "url": "https://support.microsoft.com/en-us/office/share-your-screen-in-a-teams-meeting",
                    "description": "Microsoft Teams screen sharing guide"
                }
            ],
            "tips": [
                "Always use strong passwords for VNC",
                "Configure firewall exceptions properly",
                "Test connections before field deployment",
                "Document all remote access configurations",
                "Consider using VPN for extra security",
                "Keep VNC software updated"
            ],
            "troubleshooting": {
                "Connection refused": "Check firewall settings and VNC service status",
                "Authentication failed": "Verify password is correct (ae746)",
                "Black screen": "Check display settings and user permissions",
                "Slow performance": "Adjust color depth and encoding settings"
            }
        }

# Export the module class
MODULE_CLASS = RemoteAccessModule