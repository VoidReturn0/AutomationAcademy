#!/usr/bin/env python3
"""
Setup Deploy Key Script
Helps configure the deploy key for the application
"""

import os
import sys
from config_manager import get_config_manager, ConfigManager

def main():
    print("Broetje Training System - Deploy Key Setup")
    print("=" * 40)
    
    config_manager = get_config_manager()
    
    print("\nCurrent Configuration:")
    print(f"Use Deploy Key: {config_manager.get('github.use_deploy_key', False)}")
    print(f"Repository URL: {config_manager.get('github.repository_url')}")
    
    # Check environment variable
    env_key = os.environ.get('BROETJE_DEPLOY_KEY')
    if env_key:
        print(f"Deploy key found in environment: {env_key[:10]}...")
    else:
        print("No deploy key in environment")
    
    print("\nOptions:")
    print("1. Enable deploy key usage")
    print("2. Disable deploy key usage")
    print("3. Set deploy key in environment")
    print("4. Test GitHub access")
    print("5. Exit")
    
    while True:
        choice = input("\nSelect option: ").strip()
        
        if choice == '1':
            config_manager.set('github.use_deploy_key', True)
            print("Deploy key usage enabled")
            
        elif choice == '2':
            config_manager.set('github.use_deploy_key', False)
            print("Deploy key usage disabled")
            
        elif choice == '3':
            key = input("Enter deploy key (or press Enter to cancel): ").strip()
            if key:
                os.environ['BROETJE_DEPLOY_KEY'] = key
                print("Deploy key set in environment for this session")
                print("To make permanent, add to system environment variables")
            
        elif choice == '4':
            print("\nTesting GitHub access...")
            try:
                from github_integration import GitHubAPIClient
                repo_url = config_manager.get('github.repository_url')
                client = GitHubAPIClient(repo_url)
                
                if client.api_token:
                    print(f"Token available: {client.api_token[:10]}...")
                    info = client.get_repository_info()
                    print(f"Repository: {info.get('full_name', 'Unknown')}")
                    print(f"Description: {info.get('description', 'None')}")
                    print("✓ GitHub access successful")
                else:
                    print("✗ No token available")
                    
            except Exception as e:
                print(f"✗ Error: {e}")
                
        elif choice == '5':
            break
        else:
            print("Invalid option")
    
    print("\nSetup complete")

if __name__ == "__main__":
    main()