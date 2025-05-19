# Basic Computer Requirements Training Checklist
**Broetje Automation USA - Technical Competency Assessment**

---

## Overview
This checklist verifies essential computer skills required for technical support roles at Broetje Automation. Each skill builds upon previous knowledge, creating a comprehensive training pathway. Complete modules in sequence for optimal learning.

**Trainee:** _________________________________ **Date:** _______________  
**Trainer:** _________________________________ **Completion Time:** _______________

---

## Module 1: Network File Sharing & Mapping
**Objective:** Master network file operations using Broetje standards

**Tasks:**
- [ ] Share folder on D: drive
- [ ] Map shared folder as network drive on remote PC
- [ ] Create folder structure: `D:\Temp\[User Initials]` on both PCs
- [ ] Transfer test file between PCs using mapped drive
- [ ] Verify file transfer successful

**Verification Signature:** ______________________ **Pass/Fail:** ________

---

## Module 2: Command Line Network Diagnostics
**Objective:** Use CLI tools for Broetje network troubleshooting

**Tasks:**
- [ ] Open Command Prompt (CMD)
- [ ] Execute ping tests to all Broetje networks:
  - [ ] Service PC: `ping 192.168.214.34`
  - [ ] Operator PC: `ping 192.168.214.35`
  - [ ] Riveter PC: `ping 192.168.214.60`
  - [ ] RTX System: `ping 192.168.213.33`
- [ ] Use advanced network commands:
  - [ ] `arp -a` to view MAC addresses
  - [ ] `netstat -an` to view connections
  - [ ] `pathping 192.168.214.1` to NCU
- [ ] Document all results with timestamps

**Verification Signature:** ______________________ **Pass/Fail:** ________

---

## Module 3: IP Address Configuration
**Objective:** Configure IP addresses for Broetje machine networks

**Tasks:**
- [ ] Access Network and Sharing Center
- [ ] Configure static IP for machine network (192.168.214.x)
- [ ] Test connectivity to all device IPs
- [ ] Switch to riveter network (192.168.213.x)
- [ ] Test RTX system connectivity
- [ ] Configure video network (192.168.1.x)
- [ ] Return to DHCP configuration
- [ ] Document all IP configurations used

**Verification Signature:** ______________________ **Pass/Fail:** ________

---

## Module 4: Hard Drive Management
**Objective:** Manage drive letters and assignments

**Tasks:**
- [ ] Open Disk Management (diskmgmt.msc)
- [ ] Assign drive letter to USB device
- [ ] Change drive letter of existing hard drive
- [ ] View and document current drive assignments
- [ ] Remove and reassign USB device drive letter
- [ ] Verify all changes in File Explorer

**Verification Signature:** ______________________ **Pass/Fail:** ________

---

## Module 5: Backup/Restore Operations
**Objective:** Perform system backup and restore using Paragon software with Broetje naming standards

**Tasks:**
- [ ] Open Paragon Backup & Recovery software
- [ ] Create system backup of test Siemens IPC
- [ ] Name backup following Broetje standards:
  - Format: `[Machine#]_[Initials]_[Type]_[YYYYMMDD]`
  - Example: `AP1741_R1_NC_20250819`
- [ ] Verify backup file location and size
- [ ] Prepare blank hard drive for restoration
- [ ] Restore backup image to blank drive
- [ ] Verify successful boot from restored drive

**Verification Signature:** ______________________ **Pass/Fail:** ________

---

## Module 6: Hard Drive Replacement
**Objective:** Replace HDD with SSD using Torx tools

**Tasks:**
- [ ] Power down Siemens IPC safely
- [ ] Remove existing hard drive using Torx drivers
- [ ] Install new SSD drive (minimum 250GB)
- [ ] Boot system and verify BIOS/UEFI recognition
- [ ] Complete successful restoration from backup
- [ ] Verify system boots successfully
- [ ] Document drive specifications and installation date

**Verification Signature:** ______________________ **Pass/Fail:** ________

---

## Module 7: Remote Access Configuration
**Objective:** Set up UltraVNC with standard Broetje settings

**Tasks:**
- [ ] Install UltraVNC server on machine
- [ ] Configure with standard password: ae746
- [ ] Connect to machine using UltraVNC client from external PC
- [ ] Configure Microsoft Teams for screen sharing
- [ ] Successfully share screen via Teams
- [ ] Demonstrate remote control capabilities
- [ ] End remote sessions properly

**Verification Signature:** ______________________ **Pass/Fail:** ________

---

## Module 8A: Batch File Scripting
**Objective:** Create basic batch file automation

**Tasks:**
- [ ] Create folder `D:\Temp\[User Initials]\BatchScripts`
- [ ] Create text file "Hello World.txt"
- [ ] Create .bat file that opens this text file
- [ ] Configure .bat file to run at startup
- [ ] Test batch file execution manually
- [ ] Verify auto-start functionality after reboot
- [ ] Document batch file content

**Verification Signature:** ______________________ **Pass/Fail:** ________

---

## Module 8B: PowerShell Scripting
**Objective:** Create PowerShell automation scripts

**Tasks:**
- [ ] Set PowerShell execution policy
- [ ] Create PowerShell script that opens Hello World.txt
- [ ] Add error handling to script
- [ ] Create network diagnostic PowerShell script
- [ ] Set up scheduled task for startup
- [ ] Test all PowerShell functionality
- [ ] Document script purposes and usage

**Verification Signature:** ______________________ **Pass/Fail:** ________

---

## Module 9: OneDrive Integration
**Objective:** Set up enterprise file sharing

**Tasks:**
- [ ] Install/configure OneDrive with Broetje account
- [ ] Create folder structure for customer backups
- [ ] Upload test file (>100MB recommended)
- [ ] Generate sharing link with expiration
- [ ] Test download from shared link on different device
- [ ] Configure sync settings for storage optimization
- [ ] Document sharing permissions used

**Verification Signature:** ______________________ **Pass/Fail:** ________

---

## Final Assessment

**Overall Performance:** _____ / 10 modules completed successfully

**Module Completion Summary:**
- [ ] Network fundamentals mastered
- [ ] Command line proficiency demonstrated  
- [ ] IP configuration competent
- [ ] Drive management successful
- [ ] Backup/restore procedures verified
- [ ] Hardware replacement completed
- [ ] Remote access configured
- [ ] Scripting (Batch & PowerShell) functional
- [ ] Enterprise file sharing operational

**Training Pathway Competencies:**
- Level 1: Basic Network Operations (Modules 1-3)
- Level 2: System Administration (Modules 4-6)
- Level 3: Remote Support (Module 7)
- Level 4: Automation & Collaboration (Modules 8-9)

**Trainer Comments:**
```
_________________________________________________________
_________________________________________________________
_________________________________________________________
_________________________________________________________
```

**Recommend for:**
- [ ] Advanced Technical Training
- [ ] Field Service Assignment (Customer Sites)
- [ ] Remote Support Team Assignment
- [ ] Additional Practice Required
- [ ] Specialized Training Needed

**Areas for Additional Focus:**
- [ ] Network diagnostics
- [ ] Remote troubleshooting
- [ ] Backup restoration procedures
- [ ] Script development
- [ ] Customer communication

**Training Completion Certification:**

**Trainer Signature:** _________________________ **Date:** _______________

**Trainee Signature:** _________________________ **Date:** _______________

**Training Coordinator:** ______________________ **Date:** _______________

---

## Quality Assurance Review

**Pre-Customer Deployment Checklist:**
- [ ] Successfully completed all 10 modules
- [ ] Demonstrated competency in customer environment simulation
- [ ] Passed practical troubleshooting scenarios
- [ ] Completed documentation requirements
- [ ] Ready for mentored customer support

**Post-Training Support Plan:**
1. **Week 1-2**: Shadow experienced technician on customer sites
2. **Week 3-4**: Handle simple tickets with supervision
3. **Month 2**: Begin independent remote support
4. **Month 3**: Review and advanced training assessment

**Emergency Procedures Verified:**
- [ ] Machine crash recovery
- [ ] Network outage troubleshooting
- [ ] Remote access failure backup plans
- [ ] Customer communication protocols
- [ ] Escalation procedures

---

## Additional Resources

**Reference Materials Provided:**
- [ ] Broetje Network Diagram
- [ ] Customer IP Address Spreadsheet
- [ ] Backup Naming Convention Guide
- [ ] VNC Password Reference
- [ ] PowerShell Script Repository

**Online Resources Access:**
- [ ] Internal knowledge base credentials
- [ ] Microsoft Teams training channel
- [ ] PowerShell documentation portal
- [ ] Siemens IPC documentation
- [ ] Customer support ticketing system

**Support Contacts:**
- Senior Technician: ______________________
- Team Lead: _____________________________
- IT Support: ____________________________
- Training Questions: _____________________

---

## Continuous Improvement

**Skills Maintenance Schedule:**
- Monthly: Network diagram review
- Quarterly: Backup/restore practice
- Semi-annually: PowerShell skills refresh
- Annually: Full competency re-certification

**Advanced Training Opportunities:**
- [ ] Advanced PowerShell automation
- [ ] Siemens PLC programming basics
- [ ] Customer communication excellence
- [ ] Advanced troubleshooting techniques
- [ ] Leadership development pathway

---

*This training checklist completes the comprehensive computer skills development program for Broetje Automation technical support staff. All modules align with real-world customer support requirements and company operational standards.*# Basic Computer Requirements Training Checklist
**Broetje Automation USA - Technical Competency Assessment**

---

## Overview
This checklist is designed to verify basic computer competencies required for technical support roles at Broetje Automation. Each item should be completed in a controlled environment with a trainer present to verify completion.

**Trainee:** _________________________________ **Date:** _______________  
**Trainer:** _________________________________ **Completion Time:** _______________

---

## 1. Network File Sharing & Mapping
**Objective:** Demonstrate ability to share folders and map network drives according to site standards

**Tasks:**
- [ ] Share C: or D: drive folder on local PC
- [ ] Map the shared folder as a network drive on remote PC
- [ ] Create folder structure: `D:\Temp\[User Initials]` on both PCs
- [ ] Transfer a test file between PCs using mapped drive
- [ ] Verify file transfer successful

**Verification Signature:** ______________________ **Pass/Fail:** ________

---

## 2. Hard Drive Management
**Objective:** Demonstrate proper hard drive management and assignment

**Tasks:**
- [ ] Assign drive letter to USB device using Disk Management
- [ ] Change drive letter of existing hard drive
- [ ] View and document current drive assignments
- [ ] Remove and reassign USB device drive letter
- [ ] Verify all changes in File Explorer

**Verification Signature:** ______________________ **Pass/Fail:** ________

---

## 3. Basic Command Line Interface (CLI)
**Objective:** Execute basic network diagnostic commands

**Tasks:**
- [ ] Open Command Prompt (CMD)
- [ ] Execute `ping 192.168.213.1` (Riveter network)
- [ ] Execute `ping 192.168.214.1` (NC network)
- [ ] Execute `ping 192.168.1.1` (Video recording network)
- [ ] Execute `tracert google.com`
- [ ] Document results for all commands

**Verification Signature:** ______________________ **Pass/Fail:** ________

---

## 4. IP Address Configuration
**Objective:** Change IP addresses for different machine networks

**Tasks:**
- [ ] Access Network and Sharing Center
- [ ] Change adapter settings
- [ ] Configure static IP for 192.168.213.x subnet (Riveter)
- [ ] Test connectivity with `ping`
- [ ] Change IP to 192.168.214.x subnet (NC)
- [ ] Test connectivity with `ping`
- [ ] Change IP to 192.168.1.x subnet (Video recording)
- [ ] Test connectivity with `ping`
- [ ] Document all IP configurations used

**Verification Signature:** ______________________ **Pass/Fail:** ________

---

## 5. Backup/Restore Operations
**Objective:** Perform system backup and restore using Paragon software

**Tasks:**
- [ ] Open Paragon Backup & Recovery software
- [ ] Create system backup of Siemens IPC
- [ ] Name backup following Broetje naming standards
  - Format: `[Customer]_[Machine#]_[Date]_[Type]_backup`
- [ ] Verify backup file location and size
- [ ] Prepare blank hard drive for restoration
- [ ] Restore backup image to blank drive
- [ ] Verify successful boot from restored drive

**Verification Signature:** ______________________ **Pass/Fail:** ________

---

## 6. Hard Drive Replacement
**Objective:** Replace HDD with SSD and ensure proper boot

**Tasks:**
- [ ] Power down Siemens IPC safely
- [ ] Remove existing hard drive
- [ ] Install new SSD drive
- [ ] Boot system and verify BIOS recognition
- [ ] Configure boot priority if needed
- [ ] Verify system boots successfully
- [ ] Document drive specifications and installation date

**Verification Signature:** ______________________ **Pass/Fail:** ________

---

## 7. Remote Access Configuration
**Objective:** Set up and use remote viewing tools

**Tasks:**
- [ ] Install and configure VNC server on machine
- [ ] Connect to machine using VNC client from external PC
- [ ] Configure Teams for screen sharing
- [ ] Successfully share screen via Teams
- [ ] Demonstrate remote control capabilities
- [ ] Document connection settings used

**Verification Signature:** ______________________ **Pass/Fail:** ________

---

## 8. Batch File Scripting
**Objective:** Create basic batch file for automation

**Tasks:**
- [ ] Create folder `D:\Temp\[User Initials]`
- [ ] Create text file "Hello World.txt" in this folder
- [ ] Create .bat file that opens this text file
- [ ] Configure .bat file to run at startup
- [ ] Test batch file execution
- [ ] Verify auto-start functionality after reboot
- [ ] Document batch file content

**Batch File Content:**
```
____________________________________
____________________________________
____________________________________
____________________________________
```

**Verification Signature:** ______________________ **Pass/Fail:** ________

---

## 9. OneDrive Integration
**Objective:** Set up OneDrive for file sharing

**Tasks:**
- [ ] Install/configure OneDrive application
- [ ] Sign in with Broetje account credentials
- [ ] Create shared folder for large file transfers
- [ ] Upload test file (>100MB recommended)
- [ ] Generate sharing link
- [ ] Test download from shared link on different device
- [ ] Document sharing permissions used

**Verification Signature:** ______________________ **Pass/Fail:** ________

---

## Final Assessment

**Overall Performance:** _____ / 9 tasks completed successfully

**Trainer Comments:**
```
_________________________________________________________
_________________________________________________________
_________________________________________________________
_________________________________________________________
```

**Recommend for:**
- [ ] Advanced Technical Training
- [ ] Field Service Assignment
- [ ] Additional Practice Required
- [ ] Specialized Training Needed

**Trainer Signature:** _________________________ **Date:** _______________

**Trainee Signature:** _________________________ **Date:** _______________

---

## Notes and Observations
```
_________________________________________________________
_________________________________________________________
_________________________________________________________
_________________________________________________________
_________________________________________________________
```

---

*This checklist should be completed in a controlled laboratory environment before field deployment. All tasks must be performed under trainer supervision to ensure proper technique and safety protocols are followed.*