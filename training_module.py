#!/usr/bin/env python3
"""
Training Modules
Base classes and module registry for all training modules
"""

import json
import time
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QTextEdit, QLineEdit, QCheckBox, QProgressBar, QGroupBox, QListWidget,
    QListWidgetItem, QScrollArea, QFrame, QTextBrowser, QMessageBox,
    QFileDialog, QSpinBox, QComboBox, QTimeEdit, QTabWidget
)
from PySide6.QtCore import Qt, QTimer, Signal, QTime
from PySide6.QtGui import QFont, QPixmap, QPainter, QPen

class TaskWidget(QWidget):
    """Widget for individual training tasks"""
    task_completed = Signal(str, bool)
    screenshot_requested = Signal(str)
    
    def __init__(self, task_id: str, task_data: Dict):
        super().__init__()
        self.task_id = task_id
        self.task_data = task_data
        self.completed = False
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Task header
        header_frame = QFrame()
        header_frame.setStyleSheet("QFrame { border: 1px solid #bdc3c7; border-radius: 4px; padding: 5px; }")
        header_layout = QHBoxLayout(header_frame)
        
        # Task name
        task_label = QLabel(self.task_data['name'])
        task_label.setFont(QFont("Arial", 12, QFont.Bold))
        header_layout.addWidget(task_label)
        
        header_layout.addStretch()
        
        # Required indicator
        if self.task_data.get('required', True):
            required_label = QLabel("REQUIRED")
            required_label.setStyleSheet("color: red; font-weight: bold;")
            header_layout.addWidget(required_label)
        
        layout.addWidget(header_frame)
        
        # Task description
        desc_text = QTextBrowser()
        desc_text.setMaximumHeight(100)
        desc_text.setHtml(self.task_data.get('description', ''))
        layout.addWidget(desc_text)
        
        # Instructions
        if 'instructions' in self.task_data:
            instructions_group = QGroupBox("Instructions")
            instructions_layout = QVBoxLayout(instructions_group)
            
            for step in self.task_data['instructions']:
                step_label = QLabel(f"• {step}")
                step_label.setWordWrap(True)
                instructions_layout.addWidget(step_label)
            
            layout.addWidget(instructions_group)
        
        # Verification
        verification_group = QGroupBox("Verification")
        verification_layout = QHBoxLayout(verification_group)
        
        # Completion checkbox
        self.completion_checkbox = QCheckBox("Task Completed")
        self.completion_checkbox.stateChanged.connect(self.on_completion_changed)
        verification_layout.addWidget(self.completion_checkbox)
        
        # Screenshot button (if required)
        if self.task_data.get('screenshot_required', False):
            screenshot_button = QPushButton("Take Screenshot")
            screenshot_button.clicked.connect(self.request_screenshot)
            verification_layout.addWidget(screenshot_button)
        
        verification_layout.addStretch()
        layout.addWidget(verification_group)
        
        self.setLayout(layout)
    
    def on_completion_changed(self, state):
        """Handle completion checkbox change"""
        self.completed = state == Qt.Checked
        self.task_completed.emit(self.task_id, self.completed)
    
    def request_screenshot(self):
        """Request screenshot capture"""
        self.screenshot_requested.emit(self.task_id)
    
    def set_completed(self, completed: bool):
        """Set task completion status"""
        self.completed = completed
        self.completion_checkbox.setChecked(completed)

class DigitalSignaturePad(QWidget):
    """Simple digital signature capture widget"""
    signature_captured = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.signature_points = []
        self.drawing = False
        self.setFixedSize(400, 150)
        self.setStyleSheet("border: 1px solid #bdc3c7; background-color: white;")
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.signature_points.append([event.pos()])
    
    def mouseMoveEvent(self, event):
        if self.drawing:
            self.signature_points[-1].append(event.pos())
            self.update()
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = False
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QPen(Qt.black, 2))
        
        for stroke in self.signature_points:
            for i in range(1, len(stroke)):
                painter.drawLine(stroke[i-1], stroke[i])
    
    def clear_signature(self):
        """Clear the signature"""
        self.signature_points = []
        self.update()
    
    def save_signature(self) -> str:
        """Save signature and return base64 encoded string"""
        pixmap = QPixmap(self.size())
        pixmap.fill(Qt.white)
        painter = QPainter(pixmap)
        painter.setPen(QPen(Qt.black, 2))
        
        for stroke in self.signature_points:
            for i in range(1, len(stroke)):
                painter.drawLine(stroke[i-1], stroke[i])
        
        painter.end()
        
        # Convert pixmap to base64 string
        import io
        import base64
        
        buffer = io.BytesIO()
        pixmap.save(buffer, "PNG")
        buffer.seek(0)
        
        # Return base64 encoded signature
        return base64.b64encode(buffer.getvalue()).decode('utf-8')

class TrainingModule(QWidget):
    """Base class for training modules"""
    module_completed = Signal(str, dict)
    progress_updated = Signal(int)
    
    def __init__(self, module_data: Dict, user_data: Dict):
        super().__init__()
        self.module_data = module_data
        self.user_data = user_data
        self.tasks = {}
        self.start_time = datetime.now()
        self.elapsed_timer = QTimer()
        self.elapsed_timer.timeout.connect(self.update_elapsed_time)
        self.elapsed_timer.start(1000)  # Update every second
        self.setup_ui()
        self.load_tasks()
    
    def setup_ui(self):
        """Setup the module UI"""
        layout = QVBoxLayout()
        
        # Header
        header_group = QGroupBox()
        header_layout = QVBoxLayout(header_group)
        
        # Title and timer
        title_layout = QHBoxLayout()
        
        title_label = QLabel(self.module_data['name'])
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_layout.addWidget(title_label)
        
        title_layout.addStretch()
        
        # Timer
        timer_label = QLabel("Elapsed Time:")
        self.elapsed_time_label = QLabel("00:00:00")
        self.elapsed_time_label.setFont(QFont("Arial", 12, QFont.Bold))
        title_layout.addWidget(timer_label)
        title_layout.addWidget(self.elapsed_time_label)
        
        header_layout.addLayout(title_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        header_layout.addWidget(self.progress_bar)
        
        layout.addWidget(header_group)
        
        # Tabs for different sections
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Overview tab
        self.setup_overview_tab()
        
        # Tasks tab
        self.setup_tasks_tab()
        
        # Completion tab
        self.setup_completion_tab()
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        button_layout.addStretch()
        
        self.complete_button = QPushButton("Complete Module")
        self.complete_button.clicked.connect(self.complete_module)
        self.complete_button.setEnabled(False)
        button_layout.addWidget(self.complete_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def setup_overview_tab(self):
        """Setup overview tab"""
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        # Create content widget
        overview_widget = QWidget()
        layout = QVBoxLayout(overview_widget)
        layout.setSpacing(15)  # Add spacing between elements
        layout.setContentsMargins(20, 20, 20, 20)  # Add margins
        
        # Module description
        desc_group = QGroupBox("Module Description")
        desc_layout = QVBoxLayout(desc_group)
        desc_layout.setSpacing(10)
        
        desc_text = QTextBrowser()
        desc_text.setMaximumHeight(200)  # Limit height to prevent squishing
        desc_text.setHtml(f"""
        <h3>{self.module_data['name']}</h3>
        <p>{self.module_data.get('description', '')}</p>
        <p><strong>Estimated Duration:</strong> {self.module_data.get('estimated_duration', 0)} minutes</p>
        <p><strong>Prerequisites:</strong> {self.module_data.get('prerequisites', 'None')}</p>
        """)
        desc_layout.addWidget(desc_text)
        
        layout.addWidget(desc_group)
        
        # Learning objectives
        objectives_group = QGroupBox("Learning Objectives")
        objectives_layout = QVBoxLayout(objectives_group)
        objectives_layout.setSpacing(8)
        
        objectives = self.get_learning_objectives()
        for objective in objectives:
            obj_label = QLabel(f"• {objective}")
            obj_label.setWordWrap(True)
            obj_label.setMinimumHeight(25)  # Ensure minimum height for readability
            objectives_layout.addWidget(obj_label)
        
        layout.addWidget(objectives_group)
        
        layout.addStretch()
        
        # Set the content widget for the scroll area
        scroll_area.setWidget(overview_widget)
        
        # Add the scroll area to the tab widget
        self.tab_widget.addTab(scroll_area, "Overview")
    
    def setup_tasks_tab(self):
        """Setup tasks tab"""
        tasks_widget = QScrollArea()
        tasks_content = QWidget()
        self.tasks_layout = QVBoxLayout(tasks_content)
        
        tasks_widget.setWidget(tasks_content)
        tasks_widget.setWidgetResizable(True)
        
        self.tab_widget.addTab(tasks_widget, "Tasks")
    
    def setup_completion_tab(self):
        """Setup completion tab"""
        completion_widget = QWidget()
        layout = QVBoxLayout(completion_widget)
        
        # Signature section
        signature_group = QGroupBox("Trainee Signature")
        signature_layout = QVBoxLayout(signature_group)
        
        instructions = QLabel("Please sign below to confirm completion of this training module:")
        signature_layout.addWidget(instructions)
        
        self.signature_pad = DigitalSignaturePad()
        signature_layout.addWidget(self.signature_pad)
        
        # Signature controls
        sig_controls = QHBoxLayout()
        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(self.signature_pad.clear_signature)
        sig_controls.addWidget(clear_button)
        sig_controls.addStretch()
        
        signature_layout.addLayout(sig_controls)
        layout.addWidget(signature_group)
        
        # Notes section
        notes_group = QGroupBox("Additional Notes")
        notes_layout = QVBoxLayout(notes_group)
        
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("Add any additional notes or comments...")
        self.notes_edit.setMaximumHeight(100)
        notes_layout.addWidget(self.notes_edit)
        
        layout.addWidget(notes_group)
        
        layout.addStretch()
        self.tab_widget.addTab(completion_widget, "Completion")
    
    def get_learning_objectives(self) -> List[str]:
        """Get learning objectives for the module"""
        return []
    
    def get_tasks(self) -> List[Dict]:
        """Get tasks for the module"""
        return []
    
    def load_tasks(self):
        """Load and display tasks"""
        task_definitions = self.get_tasks()
        
        for i, task_def in enumerate(task_definitions):
            task_widget = TaskWidget(f"task_{i}", task_def)
            task_widget.task_completed.connect(self.on_task_completed)
            task_widget.screenshot_requested.connect(self.on_screenshot_requested)
            
            self.tasks[f"task_{i}"] = {
                'widget': task_widget,
                'definition': task_def,
                'completed': False
            }
            
            self.tasks_layout.addWidget(task_widget)
        
        self.tasks_layout.addStretch()
        self.update_progress()
    
    def on_task_completed(self, task_id: str, completed: bool):
        """Handle task completion"""
        if task_id in self.tasks:
            self.tasks[task_id]['completed'] = completed
            self.update_progress()
    
    def on_screenshot_requested(self, task_id: str):
        """Handle screenshot request"""
        # This is handled by the module window
        pass
    
    def update_progress(self):
        """Update progress indicators"""
        total_tasks = len(self.tasks)
        completed_tasks = sum(1 for task in self.tasks.values() if task['completed'])
        
        if total_tasks > 0:
            progress = int((completed_tasks / total_tasks) * 100)
            self.progress_bar.setValue(progress)
            
            # Enable completion if all required tasks are done
            all_required_done = all(
                task['completed'] or not task['definition'].get('required', True)
                for task in self.tasks.values()
            )
            self.complete_button.setEnabled(all_required_done)
            
            self.progress_updated.emit(progress)
    
    def update_elapsed_time(self):
        """Update elapsed time display"""
        elapsed = datetime.now() - self.start_time
        hours, remainder = divmod(elapsed.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        self.elapsed_time_label.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
    
    def complete_module(self):
        """Complete the module"""
        # Validate completion
        signature_data = self.signature_pad.save_signature()
        notes = self.notes_edit.toPlainText()
        
        completion_data = {
            'user_id': self.user_data['id'],
            'module_name': self.module_data['name'],
            'completion_time': datetime.now().isoformat(),
            'elapsed_time': (datetime.now() - self.start_time).seconds,
            'tasks_completed': [
                task_id for task_id, task in self.tasks.items() 
                if task['completed']
            ],
            'signature': signature_data,
            'notes': notes,
            'score': self.calculate_score()
        }
        
        self.module_completed.emit(self.module_data['name'], completion_data)
    
    def calculate_score(self) -> int:
        """Calculate completion score"""
        total_tasks = len(self.tasks)
        completed_tasks = sum(1 for task in self.tasks.values() if task['completed'])
        
        if total_tasks > 0:
            return int((completed_tasks / total_tasks) * 100)
        return 0

# Example implementation for Network File Sharing module
class NetworkFileSharingModule(TrainingModule):
    """Network File Sharing & Mapping training module"""
    
    def get_learning_objectives(self) -> List[str]:
        return [
            "Understand network drive mapping concepts",
            "Map network drives using Windows Explorer",
            "Configure persistent drive mappings",
            "Access shared folders across the automation network",
            "Troubleshoot common network drive issues"
        ]
    
    def get_tasks(self) -> List[Dict]:
        return [
            {
                'name': 'Open Windows Explorer',
                'description': 'Navigate to and open Windows Explorer',
                'instructions': [
                    'Press Windows key + E to open Explorer',
                    'Alternatively, click the folder icon in the taskbar'
                ],
                'required': True,
                'screenshot_required': True
            },
            {
                'name': 'Access Map Network Drive',
                'description': 'Access the Map Network Drive function',
                'instructions': [
                    'Right-click on "This PC" in the left panel',
                    'Select "Map network drive..." from context menu',
                    'The Map Network Drive dialog should appear'
                ],
                'required': True,
                'screenshot_required': True
            },
            {
                'name': 'Map Production Network Drive',
                'description': 'Map the production network drive',
                'instructions': [
                    'Select drive letter (e.g., P:)',
                    'Enter folder path: \\\\192.168.214.10\\Production',
                    'Check "Reconnect at sign-in"',
                    'Click "Finish"'
                ],
                'required': True,
                'screenshot_required': True
            },
            {
                'name': 'Map Engineering Network Drive',
                'description': 'Map the engineering network drive',
                'instructions': [
                    'Repeat the process for engineering drive',
                    'Use drive letter E:',
                    'Enter path: \\\\192.168.213.15\\Engineering',
                    'Ensure persistence is enabled'
                ],
                'required': True,
                'screenshot_required': True
            },
            {
                'name': 'Verify Access',
                'description': 'Verify both network drives are accessible',
                'instructions': [
                    'Navigate to drive P: in Explorer',
                    'Confirm you can see production folders',
                    'Navigate to drive E:',
                    'Confirm engineering resources are visible'
                ],
                'required': True,
                'screenshot_required': True
            },
            {
                'name': 'Create Test File',
                'description': 'Create a test file on the production drive',
                'instructions': [
                    'Navigate to P:\\Test (create if needed)',
                    'Right-click and create a new text file',
                    'Name it: TestFile_[YourInitials]_[Date]',
                    'Add some content to verify write access'
                ],
                'required': False,
                'screenshot_required': True
            }
        ]

# Module registry
MODULE_REGISTRY = {}

def get_module_class(module_name: str):
    """Get module class by name"""
    import importlib
    import logging
    
    logger = logging.getLogger(__name__)
    
    # Try to get from registry cache first
    if module_name in MODULE_REGISTRY:
        return MODULE_REGISTRY[module_name]
    
    # Map module names to directory names or fallback modules
    module_dir_map = {
        'Network File Sharing & Mapping': 'network_file_sharing',
        'Command Line Network Diagnostics': 'cli_diagnostics',
        'IP Address Configuration': 'ip_configuration',
        'Hard Drive Management': 'fallback_modules',  # Use fallback
        'Backup/Restore Operations': 'backup_restore',
        'Hard Drive Replacement': 'drive_replacement',
        'Remote Access Configuration': 'remote_access',
        'Batch File Scripting': 'fallback_modules',  # Use fallback
        'PowerShell Scripting': 'powershell_scripting',
        'OneDrive Integration': 'fallback_modules'  # Use fallback
    }
    
    dir_name = module_dir_map.get(module_name)
    if not dir_name:
        logger.error(f"No directory mapping found for module: {module_name}")
        return None
    
    try:
        # Dynamically import the module
        if dir_name == 'fallback_modules':
            # Special handling for fallback modules
            import fallback_modules
            # Map module names to fallback classes
            fallback_map = {
                'Hard Drive Management': fallback_modules.HardDriveManagementModule,
                'Batch File Scripting': fallback_modules.BatchFileScriptingModule,
                'OneDrive Integration': fallback_modules.OneDriveIntegrationModule
            }
            if module_name in fallback_map:
                module_class = fallback_map[module_name]
                MODULE_REGISTRY[module_name] = module_class
                logger.info(f"Loaded fallback module class: {module_class.__name__} for {module_name}")
                return module_class
            else:
                logger.error(f"No fallback class found for {module_name}")
                return None
        else:
            module_path = f"modules.{dir_name}.module"
            imported_module = importlib.import_module(module_path)
            
            # Look for a class that extends TrainingModule
            for attr_name in dir(imported_module):
                attr = getattr(imported_module, attr_name)
                if isinstance(attr, type) and issubclass(attr, TrainingModule) and attr != TrainingModule:
                    MODULE_REGISTRY[module_name] = attr
                    logger.info(f"Loaded module class: {attr.__name__} for {module_name}")
                    return attr
            
            logger.error(f"No TrainingModule subclass found in {module_path}")
            return None
        
    except ImportError as e:
        logger.error(f"Failed to import module {module_name}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error loading module {module_name}: {e}")
        return None