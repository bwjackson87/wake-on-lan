# Wake-on-LAN

A lightweight Windows desktop application for sending [Wake-on-LAN](https://en.wikipedia.org/wiki/Wake-on-LAN) magic packets to network devices. Built with Python and Tkinter — no third-party runtime dependencies.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python) ![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey?logo=windows) ![License](https://img.shields.io/badge/License-MIT-green)

## Features

- Add, edit, and remove named devices with their MAC addresses
- Configurable broadcast IP per device (supports subnet-directed broadcast)
- Sends a standard 102-byte magic packet over UDP port 9
- Device list persisted to `devices.json` next to the executable
- Double-click a device to wake it instantly
- Alternating row colors for easy reading
- Builds to a single portable `.exe` with PyInstaller

## Screenshots

> Run the app with `python wol.py` to see it in action.

## Requirements

- Python 3.10 or later (for development / running from source)
- No third-party packages required — uses only the Python standard library

## Usage

### Run from source

```bash
python wol.py
```

### Build a standalone executable

```batch
build.bat
```

The output `WakeOnLAN.exe` will appear in the `dist\` folder. Copy it anywhere — it carries everything it needs.

## How Wake-on-LAN works

A magic packet is a broadcast frame containing 6 bytes of `0xFF` followed by the target device's 48-bit MAC address repeated 16 times. When a network adapter in a sleeping PC receives this packet, it powers the machine on.

Your router or managed switch must allow broadcast UDP traffic on port 9, and the target machine must have Wake-on-LAN enabled in its BIOS/UEFI and network adapter settings.

## Project structure

```
WakeOnLAN/
├── wol.py        # Application source (UI + WoL logic)
├── build.bat     # One-click PyInstaller build script
└── devices.json  # Auto-created at runtime; stores saved devices
```

## License

MIT — see [LICENSE](LICENSE) for details.
