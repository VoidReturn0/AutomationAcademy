# API Token Configuration Update

The token provided appears to be a JWT token, not a GitHub personal access token. GitHub requires personal access tokens that start with "ghp_" for API access.

## To Set Up Proper GitHub Access:

1. **Generate a GitHub Personal Access Token**:
   - Go to https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Set expiration to custom (5 years)
   - Select scopes:
     - `repo` (for private repositories)
     - `read:org` (if in an organization)
   - Generate and copy the token (starts with "ghp_")

2. **Update the Configuration**:
   ```json
   "github": {
       "repository_url": "https://github.com/VoidReturn0/AutomationAcademy.git",
       "api_token": "ghp_yourActualGitHubToken",
       "check_interval_hours": 6,
       "auto_download": false,
       "use_deploy_key": false
   }
   ```

3. **Alternative: Use Environment Variable**:
   ```bash
   export GITHUB_API_TOKEN="ghp_yourActualGitHubToken"
   ```

## JWT Token Storage

If you need to store the JWT token for other purposes, we can add a separate configuration section:

```json
"authentication": {
    "jwt_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_expiry": "2030-05-19T00:00:00Z"
}
```

## Note About Token Security

- Never commit real tokens to version control
- Use environment variables for production
- Consider encrypting tokens in configuration files
- Rotate tokens periodically

The JWT token you provided may be for a different purpose (perhaps internal authentication). GitHub API requires their specific personal access tokens for repository access.