#!/usr/bin/env python3
"""
Dynamic Module Loader
Handles loading training modules from the modules directory
"""

import json
import importlib.util
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class ModuleMetadata:
    """Module metadata structure"""
    id: str
    name: str
    version: str
    description: str
    category: str
    difficulty: str
    estimated_time: str
    dependencies: List[str]
    prerequisites: List[str]
    learning_objectives: List[str]
    tags: List[str]
    created_date: str
    updated_date: str
    author: str

class ModuleLoader:
    """Dynamic module loader for training modules"""
    
    def __init__(self, modules_dir: Path):
        self.modules_dir = Path(modules_dir)
        self.loaded_modules: Dict[str, Any] = {}
        self.module_metadata: Dict[str, ModuleMetadata] = {}
        
    def discover_modules(self) -> List[str]:
        """Discover all available modules"""
        modules = []
        
        for module_path in self.modules_dir.iterdir():
            if module_path.is_dir() and not module_path.name.startswith('_'):
                metadata_file = module_path / 'metadata.json'
                module_file = module_path / 'module.py'
                
                if metadata_file.exists() and module_file.exists():
                    modules.append(module_path.name)
                    
        return modules
    
    def load_module_metadata(self, module_name: str) -> Optional[ModuleMetadata]:
        """Load module metadata from JSON file"""
        metadata_path = self.modules_dir / module_name / 'metadata.json'
        
        try:
            with open(metadata_path, 'r') as f:
                data = json.load(f)
                
            # Convert to ModuleMetadata object
            metadata = ModuleMetadata(**data)
            self.module_metadata[module_name] = metadata
            
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to load metadata for {module_name}: {e}")
            return None
    
    def load_module(self, module_name: str) -> Optional[Any]:
        """Dynamically load a module"""
        if module_name in self.loaded_modules:
            return self.loaded_modules[module_name]
            
        module_path = self.modules_dir / module_name / 'module.py'
        
        try:
            # Load the module dynamically
            spec = importlib.util.spec_from_file_location(
                f"modules.{module_name}", 
                module_path
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Get the module class (assume it follows naming convention)
            class_name = self._get_module_class_name(module_name)
            if hasattr(module, class_name):
                module_class = getattr(module, class_name)
                self.loaded_modules[module_name] = module_class
                return module_class
            else:
                logger.error(f"Module {module_name} does not have class {class_name}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to load module {module_name}: {e}")
            return None
    
    def _get_module_class_name(self, module_name: str) -> str:
        """Convert module name to class name"""
        # Convert snake_case to PascalCase
        parts = module_name.split('_')
        return ''.join(part.capitalize() for part in parts) + 'Module'
    
    def check_dependencies(self, module_name: str) -> bool:
        """Check if module dependencies are satisfied"""
        metadata = self.module_metadata.get(module_name)
        
        if not metadata:
            return False
            
        for dep in metadata.dependencies:
            if dep not in self.loaded_modules:
                if not self.load_module(dep):
                    logger.error(f"Failed to load dependency {dep} for {module_name}")
                    return False
                    
        return True
    
    def get_modules_by_category(self, category: str) -> List[str]:
        """Get all modules in a specific category"""
        modules = []
        
        for name, metadata in self.module_metadata.items():
            if metadata.category == category:
                modules.append(name)
                
        return modules
    
    def get_modules_by_difficulty(self, difficulty: str) -> List[str]:
        """Get all modules of a specific difficulty"""
        modules = []
        
        for name, metadata in self.module_metadata.items():
            if metadata.difficulty == difficulty:
                modules.append(name)
                
        return modules
    
    def export_module_catalog(self, output_path: Path):
        """Export module catalog to JSON"""
        catalog = {}
        
        for name, metadata in self.module_metadata.items():
            catalog[name] = asdict(metadata)
            
        with open(output_path, 'w') as f:
            json.dump(catalog, f, indent=2)

# Example usage
if __name__ == "__main__":
    loader = ModuleLoader(Path("modules"))
    
    # Discover all modules
    modules = loader.discover_modules()
    print(f"Found {len(modules)} modules")
    
    # Load metadata for each module
    for module in modules:
        metadata = loader.load_module_metadata(module)
        if metadata:
            print(f"Loaded metadata for {metadata.name} v{metadata.version}")
    
    # Load a specific module
    module_class = loader.load_module("network_file_sharing")
    if module_class:
        print(f"Successfully loaded module class: {module_class.__name__}")