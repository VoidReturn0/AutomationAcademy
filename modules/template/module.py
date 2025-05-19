#!/usr/bin/env python3
"""
Module Template
Base template for creating new training modules
"""

from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QTextEdit, QListWidget, QListWidgetItem,
    QMessageBox, QLineEdit, QComboBox, QSpinBox, QCheckBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from pathlib import Path
from training_module import TrainingModule

class TemplateModule(TrainingModule):
    """Template module implementation"""
    
    def __init__(self, parent=None):
        super().__init__(
            module_id="module_template",
            title="Module Template",
            parent=parent
        )
        self.setup_ui()
    
    def setup_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Module header
        header_label = QLabel("Module Template")
        header_label.setFont(QFont("Arial", 24, QFont.Bold))
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)
        
        # Introduction section
        intro_group = QGroupBox("Introduction")
        intro_layout = QVBoxLayout()
        
        intro_text = QTextEdit()
        intro_text.setReadOnly(True)
        intro_text.setPlainText("""
This is a template module for creating new training modules.

Key Components:
1. Module metadata (metadata.json)
2. Module implementation (module.py)
3. Resources directory
4. Custom UI elements
5. Task validation logic

Use this template as a starting point for new modules.
        """)
        intro_text.setMaximumHeight(200)
        intro_layout.addWidget(intro_text)
        
        intro_group.setLayout(intro_layout)
        layout.addWidget(intro_group)
        
        # Interactive section
        self.setup_interactive_section(layout)
        
        # Practice section
        self.setup_practice_section(layout)
        
        # Add stretch to push content to top
        layout.addStretch()
        
        # Set the layout
        self.setLayout(layout)
    
    def setup_interactive_section(self, parent_layout):
        """Setup interactive elements"""
        interactive_group = QGroupBox("Interactive Section")
        layout = QVBoxLayout()
        
        # Example input field
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Input:"))
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Enter value here")
        input_layout.addWidget(self.input_field)
        layout.addLayout(input_layout)
        
        # Example dropdown
        dropdown_layout = QHBoxLayout()
        dropdown_layout.addWidget(QLabel("Options:"))
        self.dropdown = QComboBox()
        self.dropdown.addItems(["Option 1", "Option 2", "Option 3"])
        dropdown_layout.addWidget(self.dropdown)
        layout.addLayout(dropdown_layout)
        
        # Example checkbox
        self.checkbox = QCheckBox("Enable advanced features")
        layout.addWidget(self.checkbox)
        
        # Action button
        self.action_button = QPushButton("Perform Action")
        self.action_button.clicked.connect(self.perform_action)
        layout.addWidget(self.action_button)
        
        # Result display
        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        self.result_display.setMaximumHeight(100)
        layout.addWidget(self.result_display)
        
        interactive_group.setLayout(layout)
        parent_layout.addWidget(interactive_group)
    
    def setup_practice_section(self, parent_layout):
        """Setup practice exercises"""
        practice_group = QGroupBox("Practice Exercises")
        layout = QVBoxLayout()
        
        # Exercise list
        self.exercise_list = QListWidget()
        self.exercise_list.addItem("Exercise 1: Basic Task")
        self.exercise_list.addItem("Exercise 2: Intermediate Task")
        self.exercise_list.addItem("Exercise 3: Advanced Task")
        self.exercise_list.itemClicked.connect(self.select_exercise)
        layout.addWidget(self.exercise_list)
        
        # Exercise description
        self.exercise_desc = QTextEdit()
        self.exercise_desc.setReadOnly(True)
        self.exercise_desc.setMaximumHeight(100)
        layout.addWidget(self.exercise_desc)
        
        # Start exercise button
        self.start_button = QPushButton("Start Exercise")
        self.start_button.clicked.connect(self.start_exercise)
        layout.addWidget(self.start_button)
        
        practice_group.setLayout(layout)
        parent_layout.addWidget(practice_group)
    
    def perform_action(self):
        """Handle action button click"""
        input_value = self.input_field.text()
        selected_option = self.dropdown.currentText()
        advanced_enabled = self.checkbox.isChecked()
        
        result = f"Action performed:\n"
        result += f"Input: {input_value}\n"
        result += f"Option: {selected_option}\n"
        result += f"Advanced: {advanced_enabled}"
        
        self.result_display.setPlainText(result)
        
        # Example of marking a task complete
        self.mark_task_complete("task_1")
    
    def select_exercise(self, item):
        """Handle exercise selection"""
        exercise_descriptions = {
            "Exercise 1: Basic Task": "Complete the basic configuration steps",
            "Exercise 2: Intermediate Task": "Implement the intermediate features",
            "Exercise 3: Advanced Task": "Solve the advanced challenge"
        }
        
        desc = exercise_descriptions.get(item.text(), "No description available")
        self.exercise_desc.setPlainText(desc)
    
    def start_exercise(self):
        """Start the selected exercise"""
        current_item = self.exercise_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select an exercise first")
            return
        
        exercise_name = current_item.text()
        QMessageBox.information(self, "Exercise Started", 
                              f"Starting {exercise_name}\n\nFollow the instructions to complete the task.")
    
    def validate_task(self, task_id: str) -> bool:
        """Validate task completion"""
        # Implement custom validation logic for each task
        if task_id == "task_1":
            # Example validation: check if input field has value
            return bool(self.input_field.text())
        
        return False
    
    def get_task_help(self, task_id: str) -> str:
        """Get help text for specific task"""
        help_texts = {
            "task_1": "Enter any value in the input field and click 'Perform Action' to complete this task."
        }
        
        return help_texts.get(task_id, "No help available for this task.")

# Module registration
def get_module():
    """Factory function to create module instance"""
    return TemplateModule