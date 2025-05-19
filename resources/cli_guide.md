# Command Line Interface (CLI) Guide
**Windows 10 Basic Network Commands**

---

## Overview
This guide teaches essential network diagnostic commands used daily in troubleshooting Broetje Automation equipment. These commands help verify connectivity to our three machine networks.

---

## Part 1: Opening Command Prompt

### Method 1 (Recommended):
1. Press **Windows key + R**
2. Type `cmd`
3. Press **Enter**

### Method 2:
1. Click Start menu
2. Type `cmd` in search box
3. Click "Command Prompt"

### Method 3 (Administrator):
1. Right-click Start button
2. Select "Command Prompt (Admin)"
3. Click "Yes" when prompted

### Understanding the Prompt
- Shows current directory (e.g., `C:\Users\YourName>`)
- `>` indicates it's ready for commands
- Case insensitive (PING = ping = Ping)

---

## Part 2: PING Command

### What PING Does
- Tests connectivity to another device
- Sends packets and measures response time
- Shows if device is "alive" on network
- Essential for troubleshooting

### Basic PING Syntax
```
ping [IP address or hostname]
```

### Testing Broetje Networks

**Machine Network (192.168.214.x)**
```
ping 192.168.214.1          # NCU Controller
ping 192.168.214.34         # Service PC
ping 192.168.214.35         # Operator PC
ping 192.168.214.37         # Scale PC (Vision System)
ping 192.168.214.38         # Ketop (industrial tablet)
ping 192.168.214.60         # Riveter PC (Siemens soft PLC)
ping 192.168.214.249        # NCU (alternative)
```

**Riveter Network (192.168.213.x)**
```
ping 192.168.213.33         # RTX System
ping 192.168.213.60         # Riveter PLC backup path
```

**Video Recording Network (192.168.1.x)**
```
ping 192.168.1.1            # Video system gateway
```

### Reading PING Results

**Successful Response:**
```
Reply from 192.168.213.1: bytes=32 time=1ms TTL=64
Reply from 192.168.213.1: bytes=32 time=1ms TTL=64
```

**Failed Response:**
```
Request timed out.
```
or
```
Destination host unreachable.
```

---

## Part 3: Additional Network Commands

### TRACERT (Trace Route)
- Shows path to destination
- Identifies where connection fails
- Useful for network troubleshooting

**Syntax:**
```
tracert google.com
```

**Example:**
```
tracert 192.168.213.10
```

### IPCONFIG
- Shows current IP configuration
- Useful for verifying settings

**Basic command:**
```
ipconfig
```

**Detailed info:**
```
ipconfig /all
```

### ARP
- Shows connected devices
- Lists IP to MAC address mappings

**Basic command:**
```
arp -a
```

---

## Part 4: Practice Exercises

### Exercise 1: Network Discovery
1. Open Command Prompt
2. Test all Broetje machine network components:
   ```
   ping 192.168.214.34    # Service PC
   ping 192.168.214.35    # Operator PC  
   ping 192.168.214.37    # Vision System
   ping 192.168.214.60    # Riveter PC
   ```
3. Document response times for each

### Exercise 2: Advanced Network Analysis
1. Check all connected devices:
   ```
   arp -a
   nbtstat -n
   netstat -an | find "192.168.214"
   ```
2. Identify which machines are active
3. Document device names and MAC addresses

### Exercise 3: Troubleshooting Scenario
1. Simulate network issue:
   - Set static IP that conflicts
2. Use diagnostic commands:
   ```
   pathping 192.168.214.1
   netstat -rn
   arp -d (clear ARP cache)
   ```
3. Identify and resolve issue
4. Verify resolution with ping tests

**Time to complete**: 10-15 minutes

---

## Part 5: Documenting Results

### Create a Network Log
Document each test:
- Command used
- Target IP/hostname
- Response status (Success/Fail)
- Average response time
- Date and time

**Example Format:**
```
Test Date: [Date]
Command: ping 192.168.213.1
Status: Success
Avg Response: 1ms
Notes: Connection stable
```

---

## Troubleshooting Tips

### If PING fails:
- Check IP address for typos
- Verify network cable connection
- Confirm correct network adapter is active
- Check firewall settings

### Slow response times:
- Network congestion
- Hardware issues
- Distance to target

### Common Errors:
- "ping is not recognized": Check spelling
- "Request timed out": Device offline or firewall blocking
- "Destination unreachable": Network path issue

---

## Quick Reference Card

### Essential Commands:
```
ping [IP]          - Test connectivity
ping -t [IP]       - Continuous ping
ping -n 10 [IP]    - Ping 10 times
tracert [IP]       - Trace route to destination
ipconfig           - Show IP settings
ipconfig /all      - Detailed IP info
arp -a             - Show MAC addresses
```

### Broetje Networks:
- Machine: 192.168.214.x (Primary network)
  - .1 = NCU Controller
  - .34 = Service PC
  - .35 = Operator PC  
  - .37 = Scale PC (Vision)
  - .38/.39 = Ketop tablets
  - .60 = Riveter PC
  - .249 = NCU (alt)
- Riveter: 192.168.213.x
  - .33 = RTX System
- Video: 192.168.1.x

### Stop Commands:
- Press **Ctrl+C** to stop any running command

---

## Checklist
- [ ] Opened Command Prompt
- [ ] Successfully pinged all three networks
- [ ] Ran tracert command
- [ ] Viewed IP configuration
- [ ] Documented all results
- [ ] Troubleshooted at least one failed connection

**Trainer Initials**: _______ **Trainee Initials**: _______

---

## Command Practice Log
| Command | Target | Result | Time | Notes |
|---------|--------|--------|------|-------|
| | | | | |
| | | | | |
| | | | | |
| | | | | |

---

## Advanced Tips
- Use `ping -n 100` for extended testing
- Save output: `ping google.com > ping_results.txt`
- Use `pathping` for combined ping and tracert