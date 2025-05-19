# Completion Tracking System

## Overview

The Broetje Training System now includes a comprehensive completion tracking system that:

1. Organizes screenshots with meaningful naming conventions
2. Automatically uploads completion data to GitHub
3. Tracks real-time training progress across the organization

## Features

### Screenshot Organization

Screenshots are now saved with the following structure:
```
completion_data/
├── screenshots/
│   ├── john_doe/
│   │   ├── network_file_sharing/
│   │   │   ├── task1_20241218_143052.png
│   │   │   ├── task2_20241218_143215.png
│   │   │   └── task3_20241218_143342.png
│   │   └── cli_diagnostics/
│   │       ├── task1_20241218_151023.png
│   │       └── task2_20241218_151145.png
│   └── jane_smith/
│       └── ...
```

### Completion Reports

Each completion generates a comprehensive JSON report containing:
- User information (username, full name, role)
- Module details (ID, name, version)
- Completion data (timestamp, score, elapsed time, completed tasks)
- Screenshot paths
- Digital signature
- Verification hash

### GitHub Integration

When enabled, the system automatically uploads:
- Completion reports
- Screenshots
- Updates a centralized dashboard

## Configuration

Edit `config/github_config.json`:

```json
{
    "completion_tracking": {
        "enabled": true,
        "upload_screenshots": true,
        "repository": "broetje-automation/training-completion-tracking",
        "branch": "main",
        "token": "${GITHUB_TOKEN}"
    }
}
```

## GitHub Repository Structure

The tracking repository has the following structure:
```
completion_tracking/
├── dashboard.json              # Real-time completion dashboard
├── john_doe/
│   ├── network_file_sharing/
│   │   ├── report_20241218_143400.json
│   │   └── screenshots/
│   │       ├── task1_20241218_143052.png
│   │       ├── task2_20241218_143215.png
│   │       └── task3_20241218_143342.png
│   └── cli_diagnostics/
│       ├── report_20241218_151200.json
│       └── screenshots/
│           └── ...
└── jane_smith/
    └── ...
```

## Dashboard

The dashboard.json file provides:
- Total completions
- User-specific completion history
- Module statistics (completion count, average scores)
- Last update timestamp

## Security

- Screenshots are only uploaded if explicitly enabled
- GitHub token should be stored as an environment variable
- All data is verified with SHA-256 hashes

## Local Storage

Even if GitHub upload fails, all data is saved locally:
- Screenshots in `completion_data/screenshots/`
- Reports in `completion_data/reports/`

## Usage

1. Complete a training module
2. Take screenshots when prompted
3. Sign the completion form
4. System automatically:
   - Saves organized screenshots
   - Creates completion report
   - Uploads to GitHub (if enabled)
   - Updates dashboard

## Monitoring Progress

Access the GitHub repository to view:
- Real-time completion dashboard
- Individual user progress
- Module completion statistics
- Screenshot evidence

## Troubleshooting

If uploads fail:
1. Check GitHub token configuration
2. Verify internet connection
3. Check repository permissions
4. Review logs in `training_app.log`

All data is saved locally even if upload fails, and can be manually uploaded later.