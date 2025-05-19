#!/usr/bin/env python3
"""
Dynamic Module Loader
Handles loading training modules from the modules directory
"""

import json
import importlib.util
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import requests
import zipfile
import tempfile
import shutil

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
                
            # Extract only the fields that ModuleMetadata expects
            metadata_fields = {
                'id': data.get('id', module_name),
                'name': data.get('name', module_name),
                'version': data.get('version', '1.0.0'),
                'description': data.get('description', ''),
                'category': data.get('category', 'General'),
                'difficulty': data.get('difficulty', 'Beginner'),
                'estimated_time': str(data.get('estimated_time', '60')),
                'dependencies': data.get('dependencies', []),
                'prerequisites': data.get('prerequisites', []),
                'learning_objectives': data.get('learning_objectives', []),
                'tags': data.get('tags', []),
                'created_date': data.get('created_date', ''),
                'updated_date': data.get('updated_date', ''),
                'author': data.get('author', '')
            }
            
            # Convert to ModuleMetadata object
            metadata = ModuleMetadata(**metadata_fields)
            self.module_metadata[module_name] = metadata
            
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to load metadata for {module_name}: {e}")
            return None
    
    def load_module(self, module_name: str, github_token: Optional[str] = None) -> Optional[Any]:
        """Dynamically load a module"""
        if module_name in self.loaded_modules:
            return self.loaded_modules[module_name]
            
        module_path = self.modules_dir / module_name / 'module.py'
        
        # Check if module exists locally
        if not module_path.exists():
            if github_token:
                logger.info(f"Module {module_name} not found locally, attempting GitHub download")
                if self.download_module_from_github(module_name, github_token):
                    # Try loading again after download
                    if module_path.exists():
                        return self.load_module(module_name, github_token)
                else:
                    logger.error(f"Failed to download module {module_name} from GitHub")
                    return None
            else:
                logger.error(f"Module {module_name} not found and no GitHub token provided")
                return None
        
        try:
            # Load the module dynamically
            spec = importlib.util.spec_from_file_location(
                f"modules.{module_name}", 
                module_path
            )
            
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Get the module class (assume it follows naming convention)
                class_name = self._get_module_class_name(module_name)
                if hasattr(module, class_name):
                    module_class = getattr(module, class_name)
                    self.loaded_modules[module_name] = module_class
                    logger.info(f"Successfully loaded module {module_name}")
                    return module_class
                else:
                    # Try to find any class that inherits from TrainingModule
                    from training_module import TrainingModule
                    for name, obj in module.__dict__.items():
                        if (isinstance(obj, type) and 
                            issubclass(obj, TrainingModule) and 
                            obj is not TrainingModule):
                            self.loaded_modules[module_name] = obj
                            logger.info(f"Successfully loaded module {module_name} as {name}")
                            return obj
                    
                    logger.error(f"Module {module_name} does not have expected class {class_name}")
                    return None
            else:
                logger.error(f"Failed to create module spec for {module_name}")
                return None
                
        except FileNotFoundError:
            logger.error(f"Module file not found: {module_path}")
            return None
        except ImportError as e:
            logger.error(f"Import error loading module {module_name}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error loading module {module_name}: {e}", exc_info=True)
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
    
    def download_module_from_github(self, module_name: str, github_token: str, 
                                  repo_url: str = "https://github.com/VoidReturn0/AutomationAcademy") -> bool:
        """Download a module from GitHub repository"""
        try:
            headers = {'Authorization': f'token {github_token}'} if github_token else {}
            
            # Construct URL to module directory
            module_url = f"{repo_url}/archive/refs/heads/master.zip"
            
            # Download repository archive
            response = requests.get(module_url, headers=headers, stream=True)
            response.raise_for_status()
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        tmp_file.write(chunk)
                tmp_path = tmp_file.name
            
            # Extract module from archive
            with zipfile.ZipFile(tmp_path, 'r') as zip_ref:
                # Find module in archive
                module_prefix = f"AutomationAcademy-master/modules/{module_name}/"
                module_files = [f for f in zip_ref.namelist() if f.startswith(module_prefix)]
                
                if not module_files:
                    logger.error(f"Module {module_name} not found in repository")
                    return False
                
                # Extract module files
                module_dir = self.modules_dir / module_name
                module_dir.mkdir(parents=True, exist_ok=True)
                
                for file_path in module_files:
                    # Get relative path within module
                    relative_path = file_path[len(module_prefix):]
                    if relative_path:  # Skip the directory itself
                        target_path = module_dir / relative_path
                        target_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        # Extract file
                        with zip_ref.open(file_path) as source, open(target_path, 'wb') as target:
                            shutil.copyfileobj(source, target)
                
                logger.info(f"Successfully downloaded module {module_name}")
                return True
                
        except requests.RequestException as e:
            logger.error(f"Failed to download module {module_name}: {e}")
            return False
        except Exception as e:
            logger.error(f"Error processing module {module_name}: {e}")
            return False
        finally:
            # Clean up temp file
            if 'tmp_path' in locals():
                try:
                    os.unlink(tmp_path)
                except:
                    pass

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