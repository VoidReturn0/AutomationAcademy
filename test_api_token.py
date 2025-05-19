#!/usr/bin/env python3
"""
Test API Token Script
Verifies that the GitHub API token is working correctly
"""

import sys
from config_manager import get_config_manager
from github_integration import GitHubAPIClient

def test_api_token():
    print("Testing GitHub API Token Configuration")
    print("=" * 40)
    
    # Get configuration
    config_manager = get_config_manager()
    
    # Display current configuration
    repo_url = config_manager.get('github.repository_url')
    api_token = config_manager.get('github.api_token')
    use_deploy_key = config_manager.get('github.use_deploy_key', False)
    
    print(f"\nConfiguration:")
    print(f"Repository URL: {repo_url}")
    print(f"API Token: {api_token[:20]}..." if api_token else "API Token: None")
    print(f"Use Deploy Key: {use_deploy_key}")
    
    # Test GitHub API access
    print("\nTesting GitHub API Access...")
    try:
        client = GitHubAPIClient(repo_url)
        
        # Check which token is being used
        if client.api_token:
            print(f"Using token: {client.api_token[:20]}...")
        else:
            print("No token available!")
            return False
        
        # Test repository access
        print("\nTesting repository access...")
        repo_info = client.get_repository_info()
        
        print(f"✓ Repository: {repo_info.get('full_name', 'Unknown')}")
        print(f"✓ Description: {repo_info.get('description', 'None')}")
        print(f"✓ Private: {repo_info.get('private', False)}")
        print(f"✓ Default Branch: {repo_info.get('default_branch', 'Unknown')}")
        
        # Test module listing
        print("\nTesting module access...")
        modules = client.get_directory_contents("modules")
        print(f"✓ Found {len(modules)} modules in repository")
        
        if modules:
            print("\nAvailable modules:")
            for module in modules[:5]:  # Show first 5
                if module['type'] == 'dir':
                    print(f"  - {module['name']}")
        
        print("\n✅ API token is working correctly!")
        print("Token expires in 2030 (5-year token)")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_api_token()
    sys.exit(0 if success else 1)