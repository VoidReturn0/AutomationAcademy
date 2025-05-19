#!/usr/bin/env python3
"""
Setup GitHub Token Script
Helps configure the GitHub personal access token
"""

import os
import sys
from config_manager import get_config_manager

def main():
    print("Broetje Training System - GitHub Token Setup")
    print("=" * 40)
    
    config_manager = get_config_manager()
    
    print("\nCurrent Configuration:")
    print(f"Repository URL: {config_manager.get('github.repository_url')}")
    current_token = config_manager.get('github.api_token')
    
    if current_token:
        print(f"Current Token: {current_token[:10]}..." if current_token.startswith('ghp_') else "Invalid token format")
    else:
        print("No GitHub token configured")
    
    print("\n⚠️  GitHub requires personal access tokens that start with 'ghp_'")
    print("To generate a token:")
    print("1. Go to https://github.com/settings/tokens")
    print("2. Click 'Generate new token (classic)'")
    print("3. Set expiration (recommend 5 years)")
    print("4. Select 'repo' scope for full repository access")
    print("5. Generate and copy the token")
    
    print("\nOptions:")
    print("1. Set GitHub API token")
    print("2. Set token via environment variable")
    print("3. Test current configuration")
    print("4. Clear token")
    print("5. Exit")
    
    while True:
        choice = input("\nSelect option: ").strip()
        
        if choice == '1':
            token = input("Enter GitHub token (ghp_...): ").strip()
            if token and token.startswith('ghp_'):
                config_manager.set('github.api_token', token)
                config_manager.set('github.use_deploy_key', False)
                print("✓ GitHub token saved to configuration")
            else:
                print("✗ Invalid token format. Must start with 'ghp_'")
            
        elif choice == '2':
            print("\nTo use environment variable, add to your shell:")
            print("export GITHUB_API_TOKEN='ghp_yourtoken'")
            print("Or on Windows:")
            print("set GITHUB_API_TOKEN=ghp_yourtoken")
            
        elif choice == '3':
            print("\nTesting GitHub access...")
            try:
                from github_integration import GitHubAPIClient
                repo_url = config_manager.get('github.repository_url')
                client = GitHubAPIClient(repo_url)
                
                if client.api_token:
                    print(f"Using token: {client.api_token[:10]}...")
                    info = client.get_repository_info()
                    print(f"✓ Repository: {info.get('full_name', 'Unknown')}")
                    print("✓ GitHub access successful")
                else:
                    print("✗ No token available")
                    
            except Exception as e:
                print(f"✗ Error: {e}")
                
        elif choice == '4':
            config_manager.set('github.api_token', None)
            print("GitHub token cleared")
            
        elif choice == '5':
            break
        else:
            print("Invalid option")
    
    print("\nSetup complete")
    
    # Show JWT token info if available
    jwt_token = config_manager.get('authentication.jwt_token')
    if jwt_token:
        print("\nNote: Found JWT token in authentication section")
        print("This is stored separately and not used for GitHub API access")

if __name__ == "__main__":
    main()