# Hard Drive Replacement Guide
**Siemens IPC Hard Drive to SSD Upgrade**

---

## Overview
This guide covers the physical replacement of traditional hard drives with SSDs in Siemens IPCs, including proper handling, installation, and post-installation verification procedures.

---

## Part 1: Pre-Replacement Preparation

### Required Tools
- Torx driver set (T8, T10, T15, T20)
- Clean microfiber cloth
- Cable ties or velcro straps
- Digital camera for documentation

### Safety Requirements
- Power off system and disconnect power
- Work in static-free environment
- Avoid touching circuit boards
- Wear safety glasses when opening enclosures

### Drive Selection
**SSD Requirements:**
- Capacity: Minimum 250GB required
- Interface: SATA III (6 Gb/s)
- Form factor: 2.5" (standard for IPC)
- Brand: Enterprise-grade (Samsung, Crucial, Intel)
- Warranty: Minimum 5 years

---

## Part 2: Data Backup and Documentation

### Pre-Replacement Documentation
```
Serial Numbers:
- Computer: ________________
- Old Drive: ________________
- New Drive: ________________

Current Configuration:
- OS Version: ________________
- Installed Software: _________
- Total Data Size: ___________
- Network Settings: __________
```

### Critical Backup Steps
1. Create full system backup using Paragon
2. Document all network settings
3. Note installed software and licenses
4. Save device drivers to USB
5. Record BIOS/UEFI settings
6. Document active network connections

---

## Part 3: Physical Replacement Process

### Step 1: Power Down Safely
1. Save all open files
2. Close all applications
3. Shut down Windows properly
4. Disconnect AC power
5. Press power button for 10 seconds (discharge)
6. Wait 30 seconds before proceeding

### Step 2: Access Drive Bay
**For Rack-Mount IPC:**
1. Remove retention screws
2. Slide unit out of rack
3. Remove top/side panel
4. Locate drive bay

**For Desktop IPC:**
1. Remove side panel screws
2. Slide panel off
3. Locate 2.5" drive mount

### Step 3: Remove Old Drive
1. Disconnect SATA data cable
2. Disconnect SATA power cable
3. Remove drive mounting screws using appropriate Torx driver
4. Carefully slide drive out
5. Place in protective bag

### Step 4: Install New SSD
1. Remove SSD from anti-static packaging
2. Mount SSD in drive bay
3. Secure with original Torx screws
4. Connect SATA data cable (red stripe = pin 1)
5. Connect SATA power cable
6. Verify secure connections

### Step 5: Cable Management
1. Route cables away from fans
2. Secure with cable ties
3. Ensure no cable pinching
4. Verify thermal clearance
5. Check for interference with moving parts

---

## Part 4: Post-Installation Boot Process

### Step 1: Initial Boot
1. Reconnect power
2. Press power button
3. System will boot with new drive
4. Verify POST completion
5. Note any error messages

### Step 2: Immediate Restoration
1. Boot from Paragon recovery media
2. Select restore option
3. Choose appropriate backup file
4. Select new SSD as target
5. Execute restoration
6. Verify successful boot

### Step 3: Verification Process
- Check drive is detected correctly
- Verify system boots normally
- Test all machine connections
- Confirm all software functions
- Document replacement details

## Part 5: Post-Installation Tasks

### Verification Steps
1. Boot into Windows successfully
2. Verify all devices are recognized
3. Test network connectivity to Broetje networks
4. Check machine control software functionality
5. Document completion of replacement

---

## Part 7: Practice Exercise

### Exercise 1: Safe Drive Removal
1. Power down test system
2. Document current configuration
3. Open case properly
4. Identify and remove drive
5. Document all connections
6. Practice cable management

### Exercise 2: SSD Installation
1. Install new SSD in test system
2. Connect all cables correctly
3. Boot and verify in BIOS
4. Configure BIOS settings
5. Boot to Windows
6. Verify functionality

### Exercise 3: Performance Testing
1. Install benchmarking software
2. Run baseline tests
3. Apply optimizations
4. Re-run performance tests
5. Document improvements
6. Create performance report

**Time to complete**: 45-60 minutes

---

## Part 8: Troubleshooting Guide

### Drive Not Detected
1. Verify power connection
2. Check SATA cable orientation
3. Test different SATA port
4. Update BIOS firmware
5. Try different SATA cable

### Boot Issues
1. Check boot order in BIOS
2. Verify AHCI mode enabled
3. Rebuild BCD (Windows):
   ```
   bootrec /fixmbr
   bootrec /fixboot
   bootrec /rebuildbcd
   ```
4. Check for secure boot conflicts

### Performance Problems
1. Enable AHCI (not IDE mode)
2. Verify SATA port speed
3. Align SSD partitions
4. Update SSD firmware
5. Check for background processes

### Common Error Messages
- "Boot device not found": Check BIOS
- "Disk read error": Verify connections
- "Operating system not found": Restore backup
- "SMART failure predicted": Replace drive

---

## Part 9: Documentation Template

### Drive Replacement Log
```
Date: ________________  Technician: ________________

System Information:
- Computer Model: _____________________
- Serial Number: ______________________
- Location: ___________________________

Old Drive:
- Model: _____________________________
- Serial: _____________________________
- Capacity: ___________________________
- Age: _______________________________

New Drive:
- Model: _____________________________
- Serial: _____________________________
- Capacity: ___________________________
- Purchase Date: ______________________

Installation Details:
- Backup Status: Pass/Fail
- Physical Install: Pass/Fail
- BIOS Detection: Pass/Fail
- Boot Status: Pass/Fail
- Performance Test: Pass/Fail

Notes:
_________________________________________
_________________________________________
_________________________________________
```

---

## Part 10: Best Practices

### Handling Procedures
1. Always ground yourself
2. Handle drives by edges only
3. Avoid exposing to magnetic fields
4. Store in anti-static bags
5. Never force connections

### Quality Assurance
1. Verify all specifications before purchase
2. Test drives before installation
3. Keep original packaging/documentation
4. Maintain drive warranty information
5. Document all replacements

### Preventive Maintenance
1. Monitor SMART attributes monthly
2. Check drive health quarterly
3. Maintain firmware updates
4. Track performance benchmarks
5. Schedule replacement before failure

---

## Quick Reference

### Common BIOS Keys
- Siemens IPC: F2 or DEL
- Boot menu: F12 or F10
- UEFI setup: F2

### Critical BIOS Settings
- SATA Mode: AHCI
- Secure Boot: Disabled (for older systems)
- Fast Boot: Enabled
- Wake on LAN: As needed

### Windows SSD Commands
```
Enable TRIM: fsutil behavior set DisableDeleteNotify 0
Check TRIM: fsutil behavior query DisableDeleteNotify
Align disk: msra.exe
```

---

## Checklist
- [ ] Created complete system backup
- [ ] Powered down safely
- [ ] Properly grounded during installation
- [ ] Installed SSD with correct orientation
- [ ] Verified BIOS detection
- [ ] Successfully booted system
- [ ] Applied SSD optimizations
- [ ] Completed performance testing
- [ ] Documented entire process

**Trainer Initials**: _______ **Trainee Initials**: _______

---

## Emergency Recovery

### If New Drive Fails to Boot
1. Verify all connections
2. Check BIOS settings
3. Boot from recovery media
4. Attempt repair installation
5. Restore from backup

### Data Recovery from Old Drive
1. Connect old drive via USB
2. Use data recovery software
3. Extract critical files
4. Verify data integrity
5. Securely wipe old drive