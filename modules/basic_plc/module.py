from training_module import TrainingModule
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit
from PySide6.QtCore import Qt
import json
import os

class BasicPLCModule(TrainingModule):
    def __init__(self):
        super().__init__()
        self.module_id = "basic_plc"
        self.name = "Basic PLC Programming"
        self.description = "Introduction to PLC programming with ladder logic basics"
        self.load_metadata()
        
    def load_metadata(self):
        """Load module metadata from JSON file"""
        metadata_path = os.path.join(os.path.dirname(__file__), 'metadata.json')
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
                self.version = metadata.get('version', '1.0.0')
                self.difficulty = metadata.get('difficulty', 'beginner')
                self.estimated_duration = metadata.get('estimated_duration', '8 hours')
                self.tasks = metadata.get('tasks', [])
                
    def create_module_widget(self):
        """Create the main widget for this module"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Module header
        header_label = QLabel(f"<h1>{self.name}</h1>")
        header_label.setTextFormat(Qt.RichText)
        layout.addWidget(header_label)
        
        # Module description
        desc_label = QLabel(self.description)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Task list
        layout.addWidget(QLabel("<h2>Tasks:</h2>"))
        for task in self.tasks:
            task_btn = QPushButton(f"{task['name']} ({task['points']} points)")
            task_btn.clicked.connect(lambda checked, t=task: self.start_task(t))
            layout.addWidget(task_btn)
        
        # Instructions area
        self.instructions_text = QTextEdit()
        self.instructions_text.setReadOnly(True)
        self.instructions_text.setPlainText("Select a task to begin...")
        layout.addWidget(self.instructions_text)
        
        layout.addStretch()
        return widget
        
    def start_task(self, task):
        """Start a specific task"""
        self.current_task = task
        instructions = self.get_task_instructions(task['id'])
        self.instructions_text.setPlainText(instructions)
        
    def get_task_instructions(self, task_id):
        """Get instructions for a specific task"""
        instructions = {
            "setup_environment": """Task 1: Setup Programming Environment

1. Install the PLC programming software
2. Configure communication settings
3. Create a new project
4. Set up the hardware configuration
5. Test the connection to the PLC

Take a screenshot when complete.""",
            
            "first_program": """Task 2: Create First Ladder Logic Program

1. Create a new program routine
2. Add a start button (input)
3. Add a stop button (input)
4. Add a motor output
5. Create a holding circuit
6. Test in simulation mode

Take a screenshot of your ladder logic.""",
            
            "timers_counters": """Task 3: Implement Timers and Counters

1. Add a timer to your program
2. Configure timer presets
3. Add a counter for cycle tracking
4. Create reset logic
5. Test the functionality

Take a screenshot showing timer/counter operation."""
        }
        return instructions.get(task_id, "Instructions not found.")
        
    def verify_task_completion(self, task_id, screenshot_path):
        """Verify that a task has been completed"""
        # In a real implementation, this would analyze the screenshot
        # or check actual PLC code
        return True
        
    def get_progress(self):
        """Get current module progress"""
        completed_tasks = 0
        total_points = 0
        earned_points = 0
        
        for task in self.tasks:
            total_points += task['points']
            if self.is_task_completed(task['id']):
                completed_tasks += 1
                earned_points += task['points']
                
        return {
            'completed_tasks': completed_tasks,
            'total_tasks': len(self.tasks),
            'earned_points': earned_points,
            'total_points': total_points,
            'completion_percentage': (earned_points / total_points * 100) if total_points > 0 else 0
        }
        
    def is_task_completed(self, task_id):
        """Check if a task is completed"""
        # This would check the database for task completion status
        return False
