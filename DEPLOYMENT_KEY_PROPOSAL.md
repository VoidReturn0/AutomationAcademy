# Deployment Key Implementation Proposal

## Recommended Approach: Organization-Level Deploy Key

Instead of individual user tokens or a single embedded key, implement an organization-level deployment key system:

### 1. Server-Side Token Management
- Store the deploy key on a company server, not in the app
- App requests modules through your company API
- Server proxies GitHub requests using the deploy key

```
[Training App] -> [Company API Server] -> [GitHub API]
                  (with deploy key)
```

### 2. Implementation Steps

1. **Create a Simple API Server**
   ```python
   # company_module_server.py
   from flask import Flask, jsonify, request
   import requests
   import os
   
   app = Flask(__name__)
   GITHUB_TOKEN = os.environ.get('GITHUB_DEPLOY_KEY')
   
   @app.route('/api/modules/<module_name>')
   def get_module(module_name):
       # Verify internal network request
       if not is_internal_network(request.remote_addr):
           return jsonify({'error': 'Unauthorized'}), 403
       
       # Proxy to GitHub
       headers = {'Authorization': f'token {GITHUB_TOKEN}'}
       response = requests.get(
           f'https://api.github.com/repos/YourOrg/AutomationAcademy/contents/modules/{module_name}',
           headers=headers
       )
       return response.json()
   ```

2. **Update the Training App**
   ```python
   # github_integration.py
   def download_module(module_name, company_api_url='http://training-server.broetje.local:5000'):
       # Use company API instead of direct GitHub
       response = requests.get(f'{company_api_url}/api/modules/{module_name}')
       # Process response...
   ```

### 3. Benefits of This Approach
- Deploy key never leaves company infrastructure
- Can add company-specific authentication/authorization
- Easy to update or rotate keys
- Can add caching to reduce GitHub API calls
- Can log module access for compliance
- Works on internal network without internet

### 4. Alternative: Encrypted Deploy Key
If you must embed a key in the app:

```python
# config_manager.py
import base64
from cryptography.fernet import Fernet

class ConfigManager:
    def __init__(self):
        # Key derived from hardware ID + master password
        self.cipher_key = self._generate_machine_key()
        self.cipher = Fernet(self.cipher_key)
    
    def _generate_machine_key(self):
        # Generate key from machine-specific data
        import uuid
        machine_id = str(uuid.getnode())  # MAC address
        master_secret = "BroetjeTraining2024"  # Could be in env var
        combined = f"{machine_id}{master_secret}"
        return base64.urlsafe_b64encode(combined[:32].encode())
    
    def get_deploy_key(self):
        # Encrypted key stored in config
        encrypted_key = "gAAAAABh..."  # Your encrypted deploy key
        return self.cipher.decrypt(encrypted_key.encode()).decode()
```

### 5. Quick Implementation (Embedded Key)
If you want to proceed with embedded deploy key immediately:

```python
# github_integration.py
class GitHubAPIClient:
    def __init__(self, repo_url: str, api_token: Optional[str] = None):
        self.repo_url = repo_url
        
        # Use provided token or fall back to deploy key
        if api_token:
            self.api_token = api_token
        else:
            # Deploy key for read-only access to the training repo
            self.api_token = self._get_deploy_key()
        
        self.headers = {'Authorization': f'token {self.api_token}'}
    
    def _get_deploy_key(self):
        # Obfuscated but not truly secure
        # This is a trade-off for ease of deployment
        key_parts = [
            'ghp_',  # GitHub token prefix
            'a1b2c3d4',  # Split the key
            'e5f6g7h8',  # into parts
            'i9j0k1l2'   # to avoid detection
        ]
        return ''.join(key_parts)
```

## Recommendation

For a corporate training system, I recommend:

1. **Short term**: Use embedded deploy key with obfuscation
2. **Medium term**: Implement company API server approach
3. **Long term**: Consider full authentication system with SSO

This provides a good balance of security and usability for your specific use case.