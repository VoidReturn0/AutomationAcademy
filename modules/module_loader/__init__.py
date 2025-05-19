"""Module loader package for dynamically loading training modules."""

import os
import json
import importlib.util
import sys
from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class ModuleInfo:
    """Container for module metadata."""
    def __init__(self, metadata: dict, path: str):
        self.id = metadata.get('id')
        self.name = metadata.get('name')
        self.version = metadata.get('version')
        self.author = metadata.get('author')
        self.description = metadata.get('description')
        self.prerequisites = metadata.get('prerequisites', [])
        self.dependencies = metadata.get('dependencies', [])
        self.difficulty = metadata.get('difficulty')
        self.estimated_duration = metadata.get('estimated_duration')
        self.tasks = metadata.get('tasks', [])
        self.resources = metadata.get('resources', {})
        self.certification = metadata.get('certification', {})
        self.path = path
        self.module_class = None
        
    def meets_prerequisites(self, completed_modules: List[str]) -> bool:
        """Check if all prerequisites are met."""
        return all(prereq in completed_modules for prereq in self.prerequisites)
        
    def get_total_points(self) -> int:
        """Calculate total points for all tasks."""
        return sum(task.get('points', 0) for task in self.tasks)

class ModuleLoader:
    """Dynamic module loader for training modules."""
    
    def __init__(self, modules_directory: str):
        self.modules_directory = Path(modules_directory)
        self.loaded_modules: Dict[str, ModuleInfo] = {}
        self.module_instances: Dict[str, object] = {}
        
    def scan_modules(self) -> Dict[str, ModuleInfo]:
        """Scan the modules directory and load all available modules."""
        self.loaded_modules.clear()
        
        if not self.modules_directory.exists():
            logger.error(f"Modules directory not found: {self.modules_directory}")
            return self.loaded_modules
            
        for module_dir in self.modules_directory.iterdir():
            if module_dir.is_dir() and module_dir.name != 'module_loader':
                metadata_path = module_dir / 'metadata.json'
                module_py_path = module_dir / 'module.py'
                
                if metadata_path.exists() and module_py_path.exists():
                    try:
                        # Load metadata
                        with open(metadata_path, 'r') as f:
                            metadata = json.load(f)
                            
                        module_info = ModuleInfo(metadata, str(module_dir))
                        
                        # Load the module class
                        module_info.module_class = self._load_module_class(
                            module_py_path, 
                            module_info.id
                        )
                        
                        self.loaded_modules[module_info.id] = module_info
                        logger.info(f"Loaded module: {module_info.name} v{module_info.version}")
                        
                    except Exception as e:
                        logger.error(f"Failed to load module from {module_dir}: {e}")
                        
        return self.loaded_modules
        
    def _load_module_class(self, module_path: Path, module_id: str):
        """Dynamically load a module class from a Python file."""
        try:
            spec = importlib.util.spec_from_file_location(
                f"modules.{module_id}", 
                module_path
            )
            
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                sys.modules[spec.name] = module
                spec.loader.exec_module(module)
                
                # Find the module class (should be named after the module)
                for name, cls in module.__dict__.items():
                    if (isinstance(cls, type) and 
                        name.lower().replace('_', '') == module_id.lower().replace('_', '') + 'module'):
                        return cls
                        
                # If no specific class found, look for any TrainingModule subclass
                for name, cls in module.__dict__.items():
                    if (isinstance(cls, type) and 
                        hasattr(cls, '__bases__') and 
                        'TrainingModule' in [base.__name__ for base in cls.__bases__']):
                        return cls
                        
        except Exception as e:
            logger.error(f"Failed to load module class from {module_path}: {e}")
            
        return None
        
    def get_module_instance(self, module_id: str) -> Optional[object]:
        """Get or create an instance of a module."""
        if module_id not in self.loaded_modules:
            logger.error(f"Module not found: {module_id}")
            return None
            
        if module_id not in self.module_instances:
            module_info = self.loaded_modules[module_id]
            if module_info.module_class:
                try:
                    self.module_instances[module_id] = module_info.module_class()
                    logger.info(f"Created instance of module: {module_id}")
                except Exception as e:
                    logger.error(f"Failed to instantiate module {module_id}: {e}")
                    return None
            else:
                logger.error(f"No module class found for: {module_id}")
                return None
                
        return self.module_instances[module_id]
        
    def get_module_info(self, module_id: str) -> Optional[ModuleInfo]:
        """Get metadata for a specific module."""
        return self.loaded_modules.get(module_id)
        
    def get_available_modules(self, completed_modules: List[str] = None) -> List[ModuleInfo]:
        """Get list of modules that can be started based on prerequisites."""
        if completed_modules is None:
            completed_modules = []
            
        available = []
        for module_info in self.loaded_modules.values():
            if module_info.meets_prerequisites(completed_modules):
                available.append(module_info)
                
        return available
        
    def check_dependencies(self, module_id: str) -> bool:
        """Check if all dependencies for a module are satisfied."""
        module_info = self.loaded_modules.get(module_id)
        if not module_info:
            return False
            
        # In a real implementation, this would check if required
        # libraries, tools, or other modules are available
        return True
        
    def get_module_resources(self, module_id: str) -> Dict[str, str]:
        """Get resource paths for a module."""
        module_info = self.loaded_modules.get(module_id)
        if not module_info:
            return {}
            
        resources = {}
        module_path = Path(module_info.path)
        
        for resource_type, resource_path in module_info.resources.items():
            full_path = module_path / resource_path
            if full_path.exists():
                resources[resource_type] = str(full_path)
                
        return resources

# Singleton instance
_module_loader_instance = None

def get_module_loader(modules_directory: str = None) -> ModuleLoader:
    """Get the singleton module loader instance."""
    global _module_loader_instance
    
    if _module_loader_instance is None:
        if modules_directory is None:
            modules_directory = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), 
                '..'
            )
        _module_loader_instance = ModuleLoader(modules_directory)
        
    return _module_loader_instance
