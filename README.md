---
> **Security & Sanitization Notice:** This repository contains sanitized, lab-safe code and documentation. It does not include proprietary, classified, sensitive, or employer-owned data. Hostnames, domains, usernames, IP addresses, and operational details are fictionalized or generalized. See [SECURITY_NOTICE.md](SECURITY_NOTICE.md) for full details.
---

# Wake-on-LAN

## Overview
A lightweight Windows desktop application for sending Wake-on-LAN magic packets to network devices. Devices are saved by name with their MAC address and broadcast IP, and can be woken with a double-click. Built with Python and Tkinter using only the standard library — no third-party packages required.

## Problem It Solves
Waking a remote machine requires either memorizing MAC addresses and typing a raw UDP packet command, or installing a full-featured network management suite just to press a power button. This tool provides a simple, portable, always-available GUI that an IT technician can keep on their desktop or USB drive — named entries mean you never need to look up a MAC address again, and a double-click is faster than any command-line alternative.

## Key Features
- Add, edit, and remove named devices with MAC addresses and broadcast IPs
- Configurable broadcast IP per device (supports subnet-directed broadcast for multi-segment networks)
- Sends a standard 102-byte magic packet over UDP port 9
- Device list persisted to `devices.json` next to the executable — survives restarts
- Double-click a device row to wake it instantly
- Alternating row colors for easy scanning of large device lists
- Builds to a single portable `.exe` — copy it to any Windows machine and run it

## Technologies Used
- Python 3.10+
- Tkinter (built-in Python GUI framework)
- `socket` module (UDP packet transmission)
- `json` module (device persistence)
- PyInstaller (portable executable build)

## Example Use Case
A systems administrator supports a lab with 15 workstations that are powered off overnight to save energy. In the morning, rather than walking the room or maintaining a spreadsheet of MAC addresses with WoL command syntax, they open this tool, select all the machines in the list, and double-click each one — all workstations are powered on before they finish their coffee, with no command-line work required.

## How to Run

**Run from source** (Python 3.10+ required):

```bash
python wol.py
```

**Build a standalone executable** (no Python required on target machine):

```batch
build.bat
```

Output: `dist\WakeOnLAN.exe` — copy it anywhere and run it directly.

## Example Output

On successful wake:
```
Magic packet sent to AA:BB:CC:DD:EE:FF via 192.168.1.255:9
```

The target machine powers on within a few seconds if Wake-on-LAN is enabled in its BIOS/UEFI and network adapter settings.

**`devices.json` format** (auto-created at first save):

```json
[
  {"name": "Dev Workstation", "mac": "AA:BB:CC:DD:EE:FF", "broadcast": "192.168.1.255"},
  {"name": "Lab Server",      "mac": "11:22:33:44:55:66", "broadcast": "192.168.10.255"}
]
```

## Security Notes
- Wake-on-LAN sends an unauthenticated broadcast UDP packet — anyone on the network segment (or with access to the broadcast IP) can wake the machine if they know its MAC address
- This tool should only be used on trusted internal networks; do not expose the broadcast IP to untrusted network segments
- MAC addresses stored in `devices.json` are not encrypted — treat the file as you would any internal inventory asset
- No network traffic is generated until the user explicitly double-clicks a device

## Lessons Learned
- Tkinter's `ttk.Treeview` requires explicit column configuration for both `columns` and `displaycolumns` — omitting `displaycolumns` causes the first column to render invisibly in some Python versions
- Writing `devices.json` atomically (write to a temp file, then rename) prevents data loss if the application closes mid-write; a simple `json.dump` directly to the target file can corrupt it on an interrupted save
- PyInstaller's `--onefile` mode embeds everything into a single EXE but is significantly slower to start than `--onedir` mode, which produces a folder with a fast-loading executable — for a tool opened frequently throughout the day, `--onedir` is the better choice
- Subnet-directed broadcast (e.g., `192.168.10.255`) is necessary for waking machines on a different subnet; the global broadcast `255.255.255.255` is blocked by most routers
