# Backup/Restore Operations Guide
**Paragon Software for Siemens IPC Systems**

---

## Overview
This guide covers critical backup and restore procedures for Siemens IPCs using Paragon Backup & Recovery. These procedures are essential for protecting machine configurations and enabling rapid recovery.

---

## Part 1: Understanding Backup Types

### Full System Backup
- Complete disk image
- All partitions, files, and settings
- Used for bare-metal restoration
- Typical size: 20-50GB per backup

### Incremental Backup
- Only changed files since last backup
- Faster and smaller
- Requires baseline full backup

### Differential Backup
- All changes since last full backup
- Moderate size and speed
- Independent of incremental backups

---

## Part 2: Broetje Naming Standards

### File Naming Convention
```
[Machine#]_[Machine Initials]_[Type]_[Date YYYYMMDD]
```

**Examples:**
- `AP1741_R1_NC_20250819` - NC system backup
- `AP1741_R1_DD_20250819` - Drive data backup
- `AP1741_R1_PLC_20250819` - PLC configuration
- `Boeing_S1_S7_20250819` - Riveter PLC backup
- `Gulfstream_M1_HMI_20250819` - HMI backup

### Storage Locations
- Network share: `\\Server\Backups\[Customer]\[Machine#]`
- Local temporary: `D:\Temp\[UserInitials]\Backups`
- External drive: `E:\Broetje_Backups\[Year]\[Customer]`

---

## Part 3: Creating System Backup

### Step 1: Launch Paragon Backup & Recovery
1. Double-click Paragon desktop icon
2. Or: Start → All Programs → Paragon → Backup & Recovery
3. Select "Create New Backup"

### Step 2: Select Backup Type
1. Choose "Disk and Partitions Backup"
2. Select source disk (usually C: and D:)
3. Include all partitions:
   - System partition (C:)
   - Data partition (D:)
   - Recovery partition (if present)

### Step 3: Choose Destination
1. Click "Browse" for destination
2. Navigate to backup storage location
3. Create filename following naming convention
4. Select compression level:
   - None: Fastest, largest file
   - Normal: Balanced speed/size
   - Maximum: Slowest, smallest file

### Step 4: Configure Options
**Advanced Options:**
- Enable "Verify backup after creation"
- Set "Split backup size" if needed (for DVD/USB)
- Configure "Password protection" if required
- Enable "Email notification" if available

**Backup Comments:**
```
Machine ID: [Machine Serial]
Customer: [Customer Name]
Configuration: [Software Version]
Created by: [Your Name]
Date: [Current Date]
Purpose: [Reason for backup]
```

### Step 5: Execute Backup
1. Review summary screen
2. Click "Create Backup"
3. Monitor progress
4. Verify completion message
5. Document backup details

---

## Part 4: Preparing for Restoration

### Hardware Requirements
- Target drive size ≥ original drive
- Compatible hard drive interface
- Sufficient RAM (min 1GB)
- Bootable USB/DVD with Paragon

### Creating Recovery Media
1. Open Paragon Recovery Media Builder
2. Select "USB Device" or "DVD"
3. Add backup files if desired
4. Add network drivers
5. Create media

### Pre-Restoration Checklist
- [ ] Backup target drive (if has data)
- [ ] Note current hardware configuration
- [ ] Gather network settings
- [ ] Prepare bootable media
- [ ] Verify backup file integrity

---

## Part 5: Restoration Process

### Step 1: Boot into Recovery Environment
1. Insert Paragon recovery media
2. Restart computer
3. Access BIOS/UEFI (usually F2, F10, or DEL)
4. Set boot priority to USB/DVD
5. Save and exit BIOS

### Step 2: Launch Paragon Restore
1. Boot from recovery media
2. Wait for Paragon to load
3. Select "Restore Backup"
4. Choose backup file location

### Step 3: Select Backup File
1. Browse to backup location
2. Select appropriate .pfi or .pvhd file
3. Verify backup date and comments
4. Click "Next"

### Step 4: Choose Target Drive
1. Select destination drive
2. **WARNING**: All data will be deleted
3. Confirm drive selection
4. Set partition alignment options

### Step 5: Execute Restoration
1. Review restoration summary
2. Start restoration process
3. Monitor progress (typically 30-60 min)
4. Do not interrupt process
5. Wait for completion message

### Step 6: Post-Restoration Tasks
1. Remove recovery media
2. Restart system
3. Verify successful boot
4. Check Windows activation
5. Update device drivers
6. Test machine functionality

---

## Part 6: Practice Exercises

### Exercise 1: Create System Backup
1. Launch Paragon on test system
2. Create full disk backup
3. Use proper naming convention
4. Save to network location
5. Verify backup completion
6. Document backup details

### Exercise 2: Restore to Test Drive
1. Prepare secondary drive
2. Boot into recovery environment
3. Restore backup to test drive
4. Verify boot functionality
5. Document restoration process

### Exercise 3: Incremental Backup
1. Make system changes
2. Create incremental backup
3. Compare file sizes
4. Restore incremental backup
5. Verify only changes applied

**Time to complete**: 2-3 hours

---

## Part 7: Troubleshooting Guide

### Common Backup Errors

**Insufficient Space**
- Check destination capacity
- Use higher compression
- Split backup into multiple files

**Access Denied**
- Run as Administrator
- Check network permissions
- Verify user credentials

**Corrupt Backup File**
- Re-create from source
- Check storage device health
- Verify network connectivity

### Common Restore Errors

**Boot Failure After Restore**
- Check BIOS settings
- Verify secure boot status
- Rebuild boot configuration:
  ```
  bootrec /fixmbr
  bootrec /fixboot
  bootrec /rebuildbcd
  ```

**Missing Drivers**
- Add drivers to recovery media
- Install manually post-restore
- Use driver backup tools

**Activation Issues**
- Note product keys before backup
- Use phone activation method
- Document licensing details

---

## Part 8: Documentation Template

### Backup Log
```
Customer: ________________  Machine: ________________
Backup Type: _____________  Date: ____________________

Source Information:
- Drive Model: ____________  Serial: _________________
- Total Size: _____________  OS Version: _____________
- Software Versions: _____________________________

Backup Details:
- Filename: ________________________________________
- Location: ________________________________________
- Compression: _____________________________________
- Duration: ________________________________________
- Verification: Pass/Fail

Restoration Test:
- Test Date: _______________________________________
- Test Drive: ______________________________________
- Boot Status: Pass/Fail
- Functionality: Pass/Fail

Technician: ________________  Verified by: ____________
```

---

## Part 9: Best Practices

### Backup Strategy
1. **Full System Backups**:
   - Twice yearly during planned shutdowns
   - Complete machine image
   - All backup types created

2. **Routine Maintenance**:
   - PLC backups: Monthly
   - HMI configurations: After changes
   - Safety systems: Quarterly

3. **Verification**:
   - Test restore annually
   - Verify backup integrity after creation
   - Document all procedures

### Storage Management
- Use redundant storage
- Implement 3-2-1 backup rule
- Monitor storage capacity
- Regular cleanup of old backups

---

## Quick Reference

### Backup Command Line
```
para_cmdline /p:"C:\" /o:"\\server\backups\machine1.pfi" /c:Normal
```

### Restore Command Line
```
para_cmdline /r:"\\server\backups\machine1.pfi" /p:"C:\"
```

### Key File Extensions
- .pfi: Paragon backup file
- .pvhd: Virtual hard disk backup
- .psl: Paragon script file

---

## Checklist
- [ ] Created full system backup
- [ ] Applied correct naming convention
- [ ] Stored backup in proper location
- [ ] Created recovery media
- [ ] Successfully restored to test drive
- [ ] Verified restored system functionality
- [ ] Documented all procedures

**Trainer Initials**: _______ **Trainee Initials**: _______

---

## Emergency Procedures

### Critical System Failure
1. Boot from recovery media
2. Access latest backup
3. Verify backup integrity
4. Restore to replacement drive
5. Test functionality
6. Update documentation

### Network Backup Access
```
net use Z: \\server\backups /persistent:yes
```

### Verify Backup Integrity
1. Open backup file in Paragon
2. Select "Verify Backup"
3. Check for corruption
4. Document results