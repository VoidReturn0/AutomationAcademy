#!/usr/bin/env python3
"""
IP Address Configuration Training Module
Interactive module for teaching network IP configuration
"""

import os
import subprocess
import re
import socket
from datetime import datetime
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QLineEdit, QMessageBox, QGroupBox, QCheckBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QSpinBox,
    QComboBox, QRadioButton, QButtonGroup
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QColor
from training_module import TrainingModule

class IPConfigurationModule(TrainingModule):
    """IP Address Configuration Training Module"""
    
    def __init__(self, module_data, user_data, db_manager=None):
        self.db_manager = db_manager
        self.network_configs = []
        super().__init__(module_data, user_data)
        
    def get_learning_objectives(self) -> list:
        return [
            "Configure IP addresses for different networks",
            "Understand subnet mask configuration",
            "Set appropriate gateway addresses",
            "Test network connectivity"
        ]
    
    def get_tasks(self) -> list:
        return self.module_data.get('tasks', [])
    
    # Remove custom setup_overview_tab - it's causing issues
        
    def setup_custom_ui(self, parent):
        """Setup module-specific UI elements"""
        layout = QVBoxLayout(parent)
        
        # Network selection section
        network_group = QGroupBox("Network Selection")
        network_layout = QVBoxLayout()
        
        # Network radio buttons
        self.network_button_group = QButtonGroup()
        
        self.machine_network_radio = QRadioButton("Machine Network (192.168.214.x)")
        self.machine_network_radio.setChecked(True)
        self.network_button_group.addButton(self.machine_network_radio, 0)
        network_layout.addWidget(self.machine_network_radio)
        
        self.riveter_network_radio = QRadioButton("Riveter Network (192.168.213.x)")
        self.network_button_group.addButton(self.riveter_network_radio, 1)
        network_layout.addWidget(self.riveter_network_radio)
        
        self.video_network_radio = QRadioButton("Video Network (192.168.1.x)")
        self.network_button_group.addButton(self.video_network_radio, 2)
        network_layout.addWidget(self.video_network_radio)
        
        # Network information display
        self.network_info_label = QLabel()
        self.update_network_info()
        network_layout.addWidget(self.network_info_label)
        
        self.network_button_group.buttonClicked.connect(self.update_network_info)
        
        network_group.setLayout(network_layout)
        layout.addWidget(network_group)
        
        # IP Configuration section
        config_group = QGroupBox("IP Configuration")
        config_layout = QVBoxLayout()
        
        # IP Address input
        ip_layout = QHBoxLayout()
        ip_layout.addWidget(QLabel("IP Address:"))
        
        self.ip_octet1 = QSpinBox()
        self.ip_octet1.setRange(0, 255)
        self.ip_octet1.setValue(192)
        ip_layout.addWidget(self.ip_octet1)
        
        ip_layout.addWidget(QLabel("."))
        
        self.ip_octet2 = QSpinBox()
        self.ip_octet2.setRange(0, 255)
        self.ip_octet2.setValue(168)
        ip_layout.addWidget(self.ip_octet2)
        
        ip_layout.addWidget(QLabel("."))
        
        self.ip_octet3 = QSpinBox()
        self.ip_octet3.setRange(0, 255)
        self.ip_octet3.setValue(214)
        ip_layout.addWidget(self.ip_octet3)
        
        ip_layout.addWidget(QLabel("."))
        
        self.ip_octet4 = QSpinBox()
        self.ip_octet4.setRange(0, 255)
        self.ip_octet4.setValue(100)
        ip_layout.addWidget(self.ip_octet4)
        
        config_layout.addLayout(ip_layout)
        
        # Subnet mask
        subnet_layout = QHBoxLayout()
        subnet_layout.addWidget(QLabel("Subnet Mask:"))
        self.subnet_mask_input = QLineEdit("255.255.255.0")
        self.subnet_mask_input.setReadOnly(True)
        subnet_layout.addWidget(self.subnet_mask_input)
        config_layout.addLayout(subnet_layout)
        
        # Gateway
        gateway_layout = QHBoxLayout()
        gateway_layout.addWidget(QLabel("Default Gateway:"))
        self.gateway_input = QLineEdit()
        self.gateway_input.setReadOnly(True)
        gateway_layout.addWidget(self.gateway_input)
        config_layout.addLayout(gateway_layout)
        
        # DNS servers
        dns_layout = QVBoxLayout()
        dns_layout.addWidget(QLabel("DNS Servers:"))
        
        primary_dns_layout = QHBoxLayout()
        primary_dns_layout.addWidget(QLabel("Primary:"))
        self.primary_dns_input = QLineEdit()
        primary_dns_layout.addWidget(self.primary_dns_input)
        dns_layout.addLayout(primary_dns_layout)
        
        secondary_dns_layout = QHBoxLayout()
        secondary_dns_layout.addWidget(QLabel("Secondary:"))
        self.secondary_dns_input = QLineEdit("8.8.8.8")
        secondary_dns_layout.addWidget(self.secondary_dns_input)
        dns_layout.addLayout(secondary_dns_layout)
        
        config_layout.addLayout(dns_layout)
        
        # Configuration mode
        mode_layout = QHBoxLayout()
        self.static_radio = QRadioButton("Static IP")
        self.static_radio.setChecked(True)
        self.dhcp_radio = QRadioButton("DHCP (Automatic)")
        
        mode_layout.addWidget(self.static_radio)
        mode_layout.addWidget(self.dhcp_radio)
        config_layout.addLayout(mode_layout)
        
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)
        
        # Action buttons
        actions_group = QGroupBox("Actions")
        actions_layout = QVBoxLayout()
        
        apply_button = QPushButton("Apply Configuration")
        apply_button.clicked.connect(self.apply_configuration)
        actions_layout.addWidget(apply_button)
        
        test_button = QPushButton("Test Configuration")
        test_button.clicked.connect(self.test_configuration)
        actions_layout.addWidget(test_button)
        
        open_network_button = QPushButton("Open Network Settings")
        open_network_button.clicked.connect(self.open_network_settings)
        actions_layout.addWidget(open_network_button)
        
        show_current_button = QPushButton("Show Current Configuration")
        show_current_button.clicked.connect(self.show_current_config)
        actions_layout.addWidget(show_current_button)
        
        actions_group.setLayout(actions_layout)
        layout.addWidget(actions_group)
        
        # Configuration log
        log_group = QGroupBox("Configuration Log")
        log_layout = QVBoxLayout()
        
        self.config_log = QTextEdit()
        self.config_log.setReadOnly(True)
        self.config_log.setMaximumHeight(150)
        log_layout.addWidget(self.config_log)
        
        save_log_button = QPushButton("Save Configuration Log")
        save_log_button.clicked.connect(self.save_configuration_log)
        log_layout.addWidget(save_log_button)
        
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
        # Network diagram
        diagram_group = QGroupBox("Network Diagram")
        diagram_layout = QVBoxLayout()
        
        self.network_diagram = QTextEdit()
        self.network_diagram.setReadOnly(True)
        self.network_diagram.setMaximumHeight(200)
        self.network_diagram.setFont(QFont("Consolas", 9))
        self.update_network_diagram()
        diagram_layout.addWidget(self.network_diagram)
        
        diagram_group.setLayout(diagram_layout)
        layout.addWidget(diagram_group)
    
    def update_network_info(self):
        """Update network information display"""
        network_id = self.network_button_group.checkedId()
        
        if network_id == 0:  # Machine Network
            info = """
<b>Machine Network (192.168.214.x)</b><br>
Gateway: 192.168.214.1 (NCU)<br>
Range: 192.168.214.50 - 192.168.214.200<br>
<br>
<b>Important Devices:</b><br>
• Service PC: 192.168.214.34<br>
• Operator PC: 192.168.214.35<br>
• Scale PC: 192.168.214.37<br>
• Riveter PC: 192.168.214.60
            """
            self.ip_octet3.setValue(214)
            self.gateway_input.setText("192.168.214.1")
            self.primary_dns_input.setText("192.168.214.1")
            
        elif network_id == 1:  # Riveter Network
            info = """
<b>Riveter Network (192.168.213.x)</b><br>
Gateway: 192.168.213.1<br>
Range: 192.168.213.50 - 192.168.213.250<br>
<br>
<b>Important Devices:</b><br>
• RTX System: 192.168.213.33<br>
• Riveter PLC: 192.168.213.60
            """
            self.ip_octet3.setValue(213)
            self.gateway_input.setText("192.168.213.1")
            self.primary_dns_input.setText("192.168.213.1")
            
        else:  # Video Network
            info = """
<b>Video Network (192.168.1.x)</b><br>
Gateway: 192.168.1.1<br>
Range: 192.168.1.10 - 192.168.1.254<br>
<br>
<b>Important Devices:</b><br>
• Video Gateway: 192.168.1.1
            """
            self.ip_octet3.setValue(1)
            self.gateway_input.setText("192.168.1.1")
            self.primary_dns_input.setText("192.168.1.1")
        
        self.network_info_label.setText(info)
        
    def update_network_diagram(self):
        """Update the network diagram"""
        diagram = """
Broetje Automation Network Architecture
=====================================

[MACHINE NETWORK - 192.168.214.x]
    |
    +-- NCU Controller (192.168.214.1) [Gateway]
    +-- Service PC (192.168.214.34)
    +-- Operator PC (192.168.214.35)
    +-- Scale PC/Vision (192.168.214.37)
    +-- Ketop Tablets (192.168.214.38/39)
    +-- Riveter PC (192.168.214.60)
    
[RIVETER NETWORK - 192.168.213.x]
    |
    +-- Gateway (192.168.213.1)
    +-- RTX System (192.168.213.33)
    +-- Riveter PLC Backup (192.168.213.60)
    
[VIDEO NETWORK - 192.168.1.x]
    |
    +-- Video Gateway (192.168.1.1)
    +-- Recording Devices (192.168.1.x)
        """
        self.network_diagram.setText(diagram)
    
    def apply_configuration(self):
        """Apply the IP configuration (simulated)"""
        if self.static_radio.isChecked():
            ip_address = f"{self.ip_octet1.value()}.{self.ip_octet2.value()}.{self.ip_octet3.value()}.{self.ip_octet4.value()}"
            subnet_mask = self.subnet_mask_input.text()
            gateway = self.gateway_input.text()
            primary_dns = self.primary_dns_input.text()
            secondary_dns = self.secondary_dns_input.text()
            
            config_text = f"""
Configuration Applied:
IP Address: {ip_address}
Subnet Mask: {subnet_mask}
Gateway: {gateway}
Primary DNS: {primary_dns}
Secondary DNS: {secondary_dns}
Time: {datetime.now().strftime('%H:%M:%S')}
"""
            self.config_log.append(config_text)
            
            # Store configuration
            self.network_configs.append({
                "ip": ip_address,
                "subnet": subnet_mask,
                "gateway": gateway,
                "primary_dns": primary_dns,
                "secondary_dns": secondary_dns,
                "time": datetime.now()
            })
            
            # Mark task complete
            if self.network_button_group.checkedId() == 0:
                self.task_widgets.get("configure_machine_network").set_completed(True)
            elif self.network_button_group.checkedId() == 1:
                self.task_widgets.get("configure_riveter_network").set_completed(True)
            elif self.network_button_group.checkedId() == 2:
                self.task_widgets.get("configure_video_network").set_completed(True)
            
            QMessageBox.information(self, "Configuration Applied", 
                                  f"IP configuration has been applied:\n{ip_address}")
        else:
            config_text = "DHCP Configuration Applied\n"
            self.config_log.append(config_text)
            self.task_widgets.get("restore_dhcp").set_completed(True)
            QMessageBox.information(self, "DHCP Enabled", 
                                  "Network adapter set to obtain IP automatically")
    
    def test_configuration(self):
        """Test the current configuration"""
        network_id = self.network_button_group.checkedId()
        test_targets = []
        
        if network_id == 0:  # Machine Network
            test_targets = ["192.168.214.1", "192.168.214.34", "192.168.214.35"]
        elif network_id == 1:  # Riveter Network
            test_targets = ["192.168.213.1", "192.168.213.33"]
        else:  # Video Network
            test_targets = ["192.168.1.1"]
        
        results = []
        for target in test_targets:
            try:
                response = subprocess.run(
                    f"ping -n 1 {target}",
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if "Reply from" in response.stdout:
                    results.append(f"✓ {target} - Reachable")
                else:
                    results.append(f"✗ {target} - Unreachable")
            except:
                results.append(f"✗ {target} - Error")
        
        result_text = "\n".join(results)
        self.config_log.append(f"\nConnectivity Test Results:\n{result_text}\n")
        
        # Mark test task complete
        if network_id == 0:
            self.task_widgets.get("test_machine_network").set_completed(True)
        
        QMessageBox.information(self, "Test Results", result_text)
    
    def open_network_settings(self):
        """Open Windows network settings"""
        try:
            os.system('ncpa.cpl')
            QMessageBox.information(self, "Network Settings", 
                                  "Network adapter settings window should now be open.")
            self.task_widgets.get("access_network_settings").set_completed(True)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not open network settings: {str(e)}")
    
    def show_current_config(self):
        """Show current network configuration"""
        try:
            result = subprocess.run("ipconfig /all", shell=True, capture_output=True, text=True)
            self.config_log.append(f"\nCurrent Configuration:\n{result.stdout}\n")
        except Exception as e:
            self.config_log.append(f"Error getting configuration: {str(e)}\n")
    
    def save_configuration_log(self):
        """Save configuration log to file"""
        from PySide6.QtWidgets import QFileDialog
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Configuration Log", 
            f"network_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Text Files (*.txt)"
        )
        
        if filename:
            with open(filename, 'w') as f:
                f.write("Broetje Automation Network Configuration Log\n")
                f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("="*50 + "\n\n")
                f.write(self.config_log.toPlainText())
                
                # Add configuration history
                f.write("\n\nConfiguration History:\n")
                f.write("-"*30 + "\n")
                for config in self.network_configs:
                    f.write(f"Time: {config['time'].strftime('%H:%M:%S')}\n")
                    f.write(f"IP: {config['ip']}\n")
                    f.write(f"Gateway: {config['gateway']}\n")
                    f.write(f"DNS: {config['primary_dns']}, {config['secondary_dns']}\n")
                    f.write("-"*30 + "\n")
            
            QMessageBox.information(self, "Log Saved", f"Configuration log saved to {filename}")
    
    def validate_task(self, task_id: str) -> bool:
        """Validate specific task completion"""
        if task_id == "access_network_settings":
            # Check if user has taken screenshot of network settings
            return self.check_screenshot_exists(task_id)
        
        elif task_id in ["configure_machine_network", "configure_riveter_network", "configure_video_network"]:
            # Check if appropriate configuration was applied
            return any(config for config in self.network_configs 
                      if task_id.replace("configure_", "") in config['ip'])
        
        elif task_id == "test_machine_network":
            # Check if connectivity test was performed
            return "Connectivity Test Results" in self.config_log.toPlainText()
        
        elif task_id == "restore_dhcp":
            # Check if DHCP was enabled
            return "DHCP Configuration Applied" in self.config_log.toPlainText()
        
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
                    "title": "IP Configuration Guide",
                    "path": "resources/ip_config_guide.md",
                    "type": "markdown"
                },
                {
                    "title": "Network Configuration PDF",
                    "path": "resources/IP config guide.pdf",
                    "type": "pdf"
                }
            ],
            "links": [
                {
                    "title": "TCP/IP Fundamentals",
                    "url": "https://docs.microsoft.com/en-us/windows-server/networking/tcpip/tcpip-fundamentals",
                    "description": "Microsoft TCP/IP documentation"
                }
            ],
            "tips": [
                "Always document IP configurations",
                "Avoid using .1 and .255 addresses",
                "Test connectivity after changes",
                "Return to DHCP when finished",
                "Check for IP conflicts before assigning"
            ],
            "network_ranges": {
                "Machine Network": "192.168.214.50 - 192.168.214.200",
                "Riveter Network": "192.168.213.50 - 192.168.213.250", 
                "Video Network": "192.168.1.10 - 192.168.1.254"
            }
        }

# Export the module class
MODULE_CLASS = IPConfigurationModule