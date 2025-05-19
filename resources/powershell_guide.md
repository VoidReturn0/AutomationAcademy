# PowerShell Scripting Guide
**Modern Windows Automation for Technical Tasks**

---

## Overview
PowerShell is Microsoft's advanced command-line shell and scripting language. Unlike batch files, PowerShell provides object-oriented programming capabilities, better error handling, and more powerful automation features.

---

## Part 1: PowerShell vs Batch Files

### Key Differences

**Batch Files (.bat)**
- Text-based commands
- Limited error handling
- String manipulation only
- DOS-era commands
- Simple syntax

**PowerShell Scripts (.ps1)**
- Object-oriented programming
- Rich error handling
- Works with .NET objects
- Cmdlet-based (verb-noun structure)
- More powerful and flexible

### When to Use Each
- **Batch**: Simple tasks, legacy compatibility
- **PowerShell**: Complex automation, system administration, data processing

### PowerShell Advantages
- Better error handling
- More robust networking capabilities
- Built-in help system
- Active Directory integration
- WMI (Windows Management Instrumentation) access

---

## Part 2: PowerShell Fundamentals

### Opening PowerShell
1. **Regular PowerShell**:
   - Start → Type "PowerShell"
   - Windows key + X → "Windows PowerShell"

2. **Administrator PowerShell**:
   - Right-click Start → "Windows PowerShell (Admin)"
   - Or search PowerShell → Right-click → "Run as Administrator"

### Basic Cmdlets
```powershell
Get-Help           # Get help for any cmdlet
Get-Command        # List all available cmdlets
Get-Location       # Show current directory (like CD)
Set-Location       # Change directory
Get-ChildItem      # List directory contents (like DIR)
Copy-Item          # Copy files/folders
Move-Item          # Move files/folders
Remove-Item        # Delete files/folders
New-Item           # Create new file/folder
```

### PowerShell Syntax
- Cmdlets follow Verb-Noun pattern (Get-Item, Set-Location)
- Parameters start with dash (-Path, -Name)
- Variables start with $ ($variable)
- Comments use # or <# ... #>

---

## Part 3: Creating Your First PowerShell Script

### Step 1: Set Up Working Directory
```powershell
# Create script directory
New-Item -Path "D:\Temp\$env:USERNAME\PowerShellScripts" -ItemType Directory
Set-Location "D:\Temp\$env:USERNAME\PowerShellScripts"

# Create test file
"Hello from Broetje Automation!" | Out-File -FilePath "Hello_World.txt"
```

### Step 2: Create Basic Script
```powershell
# Save as OpenHelloWorld.ps1
# Clear screen
Clear-Host

# Display message
Write-Host "Opening Hello World file..." -ForegroundColor Green

# Define file path
$filePath = "D:\Temp\$env:USERNAME\PowerShellScripts\Hello_World.txt"

# Check if file exists
if (Test-Path $filePath) {
    # Open file in Notepad
    Start-Process notepad.exe -ArgumentList $filePath
    Write-Host "File opened successfully!" -ForegroundColor Green
} else {
    Write-Host "File not found: $filePath" -ForegroundColor Red
}

# Pause for user input
Read-Host "Press Enter to exit"
```

### Step 3: Run Your Script
```powershell
# Enable script execution (run once)
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

# Run the script
.\OpenHelloWorld.ps1
```

---

## Part 4: Advanced PowerShell Features

### Working with Objects
```powershell
# Get network adapters
$adapters = Get-NetAdapter

# Filter for active adapters
$activeAdapters = $adapters | Where-Object { $_.Status -eq "Up" }

# Display information
$activeAdapters | Format-Table Name, Status, MacAddress

# Get IP configuration
Get-NetIPConfiguration | Format-Table InterfaceAlias, IPv4Address, IPv4DefaultGateway
```

### Error Handling
```powershell
try {
    $filePath = "D:\Temp\$env:USERNAME\TestFiles\Hello_World.txt"
    
    if (Test-Path $filePath) {
        Start-Process notepad.exe -ArgumentList $filePath
        Write-Host "Success: File opened" -ForegroundColor Green
    } else {
        throw "File not found: $filePath"
    }
}
catch {
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host "Please check file path and try again" -ForegroundColor Yellow
}
finally {
    Write-Host "Operation completed" -ForegroundColor Blue
}
```

### Functions and Parameters
```powershell
function Test-BroetjeNetwork {
    param(
        [string]$TargetIP = "192.168.214.1",
        [int]$Count = 4
    )
    
    Write-Host "Testing connectivity to $TargetIP..." -ForegroundColor Cyan
    
    try {
        $result = Test-Connection -ComputerName $TargetIP -Count $Count -ErrorAction Stop
        Write-Host "SUCCESS: Average response time: $($result | Measure-Object -Property ResponseTime -Average | Select-Object -ExpandProperty Average)ms" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "FAILED: Unable to reach $TargetIP" -ForegroundColor Red
        return $false
    }
}

# Usage
Test-BroetjeNetwork -TargetIP "192.168.214.34" -Count 3
```

---

## Part 5: Broetje-Specific PowerShell Scripts

### Network Diagnostic Script
```powershell
# Save as Broetje-NetworkDiagnostics.ps1
param(
    [string]$OutputPath = "D:\Temp\$env:USERNAME\NetworkDiagnostics.txt"
)

# Define Broetje network devices
$broetjeDevices = @{
    "NCU Controller" = "192.168.214.1"
    "Service PC" = "192.168.214.34"
    "Operator PC" = "192.168.214.35"
    "Scale PC (Vision)" = "192.168.214.37"
    "Ketop Tablet 1" = "192.168.214.38"
    "Riveter PC" = "192.168.214.60"
    "RTX System" = "192.168.213.33"
}

# Initialize report
$report = @()
$report += "=========================================="
$report += "Broetje Network Diagnostic Report"
$report += "Date: $(Get-Date)"
$report += "Performed by: $env:USERNAME"
$report += "=========================================="
$report += ""

# Test each device
foreach ($device in $broetjeDevices.GetEnumerator()) {
    Write-Host "Testing $($device.Key)..." -ForegroundColor Yellow
    
    try {
        $ping = Test-Connection -ComputerName $device.Value -Count 1 -ErrorAction Stop
        $status = "ONLINE"
        $responseTime = "$($ping.ResponseTime)ms"
        $color = "Green"
    }
    catch {
        $status = "OFFLINE"
        $responseTime = "N/A"
        $color = "Red"
    }
    
    $line = "$($device.Key.PadRight(20)) $($device.Value.PadRight(15)) $status $responseTime"
    $report += $line
    Write-Host $line -ForegroundColor $color
}

# Save report
$report | Out-File -FilePath $OutputPath -Encoding utf8
Write-Host "`nReport saved to: $OutputPath" -ForegroundColor Cyan

# Open report
Start-Process notepad.exe -ArgumentList $OutputPath
```

### Backup Management Script
```powershell
# Save as Broetje-BackupManager.ps1
function New-BroetjeBackup {
    param(
        [Parameter(Mandatory)]
        [string]$MachineNumber,
        
        [Parameter(Mandatory)]
        [string]$MachineInitials,
        
        [Parameter(Mandatory)]
        [ValidateSet('NC','DD','HMI','PLC','S7','Cisco','PLUTO','TGZ','SICK','CU')]
        [string]$BackupType,
        
        [string]$SourcePath,
        [string]$DestinationPath = "\\server\backups"
    )
    
    # Generate backup filename
    $date = Get-Date -Format "yyyyMMdd"
    $backupName = "${MachineNumber}_${MachineInitials}_${BackupType}_${date}"
    
    # Create destination directory if needed
    $destDir = Join-Path $DestinationPath $MachineNumber
    if (!(Test-Path $destDir)) {
        New-Item -Path $destDir -ItemType Directory -Force
    }
    
    # Define backup destination
    $destFile = Join-Path $destDir "${backupName}.zip"
    
    Write-Host "Creating backup: $backupName" -ForegroundColor Green
    
    try {
        # Compress source to destination
        if ($SourcePath) {
            Compress-Archive -Path $SourcePath -DestinationPath $destFile -Force
        }
        
        Write-Host "Backup completed successfully: $destFile" -ForegroundColor Green
        
        # Log the backup
        $logEntry = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - Created backup: $backupName"
        Add-Content -Path "D:\Temp\$env:USERNAME\backup_log.txt" -Value $logEntry
        
        return $destFile
    }
    catch {
        Write-Host "Backup failed: $_" -ForegroundColor Red
        return $null
    }
}

# Usage example
# New-BroetjeBackup -MachineNumber "AP1741" -MachineInitials "R1" -BackupType "NC" -SourcePath "C:\Siemens\Data"
```

### File Transfer Script
```powershell
# Save as Broetje-FileTransfer.ps1
function Copy-ToMachine {
    param(
        [Parameter(Mandatory)]
        [string]$SourceFile,
        
        [Parameter(Mandatory)]
        [string]$TargetIP,
        
        [string]$RemotePath = "C:\Temp",
        [PSCredential]$Credential
    )
    
    Write-Host "Transferring file to $TargetIP..." -ForegroundColor Cyan
    
    try {
        # Test network connectivity first
        if (!(Test-Connection -ComputerName $TargetIP -Count 1 -Quiet)) {
            throw "Cannot reach target machine: $TargetIP"
        }
        
        # Create remote session
        $sessionParams = @{
            ComputerName = $TargetIP
        }
        
        if ($Credential) {
            $sessionParams.Credential = $Credential
        }
        
        $session = New-PSSession @sessionParams
        
        # Copy file
        Copy-Item -Path $SourceFile -Destination $RemotePath -ToSession $session -Force
        
        Write-Host "File transferred successfully!" -ForegroundColor Green
        
        # Clean up
        Remove-PSSession $session
    }
    catch {
        Write-Host "Transfer failed: $_" -ForegroundColor Red
    }
}

# Usage example
# Copy-ToMachine -SourceFile "D:\Temp\test.txt" -TargetIP "192.168.214.35"
```

---

## Part 6: Script Execution and Startup

### Creating PowerShell Startup Scripts
```powershell
# Save as Startup-BroetjeTasks.ps1
# This runs when user logs in

# Set up logging
$logFile = "D:\Temp\$env:USERNAME\startup_log.txt"
Add-Content $logFile "$(Get-Date): Startup script initiated"

# Wait for network to be ready
Start-Sleep -Seconds 5

# Test critical network connections
$criticalIPs = @("192.168.214.1", "192.168.214.34", "192.168.214.60")
foreach ($ip in $criticalIPs) {
    if (Test-Connection -ComputerName $ip -Count 1 -Quiet) {
        Add-Content $logFile "$(Get-Date): $ip - ONLINE"
    } else {
        Add-Content $logFile "$(Get-Date): $ip - OFFLINE"
    }
}

# Open Hello World file
$helloFile = "D:\Temp\$env:USERNAME\PowerShellScripts\Hello_World.txt"
if (Test-Path $helloFile) {
    Start-Process notepad.exe -ArgumentList $helloFile
    Add-Content $logFile "$(Get-Date): Opened Hello World file"
}

Add-Content $logFile "$(Get-Date): Startup script completed"
```

### Adding to Windows Startup
```powershell
# Create a scheduled task to run PowerShell script at logon
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-File 'D:\Temp\$env:USERNAME\PowerShellScripts\Startup-BroetjeTasks.ps1'"
$trigger = New-ScheduledTaskTrigger -AtLogOn
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries

Register-ScheduledTask -TaskName "BroetjeStartup" -Action $action -Trigger $trigger -Principal $principal -Settings $settings
```

---

## Part 7: Practice Exercises

### Exercise 1: Basic Script Creation
1. Create a script that:
   - Creates your directory structure
   - Generates test files
   - Opens a file in Notepad
   - Logs all operations

2. Add error handling for missing paths

### Exercise 2: Network Automation
1. Create a script to:
   - Test connectivity to all Broetje devices
   - Generate a report with timestamps
   - Format output in a table
   - Save results to a dated file

### Exercise 3: Data Processing
1. Build a script that:
   - Reads a CSV file
   - Filters data based on criteria
   - Exports results to new file
   - Generates summary statistics

**Time to complete**: 90-120 minutes

---

## Part 8: Debugging and Best Practices

### Debugging Techniques
```powershell
# Use Write-Debug for troubleshooting
$DebugPreference = "Continue"
Write-Debug "Variable value: $myVariable"

# Verbose output
$VerbosePreference = "Continue"
Write-Verbose "Processing file: $file"

# Step through code
Set-PSBreakpoint -Script .\myscript.ps1 -Line 10
```

### Best Practices
1. **Use approved verbs**: Get-Command | Get-Verb
2. **Comment your code** thoroughly
3. **Handle errors gracefully** with try/catch
4. **Validate parameters** before use
5. **Use modules** for reusable functions

### Script Template
```powershell
<#
.SYNOPSIS
    Brief description of script purpose
.DESCRIPTION
    Detailed description of what script does
.PARAMETER InputFile
    Path to input file
.EXAMPLE
    .\MyScript.ps1 -InputFile "C:\data.csv"
.NOTES
    Author: Your Name
    Date: 2025-01-19
    Version: 1.0
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [string]$InputFile,
    
    [string]$OutputPath = "C:\Output"
)

begin {
    # Initialization code
    Write-Verbose "Starting script..."
}

process {
    # Main script logic
    try {
        # Your code here
    }
    catch {
        Write-Error "Error: $_"
        throw
    }
}

end {
    # Cleanup code
    Write-Verbose "Script completed"
}
```

---

## Part 9: Comparison Reference

### Batch vs PowerShell Examples

**File Operations**
```batch
REM Batch
copy source.txt dest.txt
del oldfile.txt
mkdir newdir
```

```powershell
# PowerShell
Copy-Item -Path "source.txt" -Destination "dest.txt"
Remove-Item -Path "oldfile.txt"
New-Item -Path "newdir" -ItemType Directory
```

**Network Operations**
```batch
REM Batch
ping 192.168.214.1
ipconfig /all
```

```powershell
# PowerShell
Test-Connection -ComputerName "192.168.214.1"
Get-NetIPConfiguration
```

**Variables and Logic**
```batch
REM Batch
set VAR=value
if "%VAR%"=="value" echo Match found
```

```powershell
# PowerShell
$var = "value"
if ($var -eq "value") { Write-Host "Match found" }
```

---

## Part 10: Documentation Template

### PowerShell Script Documentation
```
Script Name: ____________________________
Created By: ______________________________
Created Date: ____________________________
Last Modified: ___________________________
Purpose: _________________________________

Parameters:
- InputFile: _____________________________
- OutputPath: ____________________________
- Verbose: _______________________________

Dependencies:
- PowerShell Version: 5.0+
- Modules Required: ______________________
- Network Access: ________________________

Error Handling:
- Try/Catch blocks: Yes/No
- Logging enabled: Yes/No
- Validation checks: ______________________

Testing Results:
[ ] Script executes without errors
[ ] Parameters validated correctly
[ ] Output formatted properly
[ ] Error handling effective
[ ] Performance acceptable

Notes:
_________________________________________
_________________________________________
```

---

## Quick Reference

### Essential Cmdlets
```powershell
Get-Help cmdlet -Full        # Detailed help
Get-Command -Verb Get        # All Get cmdlets
Get-Member                   # Object properties/methods
Where-Object {$_.Name -like "*"}  # Filter objects
ForEach-Object               # Process each object
Select-Object                # Select properties
Measure-Object               # Statistics
Group-Object                 # Group data
Sort-Object                  # Sort objects
```

### Common Parameters
```powershell
-Path          # File/folder path
-Destination   # Target location
-Force         # Override protections
-WhatIf        # Preview changes
-Confirm       # Confirm actions
-ErrorAction   # Error handling
-Verbose       # Detailed output
```

---

## Checklist
- [ ] PowerShell execution policy set
- [ ] Created basic PowerShell script
- [ ] Added error handling
- [ ] Implemented logging
- [ ] Created network diagnostic script
- [ ] Set up scheduled task for startup
- [ ] Tested all functionality
- [ ] Documented scripts properly

**Trainer Initials**: _______ **Trainee Initials**: _______

---

## Advanced Topics

### Modules and Functions
```powershell
# Create reusable module
function Get-BroetjeDeviceStatus {
    # Export function to module
}
Export-ModuleMember -Function Get-BroetjeDeviceStatus
```

### Remote Administration
```powershell
# Execute commands on remote machines
Invoke-Command -ComputerName "192.168.214.35" -ScriptBlock { Get-Service }
```

### Integration with .NET
```powershell
# Use .NET classes directly
[System.IO.File]::ReadAllText("C:\data.txt")
```