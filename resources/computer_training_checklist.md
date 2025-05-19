# Basic Computer Requirements Training Checklist
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