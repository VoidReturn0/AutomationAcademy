# Automation Academy - Data Sync Repository

This repository is used for synchronizing training data between Automation Academy installations.

## Purpose

This is a **data-only repository** - it does not contain application source code. The application code is maintained separately.

## Structure

```
├── UserData/           # User progress and completion data
│   ├── Progress/       # Individual user progress tracking
│   ├── Completions/    # Module completion records
│   └── Audit/          # Append-only audit trail
├── Modules/            # Training module content
│   ├── Training/       # Training module definitions
│   └── Assessments/    # Quiz and assessment data
├── References/         # Reference materials
│   ├── Materials/      # PDF and document references
│   └── XAML/           # XAML-based reference content
└── LICENSE
```

## Data Format

- User data is stored as JSON files
- Module content uses the Automation Academy module format
- All timestamps are in UTC
- Files are synced using SHA-based versioning for idempotent operations

## Security

- No sensitive credentials are stored in this repository
- User progress data may be encrypted
- Personal information follows data minimization principles

## Sync Operations

The Automation Academy application uses this repository for:
1. **Content Sync**: Download latest training modules and references
2. **Progress Push**: Upload user progress and completion data
3. **Offline Queue**: Queue operations when offline for later sync

---
*Broetje Automation USA - Training Academy Data Repository*
