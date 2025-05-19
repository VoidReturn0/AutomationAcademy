#!/usr/bin/env python3
"""
Hard Drive Replacement Training Module
Interactive module for teaching SSD replacement procedures in Siemens IPCs
"""

import os
import subprocess
from datetime import datetime
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QLineEdit, QMessageBox, QGroupBox, QCheckBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QRadioButton, QButtonGroup, QSpinBox, QListWidget
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QPixmap
from training_module import TrainingModule

class DriveReplacementModule(TrainingModule):
    """Hard Drive Replacement Training Module"""
    
    def __init__(self, module_data, user_data, db_manager=None):
        self.db_manager = db_manager
        self.documentation = {}
        self.hardware_checklist = []
        self.performance_results = {}
        super().__init__(module_data, user_data)
        
    def get_learning_objectives(self) -> list:
        return [
            "Safely replace hard drives",
            "Follow proper hardware procedures",
            "Use correct tools",
            "Verify drive functionality"
        ]
    
    def get_tasks(self) -> list:
        return self.module_data.get('tasks', [])
    
    # Remove custom setup_overview_tab - it's causing issues
        
    def setup_custom_ui(self, parent):
        """Setup module-specific UI elements"""
        layout = QVBoxLayout(parent)
        
        # Documentation section
        doc_group = QGroupBox("System Documentation")
        doc_layout = QVBoxLayout()
        
        # Serial numbers
        serial_layout = QVBoxLayout()
        
        computer_serial_layout = QHBoxLayout()
        computer_serial_layout.addWidget(QLabel("Computer Serial:"))
        self.computer_serial_input = QLineEdit()
        self.computer_serial_input.setPlaceholderText("e.g., IPC427E-001234")
        computer_serial_layout.addWidget(self.computer_serial_input)
        serial_layout.addLayout(computer_serial_layout)
        
        old_drive_layout = QHBoxLayout()
        old_drive_layout.addWidget(QLabel("Old Drive Model/Serial:"))
        self.old_drive_input = QLineEdit()
        self.old_drive_input.setPlaceholderText("e.g., WD5000AAKX-001CA0/WD-WMAYUA123456")
        old_drive_layout.addWidget(self.old_drive_input)
        serial_layout.addLayout(old_drive_layout)
        
        new_drive_layout = QHBoxLayout()
        new_drive_layout.addWidget(QLabel("New SSD Model/Serial:"))
        self.new_drive_input = QLineEdit()
        self.new_drive_input.setPlaceholderText("e.g., Samsung 860 EVO/S4PTNF0MA12345")
        new_drive_layout.addWidget(self.new_drive_input)
        serial_layout.addLayout(new_drive_layout)
        
        doc_layout.addLayout(serial_layout)
        
        # Configuration details
        config_layout = QVBoxLayout()
        config_layout.addWidget(QLabel("Current Configuration:"))
        self.config_text = QTextEdit()
        self.config_text.setMaximumHeight(100)
        self.config_text.setPlaceholderText(
            "OS Version: Windows 10 LTSC 2019\n"
            "Installed Software: Siemens TIA Portal V16\n"
            "Network Settings: 192.168.214.35\n"
            "Machine Type: Boeing Riveter"
        )
        config_layout.addWidget(self.config_text)
        doc_layout.addLayout(config_layout)
        
        save_doc_button = QPushButton("Save Documentation")
        save_doc_button.clicked.connect(self.save_documentation)
        doc_layout.addWidget(save_doc_button)
        
        doc_group.setLayout(doc_layout)
        layout.addWidget(doc_group)
        
        # Hardware checklist section
        hardware_group = QGroupBox("Hardware Checklist")
        hardware_layout = QVBoxLayout()
        
        tools_layout = QVBoxLayout()
        tools_layout.addWidget(QLabel("Required Tools:"))
        
        self.tools_checklist = {
            'torx_t8': QCheckBox("Torx T8 driver"),
            'torx_t10': QCheckBox("Torx T10 driver"),
            'torx_t15': QCheckBox("Torx T15 driver"),
            'torx_t20': QCheckBox("Torx T20 driver"),
            'anti_static': QCheckBox("Anti-static wrist strap"),
            'cable_ties': QCheckBox("Cable ties/velcro"),
            'camera': QCheckBox("Camera for documentation")
        }
        
        for tool, checkbox in self.tools_checklist.items():
            tools_layout.addWidget(checkbox)
            checkbox.stateChanged.connect(self.update_checklist)
        
        hardware_layout.addLayout(tools_layout)
        
        # Safety checklist
        safety_layout = QVBoxLayout()
        safety_layout.addWidget(QLabel("Safety Steps:"))
        
        self.safety_checklist = {
            'power_off': QCheckBox("Power system off"),
            'disconnect_ac': QCheckBox("Disconnect AC power"),
            'discharge': QCheckBox("Press power button 10 seconds"),
            'wait_30': QCheckBox("Wait 30 seconds"),
            'grounded': QCheckBox("Properly grounded")
        }
        
        for step, checkbox in self.safety_checklist.items():
            safety_layout.addWidget(checkbox)
            checkbox.stateChanged.connect(self.update_safety)
        
        hardware_layout.addLayout(safety_layout)
        hardware_group.setLayout(hardware_layout)
        layout.addWidget(hardware_group)
        
        # Drive information section
        drive_group = QGroupBox("Drive Information")
        drive_layout = QVBoxLayout()
        
        # SSD selection
        ssd_layout = QHBoxLayout()
        ssd_layout.addWidget(QLabel("SSD Type:"))
        self.ssd_combo = QComboBox()
        self.ssd_combo.addItems([
            "Samsung 860 EVO 500GB",
            "Samsung 870 EVO 1TB",
            "Crucial MX500 500GB",
            "Intel 545s 512GB",
            "WD Blue 3D NAND 500GB"
        ])
        ssd_layout.addWidget(self.ssd_combo)
        drive_layout.addLayout(ssd_layout)
        
        # Interface info
        interface_layout = QHBoxLayout()
        interface_layout.addWidget(QLabel("Interface:"))
        self.interface_label = QLabel("SATA III (6 Gb/s)")
        self.interface_label.setStyleSheet("font-weight: bold;")
        interface_layout.addWidget(self.interface_label)
        drive_layout.addLayout(interface_layout)
        
        # Form factor
        form_layout = QHBoxLayout()
        form_layout.addWidget(QLabel("Form Factor:"))
        self.form_factor_label = QLabel("2.5\" (Standard for IPC)")
        self.form_factor_label.setStyleSheet("font-weight: bold;")
        form_layout.addWidget(self.form_factor_label)
        drive_layout.addLayout(form_layout)
        
        drive_group.setLayout(drive_layout)
        layout.addWidget(drive_group)
        
        # Installation process section
        install_group = QGroupBox("Installation Process")
        install_layout = QVBoxLayout()
        
        # Current step display
        self.current_step_label = QLabel("Current Step: Not Started")
        self.current_step_label.setFont(QFont("Arial", 12, QFont.Bold))
        install_layout.addWidget(self.current_step_label)
        
        # Process buttons
        process_buttons = [
            ("Start Documentation", self.start_documentation),
            ("Power Down System", self.power_down_system),
            ("Remove Old Drive", self.remove_old_drive),
            ("Install New SSD", self.install_new_ssd),
            ("Check BIOS Detection", self.check_bios),
            ("Restore System", self.restore_system),
            ("Test Functionality", self.test_functionality)
        ]
        
        for button_text, handler in process_buttons:
            button = QPushButton(button_text)
            button.clicked.connect(handler)
            install_layout.addWidget(button)
        
        install_group.setLayout(install_layout)
        layout.addWidget(install_group)
        
        # Performance testing section
        perf_group = QGroupBox("Performance Testing")
        perf_layout = QVBoxLayout()
        
        benchmark_button = QPushButton("Run Performance Benchmark")
        benchmark_button.clicked.connect(self.run_benchmark)
        perf_layout.addWidget(benchmark_button)
        
        self.benchmark_results = QTextEdit()
        self.benchmark_results.setReadOnly(True)
        self.benchmark_results.setMaximumHeight(100)
        perf_layout.addWidget(self.benchmark_results)
        
        optimization_button = QPushButton("Apply SSD Optimizations")
        optimization_button.clicked.connect(self.apply_optimizations)
        perf_layout.addWidget(optimization_button)
        
        perf_group.setLayout(perf_layout)
        layout.addWidget(perf_group)
        
        # Troubleshooting section
        trouble_group = QGroupBox("Troubleshooting")
        trouble_layout = QVBoxLayout()
        
        self.issue_combo = QComboBox()
        self.issue_combo.addItems([
            "Drive not detected in BIOS",
            "Boot failure after installation",
            "Poor performance",
            "SMART errors",
            "Connection issues"
        ])
        trouble_layout.addWidget(self.issue_combo)
        
        troubleshoot_button = QPushButton("Get Troubleshooting Steps")
        troubleshoot_button.clicked.connect(self.show_troubleshooting)
        trouble_layout.addWidget(troubleshoot_button)
        
        self.troubleshooting_text = QTextEdit()
        self.troubleshooting_text.setReadOnly(True)
        self.troubleshooting_text.setMaximumHeight(100)
        trouble_layout.addWidget(self.troubleshooting_text)
        
        trouble_group.setLayout(trouble_layout)
        layout.addWidget(trouble_group)
    
    def save_documentation(self):
        """Save current documentation"""
        self.documentation = {
            'computer_serial': self.computer_serial_input.text(),
            'old_drive': self.old_drive_input.text(),
            'new_drive': self.new_drive_input.text(),
            'configuration': self.config_text.toPlainText(),
            'timestamp': datetime.now()
        }
        
        # Mark task complete
        self.task_widgets.get("documentation_preparation").set_completed(True)
        self.current_step_label.setText("Current Step: Documentation Complete")
        
        QMessageBox.information(self, "Documentation Saved",
                              "System documentation has been saved.")
    
    def update_checklist(self):
        """Update hardware checklist"""
        all_checked = all(cb.isChecked() for cb in self.tools_checklist.values())
        if all_checked:
            self.hardware_checklist.append("Tools ready")
    
    def update_safety(self):
        """Update safety checklist"""
        all_checked = all(cb.isChecked() for cb in self.safety_checklist.values())
        if all_checked:
            self.task_widgets.get("safe_shutdown").set_completed(True)
            self.current_step_label.setText("Current Step: System Powered Down")
    
    def start_documentation(self):
        """Start documentation process"""
        self.current_step_label.setText("Current Step: Documenting System")
        QMessageBox.information(self, "Documentation",
                              "Please fill in all system information before proceeding.")
    
    def power_down_system(self):
        """Simulate system power down"""
        if not all(cb.isChecked() for cb in self.safety_checklist.values()):
            QMessageBox.warning(self, "Safety Check",
                              "Please complete all safety steps before proceeding.")
            return
        
        self.current_step_label.setText("Current Step: System Safely Powered Down")
        QMessageBox.information(self, "Power Down",
                              "System has been safely powered down.\n"
                              "Ready for hardware replacement.")
    
    def remove_old_drive(self):
        """Simulate drive removal"""
        self.current_step_label.setText("Current Step: Removing Old Drive")
        
        steps = [
            "Case opened with appropriate Torx driver",
            "Drive bay located",
            "SATA cables disconnected",
            "Mounting screws removed",
            "Drive safely removed"
        ]
        
        result = "\n".join([f"✓ {step}" for step in steps])
        
        QMessageBox.information(self, "Drive Removal", 
                              f"Old drive removal complete:\n\n{result}")
        
        self.task_widgets.get("drive_removal").set_completed(True)
    
    def install_new_ssd(self):
        """Simulate SSD installation"""
        self.current_step_label.setText("Current Step: Installing New SSD")
        
        selected_ssd = self.ssd_combo.currentText()
        
        steps = [
            f"Installed {selected_ssd}",
            "Secured with original Torx screws",
            "SATA data cable connected (red stripe = pin 1)",
            "SATA power cable connected",
            "Cables properly routed and secured"
        ]
        
        result = "\n".join([f"✓ {step}" for step in steps])
        
        QMessageBox.information(self, "SSD Installation",
                              f"SSD installation complete:\n\n{result}")
        
        self.task_widgets.get("ssd_installation").set_completed(True)
    
    def check_bios(self):
        """Simulate BIOS verification"""
        self.current_step_label.setText("Current Step: Verifying BIOS Detection")
        
        bios_info = f"""
BIOS Detection Results:
✓ New SSD detected: {self.ssd_combo.currentText()}
✓ SATA mode: AHCI
✓ Boot order: Correct
✓ Secure Boot: Disabled
✓ Fast Boot: Enabled
        """
        
        QMessageBox.information(self, "BIOS Verification", bios_info)
        
        self.task_widgets.get("bios_verification").set_completed(True)
    
    def restore_system(self):
        """Simulate system restoration"""
        self.current_step_label.setText("Current Step: Restoring System")
        
        QMessageBox.information(self, "System Restoration",
                              "System restoration from backup initiated.\n"
                              "This process typically takes 30-60 minutes.\n\n"
                              "Status: Restoration complete successfully.")
        
        self.task_widgets.get("system_restoration").set_completed(True)
    
    def test_functionality(self):
        """Test system functionality"""
        self.current_step_label.setText("Current Step: Testing Functionality")
        
        test_results = """
Functionality Test Results:
✓ Windows booted successfully
✓ All devices recognized
✓ Network connectivity verified
✓ Machine control software operational
✓ Performance within specifications
        """
        
        QMessageBox.information(self, "Functionality Test", test_results)
        
        self.task_widgets.get("post_installation_testing").set_completed(True)
        self.current_step_label.setText("Current Step: Replacement Complete")
    
    def run_benchmark(self):
        """Simulate performance benchmark"""
        results = f"""
Performance Benchmark Results:

Sequential Read: 550 MB/s
Sequential Write: 520 MB/s
Random Read (4K): 95,000 IOPS
Random Write (4K): 88,000 IOPS

Old HDD Performance:
Sequential Read: 120 MB/s
Sequential Write: 110 MB/s

Improvement: 458% faster
        """
        
        self.benchmark_results.setText(results)
        self.performance_results = {'benchmark_complete': True}
    
    def apply_optimizations(self):
        """Apply SSD optimizations"""
        optimizations = """
SSD Optimizations Applied:
✓ TRIM enabled
✓ Superfetch disabled
✓ Prefetch disabled
✓ Write caching enabled
✓ Power management optimized
✓ Partition alignment verified
        """
        
        self.benchmark_results.append("\n" + optimizations)
        QMessageBox.information(self, "Optimizations",
                              "SSD optimizations have been applied successfully.")
    
    def show_troubleshooting(self):
        """Show troubleshooting steps"""
        issue = self.issue_combo.currentText()
        
        troubleshooting_guides = {
            "Drive not detected in BIOS": """
1. Verify power connection
2. Check SATA cable orientation
3. Try different SATA port
4. Update BIOS firmware
5. Test with different SATA cable
            """,
            "Boot failure after installation": """
1. Check boot order in BIOS
2. Verify AHCI mode enabled
3. Rebuild BCD:
   bootrec /fixmbr
   bootrec /fixboot
   bootrec /rebuildbcd
4. Check for secure boot conflicts
            """,
            "Poor performance": """
1. Enable AHCI (not IDE mode)
2. Verify SATA port speed
3. Align SSD partitions
4. Update SSD firmware
5. Check for background processes
            """,
            "SMART errors": """
1. Check drive health utility
2. Backup data immediately
3. Run manufacturer diagnostics
4. Consider warranty replacement
5. Monitor temperature
            """,
            "Connection issues": """
1. Reseat all connections
2. Check cable integrity
3. Try different SATA port
4. Verify power cable connection
5. Test with known good cables
            """
        }
        
        steps = troubleshooting_guides.get(issue, "No troubleshooting guide available.")
        self.troubleshooting_text.setText(steps)
    
    def validate_task(self, task_id: str) -> bool:
        """Validate specific task completion"""
        if task_id == "documentation_preparation":
            return bool(self.documentation)
        
        elif task_id == "safe_shutdown":
            return all(cb.isChecked() for cb in self.safety_checklist.values())
        
        elif task_id == "drive_removal":
            return "Removing Old Drive" in self.current_step_label.text()
        
        elif task_id == "ssd_installation":
            return "Installing New SSD" in self.current_step_label.text()
        
        elif task_id == "bios_verification":
            return "BIOS Detection" in self.current_step_label.text()
        
        elif task_id == "system_restoration":
            return "Restoring System" in self.current_step_label.text()
        
        elif task_id == "post_installation_testing":
            return "Replacement Complete" in self.current_step_label.text()
        
        return True
    
    def get_additional_resources(self):
        """Get additional resources for this module"""
        return {
            "documents": [
                {
                    "title": "Drive Replacement Guide",
                    "path": "resources/drive_replacement_guide.md",
                    "type": "markdown"
                }
            ],
            "links": [
                {
                    "title": "SSD Optimization Guide",
                    "url": "https://docs.microsoft.com/en-us/windows-hardware/drivers/storage/nvm-express",
                    "description": "Microsoft NVMe and SSD optimization documentation"
                }
            ],
            "tips": [
                "Always ground yourself before handling components",
                "Handle drives by edges only",
                "Never force connections",
                "Keep original screws organized",
                "Document cable routing with photos",
                "Test drive before final assembly"
            ],
            "torx_sizes": {
                "T8": "Smallest screws",
                "T10": "Drive mounting screws",
                "T15": "Case screws",
                "T20": "Larger case screws"
            }
        }

# Export the module class
MODULE_CLASS = DriveReplacementModule