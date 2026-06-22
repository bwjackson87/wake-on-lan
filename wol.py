"""
Wake-on-LAN — sends magic packets to wake network devices.
Devices stored in devices.json next to the executable.
"""

import json
import os
import socket
import struct
import sys
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

# ---------------------------------------------------------------------------
# Config path — sits next to the .exe (or .py during dev)
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(sys.executable if getattr(sys, "frozen", False) else os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "devices.json")

# ---------------------------------------------------------------------------
# WoL core
# ---------------------------------------------------------------------------

def _clean_mac(mac: str) -> str:
    """Normalize MAC to 12 hex chars, no separators."""
    cleaned = mac.replace(":", "").replace("-", "").replace(".", "").upper()
    if len(cleaned) != 12 or not all(c in "0123456789ABCDEF" for c in cleaned):
        raise ValueError(f"Invalid MAC address: {mac}")
    return cleaned


def send_magic_packet(mac: str, broadcast: str = "255.255.255.255", port: int = 9) -> None:
    mac_bytes = bytes.fromhex(_clean_mac(mac))
    magic = b"\xff" * 6 + mac_bytes * 16
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.connect((broadcast, port))
        sock.send(magic)


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------

def load_devices() -> list[dict]:
    if not os.path.exists(CONFIG_FILE):
        return []
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)


def save_devices(devices: list[dict]) -> None:
    with open(CONFIG_FILE, "w") as f:
        json.dump(devices, f, indent=2)


# ---------------------------------------------------------------------------
# Dialog — Add / Edit device
# ---------------------------------------------------------------------------

class DeviceDialog(tk.Toplevel):
    def __init__(self, parent, title: str, name: str = "", mac: str = "", broadcast: str = "255.255.255.255"):
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.result = None
        self._build(name, mac, broadcast)
        self.transient(parent)
        self.grab_set()
        self.geometry(f"+{parent.winfo_rootx() + 60}+{parent.winfo_rooty() + 60}")
        self.wait_window()

    def _build(self, name, mac, broadcast):
        pad = dict(padx=12, pady=6)
        frame = ttk.Frame(self, padding=16)
        frame.grid(sticky="nsew")

        ttk.Label(frame, text="Device Name").grid(row=0, column=0, sticky="w", **pad)
        self._name = ttk.Entry(frame, width=28)
        self._name.insert(0, name)
        self._name.grid(row=0, column=1, **pad)

        ttk.Label(frame, text="MAC Address").grid(row=1, column=0, sticky="w", **pad)
        self._mac = ttk.Entry(frame, width=28)
        self._mac.insert(0, mac)
        self._mac.grid(row=1, column=1, **pad)

        ttk.Label(frame, text="Broadcast IP").grid(row=2, column=0, sticky="w", **pad)
        self._broadcast = ttk.Entry(frame, width=28)
        self._broadcast.insert(0, broadcast)
        self._broadcast.grid(row=2, column=1, **pad)

        ttk.Label(frame, text="e.g. 255.255.255.255 or 192.168.1.255",
                  foreground="gray").grid(row=3, column=1, sticky="w", padx=12)

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=(12, 0))
        ttk.Button(btn_frame, text="Save", command=self._save).pack(side="left", padx=6)
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side="left", padx=6)

        self._name.focus_set()
        self.bind("<Return>", lambda _: self._save())
        self.bind("<Escape>", lambda _: self.destroy())

    def _save(self):
        name = self._name.get().strip()
        mac = self._mac.get().strip()
        broadcast = self._broadcast.get().strip() or "255.255.255.255"

        if not name:
            messagebox.showerror("Missing field", "Please enter a device name.", parent=self)
            return
        try:
            _clean_mac(mac)
        except ValueError:
            messagebox.showerror("Invalid MAC", "Enter a valid MAC address.\nExample: AA:BB:CC:DD:EE:FF", parent=self)
            return

        self.result = {"name": name, "mac": mac, "broadcast": broadcast}
        self.destroy()


# ---------------------------------------------------------------------------
# Main window
# ---------------------------------------------------------------------------

class App(tk.Tk):
    ACCENT = "#0078D4"
    BG = "#F3F3F3"
    ROW_ODD = "#FFFFFF"
    ROW_EVEN = "#EAF4FF"

    def __init__(self):
        super().__init__()
        self.title("Wake-on-LAN")
        self.minsize(500, 380)
        self.configure(bg=self.BG)
        self._devices: list[dict] = load_devices()
        self._build_ui()
        self._refresh()

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # Header
        header = tk.Frame(self, bg=self.ACCENT, height=56)
        header.grid(row=0, column=0, sticky="ew")
        tk.Label(
            header, text="⚡  Wake-on-LAN",
            bg=self.ACCENT, fg="white",
            font=("Segoe UI", 16, "bold"),
        ).pack(side="left", padx=20, pady=10)

        # Device list
        list_frame = ttk.Frame(self, padding=(12, 8, 12, 0))
        list_frame.grid(row=1, column=0, sticky="nsew")
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        cols = ("name", "mac", "broadcast")
        self._tree = ttk.Treeview(list_frame, columns=cols, show="headings", selectmode="browse")
        self._tree.heading("name", text="Device Name")
        self._tree.heading("mac", text="MAC Address")
        self._tree.heading("broadcast", text="Broadcast")
        self._tree.column("name", width=180, anchor="w")
        self._tree.column("mac", width=160, anchor="w")
        self._tree.column("broadcast", width=130, anchor="w")

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscroll=scrollbar.set)

        self._tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        self._tree.bind("<Double-1>", lambda _: self._wake())

        # Status bar
        self._status_var = tk.StringVar(value="Select a device and click Wake.")
        status = tk.Label(
            self, textvariable=self._status_var,
            bg=self.BG, fg="#444", anchor="w",
            font=("Segoe UI", 9), padx=14,
        )
        status.grid(row=2, column=0, sticky="ew", pady=(4, 0))

        # Buttons
        btn_frame = tk.Frame(self, bg=self.BG, pady=10)
        btn_frame.grid(row=3, column=0)

        self._wake_btn = tk.Button(
            btn_frame, text="⚡  Wake",
            bg=self.ACCENT, fg="white", relief="flat",
            font=("Segoe UI", 11, "bold"),
            padx=20, pady=8, cursor="hand2",
            command=self._wake,
        )
        self._wake_btn.pack(side="left", padx=8)

        for label, cmd in [("＋ Add", self._add), ("✎ Edit", self._edit), ("✕ Remove", self._remove)]:
            tk.Button(
                btn_frame, text=label,
                bg="#E0E0E0", fg="#222", relief="flat",
                font=("Segoe UI", 10),
                padx=14, pady=8, cursor="hand2",
                command=cmd,
            ).pack(side="left", padx=4)

    # ------------------------------------------------------------------
    # Device list helpers
    # ------------------------------------------------------------------

    def _refresh(self):
        self._tree.delete(*self._tree.get_children())
        for i, dev in enumerate(self._devices):
            tag = "odd" if i % 2 == 0 else "even"
            self._tree.insert("", "end", iid=str(i), values=(dev["name"], dev["mac"], dev["broadcast"]), tags=(tag,))
        self._tree.tag_configure("odd", background=self.ROW_ODD)
        self._tree.tag_configure("even", background=self.ROW_EVEN)

    def _selected_index(self) -> int | None:
        sel = self._tree.selection()
        return int(sel[0]) if sel else None

    def _set_status(self, msg: str, color: str = "#444"):
        self._status_var.set(msg)
        for widget in self.nametowidget(self._status_var._name).winfo_parent().winfo_children():
            pass  # ttk Label colour is set at build time; recreating is cleaner
        # Simpler: just use a plain tk.Label already configured

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _wake(self):
        idx = self._selected_index()
        if idx is None:
            messagebox.showinfo("No selection", "Please select a device to wake.")
            return
        dev = self._devices[idx]
        try:
            send_magic_packet(dev["mac"], dev["broadcast"])
            self._status_var.set(f"✔  Magic packet sent to {dev['name']}  ({dev['mac']})")
        except Exception as exc:
            messagebox.showerror("Error", f"Failed to send packet:\n{exc}")

    def _add(self):
        dlg = DeviceDialog(self, "Add Device")
        if dlg.result:
            self._devices.append(dlg.result)
            save_devices(self._devices)
            self._refresh()
            self._tree.selection_set(str(len(self._devices) - 1))

    def _edit(self):
        idx = self._selected_index()
        if idx is None:
            messagebox.showinfo("No selection", "Please select a device to edit.")
            return
        dev = self._devices[idx]
        dlg = DeviceDialog(self, "Edit Device", dev["name"], dev["mac"], dev["broadcast"])
        if dlg.result:
            self._devices[idx] = dlg.result
            save_devices(self._devices)
            self._refresh()
            self._tree.selection_set(str(idx))

    def _remove(self):
        idx = self._selected_index()
        if idx is None:
            messagebox.showinfo("No selection", "Please select a device to remove.")
            return
        name = self._devices[idx]["name"]
        if messagebox.askyesno("Confirm", f"Remove '{name}'?"):
            self._devices.pop(idx)
            save_devices(self._devices)
            self._refresh()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app = App()
    app.mainloop()
