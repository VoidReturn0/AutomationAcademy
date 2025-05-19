#!/usr/bin/env python3
"""
Backup/Restore Operations Training Module
Interactive module for teaching Paragon backup and restore procedures
"""

import os
import subprocess
import re
from datetime import datetime
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QLineEdit, QMessageBox, QGroupBox, QCheckBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QSpinBox,
    QComboBox, QRadioButton, QButtonGroup, QProgressBar,
    QFileDialog, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt, QTimer, Signal, QThread
from PySide6.QtGui import QFont, QColor
from training_module import TrainingModule

class BackupSimulator(QThread):
    """Simulates backup operation with progress updates"""
    progress_updated = Signal(int)
    status_updated = Signal(str)
    backup_complete = Signal(bool, str)
    
    def __init__(self, backup_config):
        super().__init__()
        self.backup_config = backup_config
        
    def run(self):
        """Simulate backup process"""
        try:
            # Simulate backup stages
            stages = [
                ("Initializing backup...", 10),
                ("Reading system partitions...", 20),
                ("Creating backup image...", 60),
                ("Compressing data...", 80),
                ("Verifying backup...", 95),
                ("Finalizing backup...", 100)
            ]
            
            for status, progress in stages:
                self.status_updated.emit(status)
                self.progress_updated.emit(progress)
                self.msleep(1000)  # Simulate work
            
            # Generate backup filename
            filename = self.generate_backup_filename()
            self.backup_complete.emit(True, filename)
            
        except Exception as e:
            self.backup_complete.emit(False, str(e))
    
    def generate_backup_filename(self):
        """Generate filename following Broetje naming convention"""
        machine_id = self.backup_config.get('machine_id', 'TEST001')
        backup_type = self.backup_config.get('type', 'NC')
        date_str = datetime.now().strftime('%Y%m%d')
        return f"{machine_id}_{backup_type}_{date_str}.pfi"

class BackupRestoreModule(TrainingModule):
    """Backup/Restore Operations Training Module"""
    
    def __init__(self, module_data, user_data, db_manager=None):
        self.db_manager = db_manager
        self.backup_history = []
        self.naming_examples = []
        super().__init__(module_data, user_data)
        
    def get_learning_objectives(self) -> list:
        return [
            "Create system backups using Paragon",
            "Follow Broetje naming conventions",
            "Restore systems from backups",
            "Verify backup integrity"
        ]
    
    def get_tasks(self) -> list:
        return self.module_data.get('tasks', [])
    
    # Remove the custom setup_overview_tab - it's causing issues
        
    def setup_custom_ui(self, parent):
        """Setup module-specific UI elements"""
        layout = QVBoxLayout(parent)
        
        # Naming convention section
        naming_group = QGroupBox("Broetje Naming Convention")
        naming_layout = QVBoxLayout()
        
        convention_label = QLabel("[Machine#]_[Type]_[Date YYYYMMDD]")
        convention_label.setFont(QFont("Consolas", 12, QFont.Bold))
        naming_layout.addWidget(convention_label)
        
        # Machine ID input
        machine_layout = QHBoxLayout()
        machine_layout.addWidget(QLabel("Machine ID:"))
        self.machine_id_input = QLineEdit()
        self.machine_id_input.setPlaceholderText("e.g., AP1741_R1")
        machine_layout.addWidget(self.machine_id_input)
        naming_layout.addLayout(machine_layout)
        
        # Backup type selection
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Backup Type:"))
        self.backup_type_combo = QComboBox()
        self.backup_type_combo.addItems(["NC", "DD", "PLC", "S7", "HMI", "FULL"])
        type_layout.addWidget(self.backup_type_combo)
        naming_layout.addLayout(type_layout)
        
        # Generated filename display
        self.filename_label = QLabel()
        self.filename_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        naming_layout.addWidget(self.filename_label)
        
        # Update filename when inputs change
        self.machine_id_input.textChanged.connect(self.update_filename)
        self.backup_type_combo.currentTextChanged.connect(self.update_filename)
        
        # Practice naming button
        practice_button = QPushButton("Add to Naming Examples")
        practice_button.clicked.connect(self.add_naming_example)
        naming_layout.addWidget(practice_button)
        
        # Examples list
        self.examples_list = QListWidget()
        self.examples_list.setMaximumHeight(100)
        naming_layout.addWidget(self.examples_list)
        
        naming_group.setLayout(naming_layout)
        layout.addWidget(naming_group)
        
        # Backup configuration section
        backup_group = QGroupBox("Backup Configuration")
        backup_layout = QVBoxLayout()
        
        # Source selection
        source_layout = QHBoxLayout()
        source_layout.addWidget(QLabel("Source:"))
        self.source_combo = QComboBox()
        self.source_combo.addItems([
            "C: System Drive",
            "D: Data Drive", 
            "All Partitions",
            "Selected Files"
        ])
        source_layout.addWidget(self.source_combo)
        backup_layout.addLayout(source_layout)
        
        # Destination
        dest_layout = QHBoxLayout()
        dest_layout.addWidget(QLabel("Destination:"))
        self.destination_input = QLineEdit()
        self.destination_input.setPlaceholderText("\\\\Server\\Backups\\Customer\\Machine")
        dest_layout.addWidget(self.destination_input)
        
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browse_destination)
        dest_layout.addWidget(browse_button)
        backup_layout.addLayout(dest_layout)
        
        # Compression settings
        compression_layout = QHBoxLayout()
        compression_layout.addWidget(QLabel("Compression:"))
        self.compression_combo = QComboBox()
        self.compression_combo.addItems(["None", "Normal", "Maximum"])
        self.compression_combo.setCurrentIndex(1)
        compression_layout.addWidget(self.compression_combo)
        backup_layout.addLayout(compression_layout)
        
        # Options
        options_layout = QVBoxLayout()
        self.verify_check = QCheckBox("Verify after creation")
        self.verify_check.setChecked(True)
        options_layout.addWidget(self.verify_check)
        
        self.password_check = QCheckBox("Password protection")
        options_layout.addWidget(self.password_check)
        
        self.split_check = QCheckBox("Split backup (for USB/DVD)")
        options_layout.addWidget(self.split_check)
        
        backup_layout.addLayout(options_layout)
        
        # Backup comments
        comments_layout = QVBoxLayout()
        comments_layout.addWidget(QLabel("Backup Comments:"))
        self.comments_text = QTextEdit()
        self.comments_text.setMaximumHeight(80)
        self.comments_text.setPlaceholderText(
            "Machine ID: [Serial]\n"
            "Customer: [Name]\n"
            "Configuration: [Version]\n"
            "Purpose: [Reason]"
        )
        comments_layout.addWidget(self.comments_text)
        backup_layout.addLayout(comments_layout)
        
        # Execute backup button
        self.backup_button = QPushButton("Create Backup")
        self.backup_button.clicked.connect(self.create_backup)
        backup_layout.addWidget(self.backup_button)
        
        backup_group.setLayout(backup_layout)
        layout.addWidget(backup_group)
        
        # Progress section
        progress_group = QGroupBox("Backup/Restore Progress")
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel()
        progress_layout.addWidget(self.status_label)
        
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)
        
        # Recovery media section
        recovery_group = QGroupBox("Recovery Media Creation")
        recovery_layout = QVBoxLayout()
        
        media_layout = QHBoxLayout()
        media_layout.addWidget(QLabel("Media Type:"))
        self.media_type_combo = QComboBox()
        self.media_type_combo.addItems(["USB Device", "DVD", "ISO File"])
        media_layout.addWidget(self.media_type_combo)
        recovery_layout.addLayout(media_layout)
        
        # Driver inclusion
        self.include_drivers_check = QCheckBox("Include network drivers")
        self.include_drivers_check.setChecked(True)
        recovery_layout.addWidget(self.include_drivers_check)
        
        self.include_backup_check = QCheckBox("Include backup files")
        recovery_layout.addWidget(self.include_backup_check)
        
        create_media_button = QPushButton("Create Recovery Media")
        create_media_button.clicked.connect(self.create_recovery_media)
        recovery_layout.addWidget(create_media_button)
        
        recovery_group.setLayout(recovery_layout)
        layout.addWidget(recovery_group)
        
        # Backup history section
        history_group = QGroupBox("Backup History")
        history_layout = QVBoxLayout()
        
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels([
            "Filename", "Type", "Date", "Size", "Status"
        ])
        self.history_table.horizontalHeader().setStretchLastSection(True)
        history_layout.addWidget(self.history_table)
        
        history_buttons_layout = QHBoxLayout()
        verify_backup_button = QPushButton("Verify Selected")
        verify_backup_button.clicked.connect(self.verify_backup)
        history_buttons_layout.addWidget(verify_backup_button)
        
        restore_button = QPushButton("Restore Selected")
        restore_button.clicked.connect(self.restore_backup)
        history_buttons_layout.addWidget(restore_button)
        
        history_buttons_layout.addStretch()
        history_layout.addLayout(history_buttons_layout)
        
        history_group.setLayout(history_layout)
        layout.addWidget(history_group)
        
        # Documentation section
        doc_group = QGroupBox("Documentation")
        doc_layout = QVBoxLayout()
        
        self.doc_text = QTextEdit()
        self.doc_text.setMaximumHeight(150)
        self.doc_text.setPlaceholderText(
            "Document your backup/restore procedures here..."
        )
        doc_layout.addWidget(self.doc_text)
        
        save_doc_button = QPushButton("Save Documentation")
        save_doc_button.clicked.connect(self.save_documentation)
        doc_layout.addWidget(save_doc_button)
        
        doc_group.setLayout(doc_layout)
        layout.addWidget(doc_group)
    
    def update_filename(self):
        """Update filename based on naming convention"""
        machine_id = self.machine_id_input.text().strip()
        backup_type = self.backup_type_combo.currentText()
        
        if machine_id:
            date_str = datetime.now().strftime('%Y%m%d')
            filename = f"{machine_id}_{backup_type}_{date_str}.pfi"
            self.filename_label.setText(f"Filename: {filename}")
        else:
            self.filename_label.setText("Filename: ")
    
    def add_naming_example(self):
        """Add current naming example to list"""
        machine_id = self.machine_id_input.text().strip()
        backup_type = self.backup_type_combo.currentText()
        
        if machine_id:
            date_str = datetime.now().strftime('%Y%m%d')
            example = f"{machine_id}_{backup_type}_{date_str}"
            self.naming_examples.append(example)
            self.examples_list.addItem(example)
            
            # Mark task complete if enough examples
            if len(self.naming_examples) >= 3:
                self.task_widgets.get("naming_convention").set_completed(True)
    
    def browse_destination(self):
        """Browse for backup destination"""
        path = QFileDialog.getExistingDirectory(
            self, "Select Backup Destination",
            str(Path.home())
        )
        if path:
            self.destination_input.setText(path)
    
    def create_backup(self):
        """Create a backup (simulated)"""
        if not self.machine_id_input.text() or not self.destination_input.text():
            QMessageBox.warning(self, "Missing Information",
                              "Please fill in all required fields.")
            return
        
        # Show progress
        self.progress_bar.setVisible(True)
        self.backup_button.setEnabled(False)
        
        # Create backup configuration
        backup_config = {
            'machine_id': self.machine_id_input.text(),
            'type': self.backup_type_combo.currentText(),
            'source': self.source_combo.currentText(),
            'destination': self.destination_input.text(),
            'compression': self.compression_combo.currentText(),
            'verify': self.verify_check.isChecked(),
            'comments': self.comments_text.toPlainText()
        }
        
        # Start backup simulation
        self.backup_thread = BackupSimulator(backup_config)
        self.backup_thread.progress_updated.connect(self.update_progress)
        self.backup_thread.status_updated.connect(self.update_status)
        self.backup_thread.backup_complete.connect(self.backup_complete)
        self.backup_thread.start()
    
    def update_progress(self, value):
        """Update progress bar"""
        self.progress_bar.setValue(value)
    
    def update_status(self, status):
        """Update status label"""
        self.status_label.setText(status)
    
    def backup_complete(self, success, result):
        """Handle backup completion"""
        self.backup_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        if success:
            # Add to history
            row = self.history_table.rowCount()
            self.history_table.insertRow(row)
            
            self.history_table.setItem(row, 0, QTableWidgetItem(result))
            self.history_table.setItem(row, 1, QTableWidgetItem(self.backup_type_combo.currentText()))
            self.history_table.setItem(row, 2, QTableWidgetItem(datetime.now().strftime('%Y-%m-%d %H:%M')))
            self.history_table.setItem(row, 3, QTableWidgetItem("45.2 GB"))  # Simulated size
            self.history_table.setItem(row, 4, QTableWidgetItem("Completed"))
            
            # Store in history
            self.backup_history.append({
                'filename': result,
                'type': self.backup_type_combo.currentText(),
                'date': datetime.now(),
                'size': "45.2 GB",
                'status': "Completed",
                'config': {
                    'source': self.source_combo.currentText(),
                    'destination': self.destination_input.text(),
                    'compression': self.compression_combo.currentText()
                }
            })
            
            # Mark task complete
            self.task_widgets.get("create_system_backup").set_completed(True)
            
            QMessageBox.information(self, "Backup Complete",
                                  f"Backup created successfully:\n{result}")
        else:
            QMessageBox.critical(self, "Backup Failed", f"Error: {result}")
    
    def verify_backup(self):
        """Verify selected backup"""
        current_row = self.history_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a backup to verify.")
            return
        
        filename = self.history_table.item(current_row, 0).text()
        
        # Simulate verification
        self.status_label.setText(f"Verifying {filename}...")
        QTimer.singleShot(2000, lambda: self.verification_complete(filename))
    
    def verification_complete(self, filename):
        """Handle verification completion"""
        self.status_label.setText(f"Verification of {filename} completed successfully.")
        self.task_widgets.get("verify_backup").set_completed(True)
        QMessageBox.information(self, "Verification Complete",
                              f"Backup {filename} verified successfully.")
    
    def restore_backup(self):
        """Restore selected backup (simulated)"""
        current_row = self.history_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a backup to restore.")
            return
        
        filename = self.history_table.item(current_row, 0).text()
        
        # Confirm restoration
        reply = QMessageBox.question(self, "Confirm Restoration",
                                   f"Are you sure you want to restore {filename}?\n"
                                   "This will overwrite the target drive.",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Simulate restoration
            self.progress_bar.setVisible(True)
            self.status_label.setText(f"Restoring {filename}...")
            
            # Simulate progress
            for i in range(0, 101, 10):
                QTimer.singleShot(i * 100, lambda v=i: self.progress_bar.setValue(v))
            
            QTimer.singleShot(1100, lambda: self.restoration_complete(filename))
    
    def restoration_complete(self, filename):
        """Handle restoration completion"""
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"Restoration of {filename} completed successfully.")
        self.task_widgets.get("restore_to_test_drive").set_completed(True)
        QMessageBox.information(self, "Restoration Complete",
                              f"Backup {filename} restored successfully.")
    
    def create_recovery_media(self):
        """Create recovery media (simulated)"""
        media_type = self.media_type_combo.currentText()
        
        # Simulate creation
        self.status_label.setText(f"Creating {media_type} recovery media...")
        QTimer.singleShot(3000, lambda: self.recovery_media_complete(media_type))
    
    def recovery_media_complete(self, media_type):
        """Handle recovery media creation completion"""
        self.status_label.setText(f"{media_type} recovery media created successfully.")
        self.task_widgets.get("create_recovery_media").set_completed(True)
        QMessageBox.information(self, "Media Created",
                              f"{media_type} recovery media created successfully.")
    
    def save_documentation(self):
        """Save documentation to file"""
        if not self.doc_text.toPlainText():
            QMessageBox.warning(self, "No Documentation",
                              "Please enter documentation before saving.")
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Documentation",
            f"backup_procedures_{datetime.now().strftime('%Y%m%d')}.txt",
            "Text Files (*.txt)"
        )
        
        if filename:
            with open(filename, 'w') as f:
                f.write("Broetje Automation Backup/Restore Documentation\n")
                f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("="*50 + "\n\n")
                f.write(self.doc_text.toPlainText())
                
                # Add backup history
                f.write("\n\nBackup History:\n")
                f.write("-"*30 + "\n")
                for backup in self.backup_history:
                    f.write(f"Filename: {backup['filename']}\n")
                    f.write(f"Type: {backup['type']}\n")
                    f.write(f"Date: {backup['date'].strftime('%Y-%m-%d %H:%M')}\n")
                    f.write(f"Size: {backup['size']}\n")
                    f.write(f"Status: {backup['status']}\n")
                    f.write("-"*30 + "\n")
            
            self.task_widgets.get("document_procedures").set_completed(True)
            QMessageBox.information(self, "Documentation Saved",
                                  f"Documentation saved to {filename}")
    
    def validate_task(self, task_id: str) -> bool:
        """Validate specific task completion"""
        if task_id == "launch_paragon":
            # Check if screenshot exists
            return self.check_screenshot_exists(task_id)
        
        elif task_id == "naming_convention":
            # Check if enough naming examples created
            return len(self.naming_examples) >= 3
        
        elif task_id == "create_system_backup":
            # Check if backup was created
            return len(self.backup_history) > 0
        
        elif task_id == "verify_backup":
            # Check if verification performed
            return "Verification" in self.status_label.text()
        
        elif task_id == "create_recovery_media":
            # Check if recovery media created
            return "recovery media created" in self.status_label.text()
        
        elif task_id == "restore_to_test_drive":
            # Check if restoration performed
            return "Restoration" in self.status_label.text()
        
        elif task_id == "document_procedures":
            # Check if documentation exists
            return len(self.doc_text.toPlainText()) > 50
        
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
                    "title": "Backup/Restore Guide",
                    "path": "resources/backup_restore_guide.md",
                    "type": "markdown"
                }
            ],
            "links": [
                {
                    "title": "Paragon Documentation",
                    "url": "https://www.paragon-software.com/business/products/technician/",
                    "description": "Official Paragon Backup & Recovery documentation"
                }
            ],
            "tips": [
                "Always verify backups after creation",
                "Use consistent naming conventions",
                "Test restore procedures regularly",
                "Keep multiple backup versions",
                "Document all procedures thoroughly",
                "Store backups in multiple locations"
            ],
            "templates": {
                "backup_log": """
Customer: ________________  Machine: ________________
Backup Type: _____________  Date: ____________________

Source Information:
- Drive Model: ____________  Serial: _________________
- Total Size: _____________  OS Version: _____________

Backup Details:
- Filename: ________________________________________
- Location: ________________________________________
- Compression: _____________________________________
- Duration: ________________________________________
- Verification: Pass/Fail

Technician: ________________  Verified by: ____________
                """
            }
        }

# Export the module class
MODULE_CLASS = BackupRestoreModule