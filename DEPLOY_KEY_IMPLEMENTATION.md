# Deploy Key Implementation

This document describes the embedded deploy key implementation for the Broetje Training System.

## Overview

The system now supports an embedded deploy key that allows all users to access GitHub modules without requiring individual tokens. This simplifies deployment and user experience while maintaining reasonable security for an internal corporate application.

## How It Works

1. **Deploy Key Storage**: The deploy key is stored in the `config_manager.py` file in an obfuscated format
2. **Fallback Logic**: The system checks for tokens in this order:
   - User-provided GitHub token
   - Embedded deploy key (if enabled)
   - Configuration file token

3. **Configuration**: Controlled via `config/app_config.json`:
   ```json
   {
     "github": {
       "use_deploy_key": true
     }
   }
   ```

## Setting Up

### Option 1: Environment Variable (Recommended for Testing)
```bash
export BROETJE_DEPLOY_KEY="ghp_yourActualDeployKey"
python main.py
```

### Option 2: Embedded Key (For Production)
1. Edit `config_manager.py`
2. Replace the placeholder key in `get_deploy_key()` method:
   ```python
   return "ghp_YourActualDeployKeyHere"
   ```

### Option 3: Use Setup Script
```bash
python setup_deploy_key.py
```

## Security Considerations

1. **Access Control**: The deploy key should have read-only access to the repository
2. **Obfuscation**: The key is split and encoded to avoid plain text detection
3. **Environment**: For sensitive deployments, use environment variables instead
4. **Rotation**: Regular key rotation is recommended

## Creating a Deploy Key

1. Go to: https://github.com/settings/tokens
2. Generate new token (classic)
3. Select scopes:
   - `repo` (for private repos)
   - `public_repo` (for public repos only)
4. Copy the token and use it as the deploy key

## Benefits

- **Simplified User Experience**: No need for users to obtain GitHub tokens
- **Centralized Access**: Single key for all users
- **Easy Deployment**: No per-user configuration needed
- **Consistent Access**: All users get the same module access

## Best Practices

1. Use a dedicated GitHub account for the deploy key
2. Limit the key's permissions to read-only access
3. Store the key securely (environment variable or encrypted)
4. Monitor key usage through GitHub's security log
5. Rotate the key periodically

## Fallback Behavior

If deploy key is not available or disabled:
- Users with GitHub tokens in their profile can access all modules
- Users without tokens see only default modules
- System continues to function with limited module access

## Troubleshooting

### Deploy Key Not Working
1. Check if `use_deploy_key` is set to `true` in config
2. Verify the key is correctly set in environment or code
3. Check GitHub token permissions
4. Look for errors in the application log

### Testing Access
```python
from github_integration import GitHubAPIClient
from config_manager import get_config_manager

config = get_config_manager()
client = GitHubAPIClient(config.get('github.repository_url'))
print(f"Token available: {client.api_token is not None}")
```

## Future Enhancements

1. Encrypted key storage
2. Key rotation automation
3. Per-module access control
4. Audit logging for key usage
5. Integration with corporate key management systems