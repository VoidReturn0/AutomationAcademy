# IP Address Configuration Guide
**Windows 10 Network Settings for Broetje Equipment**

---

## Overview
This guide teaches how to configure IP addresses for connecting to different Broetje machine networks. Understanding these three networks is crucial for equipment support.

---

## Part 1: Understanding Broetje Networks

### Our Machine Network Schema:
1. **Machine Network**: 192.168.214.x
   - Gateway: 192.168.214.1 (NCU)
   - Service PC: 192.168.214.34
   - Operator PC: 192.168.214.35
   - Scale PC (Vision): 192.168.214.37
   - Ketop tablets: 192.168.214.38/39
   - Riveter PC: 192.168.214.60
   - NCU (alternate): 192.168.214.249
   - Subnet mask: 255.255.255.0

2. **Riveter Network**: 192.168.213.x
   - Gateway: 192.168.213.1
   - RTX System: 192.168.213.33
   - Subnet mask: 255.255.255.0

3. **Video Recording Network**: 192.168.1.x
   - Gateway: 192.168.1.1
   - Typical range: 192.168.1.1 - 192.168.1.254
   - Subnet mask: 255.255.255.0

---

## Part 2: Accessing Network Settings

### Method 1 (Settings App):
1. Right-click network icon in system tray
2. Select "Open Network & Internet settings"
3. Click "Change adapter options"

### Method 2 (Control Panel):
1. Press Windows key + R
2. Type `ncpa.cpl`
3. Press Enter

### Method 3 (Classic):
1. Go to Control Panel
2. Network and Sharing Center
3. Change adapter settings

---

## Part 3: Changing IP Address - Step by Step

### Step 1: Select Network Adapter
1. Double-click your active network adapter
   - Usually "Ethernet" or "Wi-Fi"
2. Click "Properties"

### Step 2: Access TCP/IPv4 Settings
1. Find "Internet Protocol Version 4 (TCP/IPv4)"
2. Click to select it
3. Click "Properties"

### Step 3: Configure Static IP
1. Select "Use the following IP address"
2. Enter settings based on network:

**For Machine Network:**
- IP address: 192.168.214.[choose 50-200]
- Subnet mask: 255.255.255.0
- Default gateway: 192.168.214.1 (NCU)

**For Riveter Network:**
- IP address: 192.168.213.[choose 50-250]
- Subnet mask: 255.255.255.0
- Default gateway: 192.168.213.1

**For Video Network:**
- IP address: 192.168.1.[choose 10-254]
- Subnet mask: 255.255.255.0
- Default gateway: 192.168.1.1

### Step 4: DNS Settings
1. Select "Use the following DNS server addresses"
2. Preferred DNS: Use same as gateway
3. Alternate DNS: 8.8.8.8 (Google DNS)

### Step 5: Apply Settings
1. Click "OK" on all windows
2. Close Network Connections window

---

## Part 4: Testing Your Configuration

### Immediate Testing
1. Open Command Prompt
2. Test gateway connectivity:
   ```
   ping 192.168.213.1
   ```
3. Verify DNS resolution:
   ```
   ping google.com
   ```

### Advanced Testing
```
ipconfig /all
```
- Verifies current settings
- Shows DNS servers
- Displays adapter status

---

## Part 5: Practice Sequence

### Exercise 1: Change to Machine Network
1. Set IP to 192.168.214.100
2. Test with: `ping 192.168.214.1`
3. Verify connectivity to:
   - Service PC: `ping 192.168.214.34`
   - Operator PC: `ping 192.168.214.35`
   - Riveter PC: `ping 192.168.214.60`
4. Document settings

### Exercise 2: Switch to Riveter Network
1. Change IP to 192.168.213.100
2. Test with: `ping 192.168.213.1`
3. Verify RTX connectivity: `ping 192.168.213.33`
4. Document configuration

### Exercise 3: Configure Video Network
1. Set IP to 192.168.1.100
2. Test with: `ping 192.168.1.1`
3. Check if internet access still works
4. Return to DHCP when complete

**Time to complete**: 20-30 minutes

---

## Part 6: Documentation Template

### Network Configuration Log
```
Date: ___________  Technician: ___________

Machine Type: ____________  Location: ____________

Network 1 (Riveter):
- IP: 192.168.213._____
- Gateway: 192.168.213.1
- Test Result: Pass/Fail
- Notes: ________________

Network 2 (NC):
- IP: 192.168.214._____
- Gateway: 192.168.214.1
- Test Result: Pass/Fail
- Notes: ________________

Network 3 (Video):
- IP: 192.168.1._____
- Gateway: 192.168.1.1
- Test Result: Pass/Fail
- Notes: ________________
```

---

## Troubleshooting Guide

### Common Issues:

**1. No Internet After IP Change**
- Verify default gateway is correct
- Check subnet mask is 255.255.255.0
- Ensure DNS servers are configured

**2. Cannot Reach Equipment**
- Confirm IP is in correct range
- Check for IP conflicts
- Verify cable connections

**3. Settings Won't Save**
- Run as Administrator
- Disable antivirus temporarily
- Check for group policy restrictions

**4. Slow Connection**
- Try different IP in range
- Check for network congestion
- Verify network adapter drivers

---

## Quick Reference

### IP Range Selection:
- Avoid: .1 (gateway), .33 (RTX), .34-39 (assigned), .60 (Riveter), .249 (NCU), .255 (broadcast)
- Safe range: .50 to .200 for temporary assignments
- Document used IPs to prevent conflicts

### Common Default Gateways:
- Machine: 192.168.214.1 (NCU)
- Riveter: 192.168.213.1
- Video: 192.168.1.1

### Network Path:
Settings → Network & Internet → Change adapter options → Right-click adapter → Properties → IPv4 → Properties

---

## Safety Reminders

1. **Always test** after changing IP
2. **Document** your configurations
3. **Never** use .1 or .255 in last octet
4. **Return to DHCP** when finished
5. **Check with team** for IP availability

---

## Checklist
- [ ] Successfully configured Riveter network
- [ ] Successfully configured NC network
- [ ] Successfully configured Video network
- [ ] Tested each configuration with ping
- [ ] Documented all settings
- [ ] Returned to DHCP/original settings

**Trainer Initials**: _______ **Trainee Initials**: _______

---

## Advanced Tips
- Use `ipconfig /release` and `ipconfig /renew` for DHCP
- Save configurations: `netsh dump > network_config.txt`
- Create shortcuts for common IPs using batch files