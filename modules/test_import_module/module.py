#!/usr/bin/env python3
"""
Test Import Module
A test module to verify the dynamic import functionality
"""

from training_module import TrainingModule
import logging
from pathlib import Path
import json

logger = logging.getLogger(__name__)

class TestImportModule(TrainingModule):
    """Test module for verifying import functionality"""
    
    def __init__(self, module_data=None, user_data=None):
        # Provide default module_data if not provided
        if module_data is None:
            module_data = {
                'id': 1,
                'name': 'Test Import Module',
                'description': 'This module tests the dynamic import system'
            }
        if user_data is None:
            user_data = {'id': 1, 'username': 'test_user'}
            
        super().__init__(module_data, user_data)
        self.module_name = "Test Import Module"
        self.module_id = "test_import_module"
        logger.info(f"Initializing {self.module_name}")
    
    @property
    def estimated_time(self):
        """Return estimated completion time in minutes"""
        return 30
    
    @property
    def difficulty(self):
        """Return module difficulty"""
        return "Beginner"
    
    @property
    def category(self):
        """Return module category"""
        return "System Test"
    
    @property
    def description(self):
        """Return module description"""
        return "This module tests the dynamic import system and verifies that modules can be loaded correctly."
    
    def get_learning_objectives(self):
        """Return learning objectives"""
        return [
            "Verify module import functionality",
            "Test dynamic class loading",
            "Confirm metadata parsing",
            "Validate task completion tracking"
        ]
    
    def get_prerequisites(self):
        """Return prerequisites"""
        return ["Basic understanding of the training system"]
    
    def get_required_resources(self):
        """Return required resources"""
        return [
            "Access to the training system",
            "Test environment setup"
        ]
    
    def get_tasks(self):
        """Return module tasks"""
        return [
            {
                'id': 1,
                'name': 'Module Loading Test',
                'description': 'Verify that this module loads correctly',
                'type': 'verification',
                'instructions': [
                    'Open the training system',
                    'Navigate to the modules list',
                    'Verify that "Test Import Module" appears in the list',
                    'Click on the module to select it'
                ],
                'verification': 'screenshot',
                'points': 20,
                'required': True,
                'screenshot_required': True
            },
            {
                'id': 2,
                'name': 'Module Metadata Test',
                'description': 'Verify that module metadata is loaded correctly',
                'type': 'verification',
                'instructions': [
                    'Check the module description in the UI',
                    'Verify the estimated time shows 30 minutes',
                    'Confirm the difficulty level is "Beginner"',
                    'Check that the category is "System Test"'
                ],
                'verification': 'screenshot',
                'points': 20,
                'required': True,
                'screenshot_required': True
            },
            {
                'id': 3,
                'name': 'Task System Test',
                'description': 'Verify that tasks are displayed correctly',
                'type': 'practical',
                'instructions': [
                    'Start the module',
                    'Verify that all tasks are displayed',
                    'Complete this task by taking a screenshot',
                    'Click "Complete Task" button'
                ],
                'verification': 'screenshot',
                'points': 20,
                'required': True,
                'screenshot_required': True
            },
            {
                'id': 4,
                'name': 'Resource Loading Test',
                'description': 'Test that module resources can be accessed',
                'type': 'verification',
                'instructions': [
                    'Check if module resources are listed',
                    'Open the test document if available',
                    'Verify resource paths are correct'
                ],
                'verification': 'manual',
                'points': 20,
                'required': False,
                'screenshot_required': False
            },
            {
                'id': 5,
                'name': 'Module Completion Test',
                'description': 'Complete the module and verify tracking',
                'type': 'practical',
                'instructions': [
                    'Complete all required tasks',
                    'Submit the module for completion',
                    'Verify that completion is tracked in the system',
                    'Check that the progress shows 100%'
                ],
                'verification': 'screenshot',
                'points': 20,
                'required': True,
                'screenshot_required': True
            }
        ]
    
    def setup(self):
        """Setup the test environment"""
        logger.info(f"Setting up {self.module_name}")
        # Create a test file in resources
        resource_path = Path(__file__).parent / 'resources' / 'test_file.txt'
        resource_path.parent.mkdir(exist_ok=True)
        with open(resource_path, 'w') as f:
            f.write("This is a test resource file for the module import test.")
        logger.info("Test resource file created")
    
    def validate_task(self, task_id: int, user_input: dict) -> bool:
        """Validate task completion"""
        logger.info(f"Validating task {task_id} with input: {user_input}")
        
        # For this test module, we'll accept any screenshot as valid
        if task_id in [1, 2, 3, 5]:
            return bool(user_input.get('screenshot_path'))
        elif task_id == 4:
            # This is a manual verification task
            return True
        
        return False
    
    def cleanup(self):
        """Cleanup test resources"""
        logger.info(f"Cleaning up {self.module_name}")
        # Clean up any test files created
        resource_path = Path(__file__).parent / 'resources' / 'test_file.txt'
        if resource_path.exists():
            resource_path.unlink()
            logger.info("Test resource file removed")

# Alternative class names to test the loader's ability to find classes
class TestImportModuleAlternative(TestImportModule):
    """Alternative class name for testing"""
    pass

class TestModule(TestImportModule):
    """Short class name for testing"""
    pass

# For testing direct import
if __name__ == "__main__":
    module = TestImportModule()
    print(f"Module loaded: {module.module_name}")
    print(f"Tasks: {len(module.get_tasks())}")
    print(f"Learning objectives: {module.get_learning_objectives()}")