#!/usr/bin/env python3
"""
Test Module Import Script
Tests the dynamic import functionality with the test module
"""

import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Initialize Qt application if needed
from PySide6.QtWidgets import QApplication
app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)

from module_loader import ModuleLoader
from training_module import TrainingModule

def test_direct_import():
    """Test direct import of the module"""
    logger.info("=== Testing Direct Import ===")
    try:
        from modules.test_import_module.module import TestImportModule
        module = TestImportModule()
        logger.info(f"✓ Direct import successful: {module.module_name}")
        logger.info(f"  - Module ID: {module.module_id}")
        logger.info(f"  - Category: {module.category}")
        logger.info(f"  - Tasks: {len(module.get_tasks())}")
        return True
    except Exception as e:
        logger.error(f"✗ Direct import failed: {e}")
        return False

def test_module_loader():
    """Test module loading through ModuleLoader"""
    logger.info("\n=== Testing Module Loader ===")
    loader = ModuleLoader(Path("modules"))
    
    # Test module discovery
    logger.info("Discovering modules...")
    modules = loader.discover_modules()
    logger.info(f"Found {len(modules)} modules: {modules}")
    
    if "test_import_module" not in modules:
        logger.error("✗ Test module not discovered")
        return False
    
    # Test metadata loading
    logger.info("\nLoading module metadata...")
    metadata = loader.load_module_metadata("test_import_module")
    if metadata:
        logger.info(f"✓ Metadata loaded successfully:")
        logger.info(f"  - Name: {metadata.name}")
        logger.info(f"  - Version: {metadata.version}")
        logger.info(f"  - Description: {metadata.description}")
        logger.info(f"  - Category: {metadata.category}")
        logger.info(f"  - Difficulty: {metadata.difficulty}")
    else:
        logger.error("✗ Failed to load metadata")
        return False
    
    # Test module loading
    logger.info("\nLoading module class...")
    module_class = loader.load_module("test_import_module")
    if module_class:
        logger.info(f"✓ Module class loaded: {module_class.__name__}")
        
        # Instantiate the module
        try:
            module_instance = module_class()
            logger.info(f"✓ Module instantiated: {module_instance.module_name}")
            
            # Test module methods
            logger.info("\nTesting module methods:")
            logger.info(f"  - Learning objectives: {len(module_instance.get_learning_objectives())}")
            logger.info(f"  - Tasks: {len(module_instance.get_tasks())}")
            logger.info(f"  - Prerequisites: {module_instance.get_prerequisites()}")
            
            # Test task validation
            test_task_id = 1
            test_input = {'screenshot_path': '/fake/path/screenshot.png'}
            is_valid = module_instance.validate_task(test_task_id, test_input)
            logger.info(f"  - Task validation test: {'✓ Passed' if is_valid else '✗ Failed'}")
            
            return True
        except Exception as e:
            logger.error(f"✗ Failed to instantiate module: {e}")
            return False
    else:
        logger.error("✗ Failed to load module class")
        return False

def test_alternative_class_names():
    """Test that the loader can find alternative class names"""
    logger.info("\n=== Testing Alternative Class Names ===")
    loader = ModuleLoader(Path("modules"))
    
    # Temporarily rename the expected class to test fallback
    original_method = loader._get_module_class_name
    loader._get_module_class_name = lambda x: "NonExistentClass"
    
    module_class = loader.load_module("test_import_module")
    loader._get_module_class_name = original_method  # Restore original method
    
    if module_class:
        logger.info(f"✓ Found alternative class: {module_class.__name__}")
        return True
    else:
        logger.error("✗ Failed to find alternative class")
        return False

def test_module_in_database():
    """Test adding the module to the database"""
    logger.info("\n=== Testing Database Integration ===")
    try:
        from main import DatabaseManager
        db = DatabaseManager("test_training_data.db")
        
        # Add test module to database
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO modules (name, description, prerequisites, estimated_duration)
            VALUES (?, ?, ?, ?)
        ''', ("Test Import Module", "Test module for import functionality", "", 30))
        
        conn.commit()
        conn.close()
        
        logger.info("✓ Module added to database")
        return True
    except Exception as e:
        logger.error(f"✗ Database integration failed: {e}")
        return False

def main():
    """Run all tests"""
    logger.info("Starting Module Import Tests")
    logger.info("=" * 50)
    
    tests = [
        ("Direct Import", test_direct_import),
        ("Module Loader", test_module_loader),
        ("Alternative Class Names", test_alternative_class_names),
        ("Database Integration", test_module_in_database)
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            logger.error(f"Test '{test_name}' crashed: {e}")
            results[test_name] = False
    
    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("TEST SUMMARY")
    logger.info("=" * 50)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASSED" if result else "✗ FAILED"
        logger.info(f"{test_name:.<40} {status}")
    
    logger.info(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("\n🎉 All tests passed! The module import system is working correctly.")
    else:
        logger.error("\n❌ Some tests failed. Please check the logs for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)