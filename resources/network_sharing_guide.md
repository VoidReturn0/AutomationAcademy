# Network File Sharing & Mapping Guide
**Windows 10 Step-by-Step Instructions**

---

## Overview
This guide will teach you how to share folders and map network drives, which is essential for transferring files between machines at Broetje Automation sites.

---

## Part 1: Sharing a Folder

### Step 1: Locate the Folder to Share
1. Open **File Explorer** (Windows key + E)
2. Navigate to the drive you want to share (usually C: or D:)
3. Right-click on the folder you want to share

### Step 2: Enable Sharing
1. Select **Properties** from the context menu
2. Click the **Sharing** tab
3. Click **Advanced Sharing**
4. Check the box **Share this folder**
5. Keep the default Share name or change it (remember this name)
6. Click **Permissions**
7. Select **Everyone** and ensure **Full Control** is checked
8. Click **OK** on all windows

### Step 3: Get the Network Path
1. Back in the Sharing tab, note the **Network Path** (e.g., `\\COMPUTER-NAME\SharedFolder`)
2. Write this down - you'll need it for mapping

---

## Part 2: Creating Site Standard Temp Folder

### Step 1: Create Your Temp Directory
1. Open File Explorer
2. Navigate to D: drive
3. Create a new folder called **Temp**
4. Inside Temp, create a folder with **your initials** (e.g., D:\Temp\MG)
5. This is your personal workspace for temporary files

---

## Part 3: Mapping a Network Drive

### Step 1: Access Map Network Drive
1. Open File Explorer
2. Click **This PC** in the left sidebar
3. Click the **Map network drive** button in the ribbon

### Step 2: Configure the Mapping
1. Choose an available drive letter (e.g., Z:)
2. In the Folder field, enter the network path from Part 1
   - Format: `\\COMPUTER-NAME\SharedFolder`
3. Check **Reconnect at sign-in** (optional but recommended)
4. Check **Connect using different credentials** if needed
5. Click **Finish**

### Step 3: Enter Credentials (if prompted)
1. Enter username: use the computer's username
2. Enter password: use the computer's password
3. Click **OK**

---

## Part 4: Testing File Transfer

### Step 1: Create a Test File
1. Navigate to your mapped drive (e.g., Z:)
2. Create a new text document
3. Name it "Test_Transfer_[YourInitials].txt"
4. Open it and type a simple message
5. Save and close the file

### Step 2: Verify Transfer
1. Go to the original computer
2. Navigate to the shared folder
3. Confirm the test file appears
4. Open it to verify the content
5. Try editing it and saving

---

## Troubleshooting Tips

### If sharing doesn't work:
- Ensure both computers are on the same network
- Check Windows Firewall settings
- Enable Network Discovery in Network and Sharing Center

### If mapping fails:
- Verify the network path is correct
- Try using the IP address instead: `\\192.168.X.X\ShareName`
- Ensure the shared folder permissions include your user

### Common Errors:
- **"Network path not found"**: Check spelling and network connectivity
- **"Access denied"**: Verify permissions on the shared folder
- **"Windows cannot access..."**: Ensure both computers have file sharing enabled

---

## Practice Exercise

1. Share a folder named "Practice" on your D: drive
2. Create your temp directory (D:\Temp\[YourInitials])
3. Map the shared folder from another computer
4. Transfer a file both ways
5. Verify the transfer was successful

**Time to complete**: 10-15 minutes

---

## Quick Reference

### To share a folder:
Right-click → Properties → Sharing tab → Advanced Sharing → Share this folder

### To map a drive:
File Explorer → This PC → Map network drive → Enter path → Finish

### Network path format:
`\\COMPUTER-NAME\SharedFolder` or `\\IP-ADDRESS\SharedFolder`

---

## Checklist
- [ ] Successfully shared a folder
- [ ] Created personal temp directory
- [ ] Mapped network drive
- [ ] Transferred file successfully
- [ ] Verified file on both computers

**Trainer Initials**: _______ **Trainee Initials**: _______