### Step 1: Download UltraVNC Server
1. Visit UltraVNC website# Remote Access Configuration Guide
**VNC and Teams Screen Sharing for Machine Support**

---

## Overview
This guide covers setting up remote access tools for troubleshooting and support at Broetje Automation. We use VNC for machine internal networks and Teams for external support access.

---

## Part 1: Understanding Remote Access Tools

### UltraVNC (Ultra Virtual Network Computing)
- High-performance VNC implementation
- Optimized for Windows systems
- File transfer capabilities
- Used for machine internal networks

### Microsoft Teams Screen Sharing
- Internet-based connection
- Secure corporate authentication
- Built-in recording capability
- Chat and collaboration features
- Used for customer support sessions

---

## Part 2: VNC Server Installation

### Step 1: Download UltraVNC Server
1. Visit UltraVNC website
2. Download UltraVNC Server (Windows version)
3. Choose appropriate version (x86 or x64)
4. Download to D:\Temp\(YourInitials)

### Step 2: Install UltraVNC Server
1. Run installer as Administrator
2. Select "Complete" installation
3. Choose components:
   - UltraVNC Server (essential)
   - UltraVNC Viewer (recommended)
4. Accept license agreement
5. Complete installation

### Step 3: Initial Configuration
1. Launch UltraVNC Server
2. Right-click UltraVNC Server icon in system tray
3. Select "Admin Properties"
4. Set security options:
   - Password: ae746 (standard Broetje password)
   - Port: 5900 (default)
5. Apply settings

### Step 4: Basic UltraVNC Settings
1. In Admin Properties:
   - Check "Auto Accept incoming connections"
   - Enable "Remove Desktop Wallpaper"
   - Enable "Remove Desktop Effects"
2. Set HTTP/HTTPS ports if needed
3. Configure logging (optional)

---

## Part 3: VNC Client Connection

### Step 1: Install VNC Viewer
1. Download VNC Viewer
2. Install on support laptop
3. Launch application

### Step 2: Create Connection
1. Click "Add Connection" or "New Connection"
2. Enter connection details:
   - VNC Server: IP:Port (192.168.214.34:5900)
   - Name: [Machine_Name]_[Customer]
   - Password: ae746
3. Save connection for quick access

### Step 3: Connect to Machine
1. Double-click saved connection
2. Wait for connection to establish
3. Desktop will appear in viewer window
4. Verify successful connection

### Step 4: Session Management
- Use Ctrl+Alt+Del for secure attention
- Enable/disable full screen mode
- Adjust quality settings for bandwidth
- Capture screenshots as needed

---

## Part 4: Teams Screen Sharing Setup

### Step 1: Teams Installation
1. Open Microsoft Teams
2. Sign in with company credentials
3. Update to latest version
4. Configure audio/video settings

### Step 2: Prepare for Support Session
1. Close sensitive applications
2. Arrange desktop for clarity
3. Test audio and video
4. Prepare troubleshooting tools

### Step 3: Start Screen Share
1. Join/start Teams meeting
2. Click "Share" button
3. Choose sharing option:
   - Desktop: Full screen sharing
   - Window: Specific application
   - PowerPoint: Presentation mode
4. Click "Share"

### Step 4: Remote Control
1. Click "Give control" button
2. Select participant
3. Grant mouse/keyboard access
4. Monitor remote actions
5. End control when finished

---

## Part 5: Security and Best Practices

### VNC Security
```
Network ACL Configuration:
Allow: 192.168.213.0/24
Allow: 192.168.214.0/24
Deny: All others

Firewall Rules:
Inbound: TCP 5900 (VNC)
Inbound: TCP 5800 (VNC HTTP)
Outbound: TCP 5900
```

### Teams Security
1. Use company-issued accounts only
2. Enable multi-factor authentication
3. Verify meeting participants
4. Use waiting room feature
5. Record sessions for documentation

### Password Management
1. Use strong, unique passwords
2. Change passwords quarterly
3. Document in password manager
4. Never share credentials via email/chat
5. Use secure key-sharing methods

---

## Part 6: Practice Exercises

### Exercise 1: VNC Setup
1. Install VNC Server on test machine
2. Configure security settings
3. Set up network restrictions
4. Create VNC Viewer connection
5. Test remote desktop access
6. Practice file transfer

### Exercise 2: Teams Screen Sharing
1. Schedule test meeting
2. Share screen with trainer
3. Pass remote control
4. Troubleshoot simulated issue
5. Record session
6. Review recording

### Exercise 3: Troubleshooting Session
1. Connect to remote machine via VNC
2. Diagnose prepared system issue
3. Document findings
4. Implement solution remotely
5. Verify fix with customer via Teams
6. Complete session documentation

**Time to complete**: 45-60 minutes

---

## Part 7: Troubleshooting Guide

### UltraVNC Connection Issues

**Cannot Connect to Server**
1. Verify IP address and port
2. Check that UltraVNC Server is running
3. Test network connectivity with ping
4. Confirm password is "ae746"
5. Verify services are running

**Slow Performance**
1. Close unnecessary applications on target machine
2. Adjust compression settings in viewer
3. Check network bandwidth availability
4. Update network drivers if needed
5. Use LAN connection instead of Wi-Fi

**Display Problems**
1. Update graphics drivers
2. Adjust color depth settings
3. Enable/disable desktop effects
4. Try different viewer scaling options
5. Check monitor resolution compatibility

### Teams Issues

**Screen Share Not Working**
1. Update Teams application
2. Check camera permissions
3. Restart Teams application
4. Clear Teams cache
5. Test different browser

**Audio/Video Problems**
1. Check device settings
2. Update audio drivers
3. Test microphone
4. Adjust bandwidth settings
5. Use dial-in option

**Remote Control Issues**
1. Re-grant control privileges
2. Check user permissions
3. Restart screen share
4. Verify network stability
5. Use alternative sharing method

---

## Part 8: Documentation Template

### Remote Session Log
```
Session Type: VNC / Teams (circle one)
Date: ________________  Time: ________________

Target System:
- Machine ID: _________________________
- Customer: ___________________________
- IP Address: _________________________
- VNC Port: ___________________________

Session Details:
- Purpose: ____________________________
- Duration: ___________________________
- Participants: ________________________
- Issues Addressed: ____________________

Technical Actions:
1. ___________________________________
2. ___________________________________
3. ___________________________________

Resolution:
- Status: Complete/Pending/Failed
- Next Steps: _________________________
- Follow-up Required: __________________

Technician: _______________ ID: _________
Customer Rep: _____________ ID: _________
```

---

## Part 9: Advanced Configuration

### VNC Advanced Settings
```
Registry Location: HKEY_LOCAL_MACHINE\Software\RealVNC\vncserver

Key Settings:
- Authentication: VncAuth
- Encryption: PreferEncryption
- IdleTimeout: 3600
- AcceptKeyEvents: 1
- AcceptPointerEvents: 1
- RemoveWallpaper: 1
- DisableEffects: 1
```

### Teams Policy Configuration
```
PowerShell Commands:
Set-CsTeamsMeetingPolicy -Identity "Remote Support" -AllowTranscription $true
Set-CsTeamsMeetingPolicy -Identity "Remote Support" -RecordingStorageMode "Stream"
Set-CsTeamsMeetingPolicy -Identity "Remote Support" -AllowCloudRecording $true
```

### Network Optimization
```
QoS Settings for VNC:
Port: 5900
Protocol: TCP
DSCP: 34
Bandwidth: Medium priority

QoS Settings for Teams:
Port Range: 50000-50200
Protocol: UDP
DSCP: 46
Bandwidth: High priority
```

---

## Part 10: Quick Reference

### VNC Shortcuts
```
Ctrl+Alt+Del - Send secure attention
Ctrl+Alt+Shift+F - Full screen toggle
Ctrl+Alt+Shift+S - Take screenshot
Ctrl+Alt+Shift+T - Transfer files
Ctrl+Alt+Shift+C - Chat window
```

### Teams Shortcuts
```
Ctrl+Shift+M - Mute/unmute
Ctrl+Shift+O - Camera on/off
Ctrl+E - Search
Ctrl+Shift+E - Share screen
Ctrl+Period - Show keyboard shortcuts
```

### Connection Syntax
- VNC: `viewer://[server]:[port]`
- Teams: `msteams://teams.microsoft.com/l/meetup-join`

---

## Checklist
- [ ] VNC Server installed and configured
- [ ] VNC password set and documented
- [ ] VNC Viewer tested successfully
- [ ] Teams screen sharing tested
- [ ] Remote control verified
- [ ] Security settings configured
- [ ] Documentation completed

**Trainer Initials**: _______ **Trainee Initials**: _______

---

## Emergency Access Procedures

### Lost VNC Access
1. Physical console access
2. VNC Server service restart
3. Registry key reset
4. Firewall rule verification
5. Network trace analysis

### Teams Connectivity Issues
1. Browser-based access
2. Mobile app backup
3. Phone dial-in option
4. Alternative meeting platform
5. Email escalation protocol