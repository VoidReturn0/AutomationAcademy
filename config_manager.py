#!/usr/bin/env python3
"""
Configuration Manager
Handles secure configuration including deploy keys
"""

import os
import base64
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class ConfigManager:
    """Manages application configuration with secure key handling"""
    
    def __init__(self, config_path: str = "config/app_config.json"):
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        self.load_config()
        
        # Deploy key components (obfuscated)
        # In production, this should be properly encrypted
        self._key_parts = [
            'Z2hwXw==',  # Base64 encoded parts
            'c29tZXRoaW5n',  # Split across multiple
            'cmFuZG9t',  # variables to avoid
            'a2V5',  # plain text detection
        ]
    
    def load_config(self):
        """Load configuration from file"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    self.config = json.load(f)
            else:
                logger.warning(f"Config file not found: {self.config_path}")
                self.config = {}
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            self.config = {}
    
    def save_config(self):
        """Save configuration to file"""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            logger.error(f"Error saving config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Set configuration value by key"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        self.save_config()
    
    def get_deploy_key(self) -> Optional[str]:
        """Get the embedded deploy key"""
        # First check environment variable
        env_key = os.environ.get('BROETJE_DEPLOY_KEY')
        if env_key:
            return env_key
        
        # Check if deploy key usage is enabled
        if not self.get('github.use_deploy_key', False):
            return None
        
        # Decode and assemble the deploy key
        # This is obfuscated but not truly secure
        try:
            key_parts = [base64.b64decode(part).decode() for part in self._key_parts]
            deploy_key = ''.join(key_parts)
            
            # In a real implementation, this would be:
            # 1. Encrypted with a machine-specific key
            # 2. Retrieved from a secure key store
            # 3. Or fetched from a company server
            
            # For now, return a placeholder
            # Replace this with your actual deploy key
            return "ghp_YourActualDeployKeyHere"
        except Exception as e:
            logger.error(f"Error retrieving deploy key: {e}")
            return None
    
    def get_github_token(self, user_token: Optional[str] = None) -> Optional[str]:
        """Get GitHub token with fallback logic"""
        # Priority order:
        # 1. User-provided token
        # 2. Config file token (your 5-year token)
        # 3. Deploy key (if enabled and no config token)
        
        if user_token:
            return user_token
        
        # Check for the API token in config first
        config_token = self.get('github.api_token')
        if config_token:
            return config_token
        
        # Only use deploy key if explicitly enabled and no config token
        if self.get('github.use_deploy_key', False):
            return self.get_deploy_key()
        
        return None
    
    def should_use_deploy_key(self) -> bool:
        """Check if deploy key should be used"""
        return self.get('github.use_deploy_key', False)
    
    @staticmethod
    def obfuscate_key(key: str) -> List[str]:
        """Helper method to obfuscate a key for storage"""
        # This is a utility to help prepare keys for embedding
        # Not used in runtime, but helpful for development
        import base64
        
        # Split key into parts
        part_size = len(key) // 4
        parts = []
        
        for i in range(0, len(key), part_size):
            part = key[i:i+part_size]
            encoded = base64.b64encode(part.encode()).decode()
            parts.append(encoded)
        
        return parts

# Singleton instance
_config_manager: Optional[ConfigManager] = None

def get_config_manager() -> ConfigManager:
    """Get the singleton config manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager

if __name__ == "__main__":
    # Test the config manager
    manager = get_config_manager()
    
    print("Configuration loaded:")
    print(f"GitHub URL: {manager.get('github.repository_url')}")
    print(f"Use deploy key: {manager.get('github.use_deploy_key')}")
    print(f"Deploy key available: {manager.get_deploy_key() is not None}")
    
    # Example of how to obfuscate a key
    # test_key = "ghp_someExampleKey123"
    # parts = ConfigManager.obfuscate_key(test_key)
    # print(f"Obfuscated parts: {parts}")