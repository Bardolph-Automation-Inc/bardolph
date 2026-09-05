#!/usr/bin/env python3
"""
virtual_light.py — Real-time "virtual light" viewer for Bardolph fake_light -f output.

Usage:
  # Option A: Run Bardolph via subprocess inside this script
  python virtual_light.py --cmd "lsrun cycle-color-lamp.ls -f"

  # Option B: Pipe existing output into the script
  lsrun cycle-color-lamp.ls -f | python virtual_light.py

What it does:
- Parses lines like:
  11:41:06 AM fake_light.py(78): Set color for "Lamp": [0, 49151, 39321, 0], 10000
- Interprets [H, S, B, K] as 16-bit HSBK in the LIFX style (H in [0..65535], S and B in [0..65535], K ignored here)
- Updates a small Tkinter window to show current color and brightness.

Requires: Python 3.8+ (standard library only).
"""

import argparse
import re
import sys
import threading
import queue
import subprocess
import shlex
import colorsys
from dataclasses import dataclass
from typing import Optional, Tuple

try:
    import tkinter as tk
    from tkinter import ttk
except Exception:
    print(
        "Tkinter is required to display the virtual light UI.",
        file=sys.stderr)
    sys.exit(1)


# -------- Parsing --------

LOG_PATTERN = re.compile(
    r"""Set\s+color\s+for\s+\"(?P<name>.+?)\"\s*:\s*\[\s*
        (?P<h>\d+)\s*,\s*(?P<s>\d+)\s*,\s*(?P<b>\d+)\s*,\s*(?P<k>\d+)
        \s*\]\s*,\s*(?P<duration>\d+)
    """,
    re.IGNORECASE | re.VERBOSE,
)

@dataclass
class LightState:
    name: str
    h: int
    s: int
    b: int
    k: int
    duration_ms: int

def parse_line(line: str) -> Optional[LightState]:
    m = LOG_PATTERN.search(line)
    if not m:
        return None
    try:
        return LightState(
            name=m.group("name"),
            h=int(m.group("h")),
            s=int(m.group("s")),
            b=int(m.group("b")),
            k=int(m.group("k")),
            duration_ms=int(m.group("duration"))
        )
    except Exception:
        return None


# -------- Color conversion --------

def lifx_hsbk_to_rgb_hex(h: int, s: int, b: int) -> str:
    """
    Convert LIFX-style 16-bit HSB (HSV) to Tkinter hex color.

    - Hue: 0..65535 => degrees 0..360
    - Sat, Bri: 0..65535 => 0.0..1.0
    """
    # Guard rails
    h = max(0, min(65535, h))
    s = max(0, min(65535, s))
    b = max(0, min(65535, b))

    # Convert
    hue_deg = (h / 65535.0) * 360.0
    sat = s / 65535.0
    bri = b / 65535.0

    # colorsys uses H in [0..1]
    h_norm = (hue_deg % 360.0) / 360.0
    r, g, bl = colorsys.hsv_to_rgb(h_norm, sat, bri)

    # To 0..255
    r_i = int(round(r * 255))
    g_i = int(round(g * 255))
    b_i = int(round(bl * 255))

    return f"#{r_i:02x}{g_i:02x}{b_i:02x}"


# -------- UI --------

class VirtualLightUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Bardolph Virtual Light")
        self.root.geometry("300x200")
        self.root.minsize(260, 180)

        self.name_var = tk.StringVar(value="(no light yet)")
        self.rgb_var = tk.StringVar(value="#000000")
        self.brightness_pct_var = tk.StringVar(value="0%")

        # Container
        container = ttk.Frame(self.root, padding=10)
        container.pack(fill="both", expand=True)

        # Name
        name_label = ttk.Label(container, textvariable=self.name_var,
                               font=("Segoe UI", 12, "bold"))
        name_label.pack(anchor="w")

        # Color patch
        self.patch = tk.Canvas(container, width=260, height=80,
                               highlightthickness=1, highlightbackground="#888")
        self.patch.pack(fill="x", pady=(8, 8))
        self.rect = self.patch.create_rectangle(2, 2, 258, 78,
                                                fill="#000000", outline="")

        # Brightness
        br_row = ttk.Frame(container)
        br_row.pack(fill="x")
        ttk.Label(br_row, text="Brightness: ").pack(side="left")
        self.br_val_label = ttk.Label(br_row,
                                      textvariable=self.brightness_pct_var)
        self.br_val_label.pack(side="left")
        self.br_scale = ttk.Progressbar(container,
                                        orient="horizontal",
                                        mode="determinate",
                                        maximum=100)
        self.br_scale.pack(fill="x", pady=(4, 0))

        # RGB label
        rgb_label = ttk.Label(container, textvariable=self.rgb_var,
                              font=("Consolas", 10))
        rgb_label.pack(anchor="w", pady=(6, 0))

        # Thread-safe update queue
        self.queue: "queue.Queue[Tuple[str, str, int]]" = queue.Queue()

        # Poll queue
        self.root.after(50, self._poll_queue)

    def _poll_queue(self):
        try:
            while True:
                name, rgb_hex, brightness_pct = self.queue.get_nowait()
                self._apply_state(name, rgb_hex, brightness_pct)
        except queue.Empty:
            pass
        self.root.after(50, self._poll_queue)

    def _apply_state(self, name: str, rgb_hex: str, brightness_pct: int):
        self.name_var.set(name)
        self.rgb_var.set(rgb_hex.upper())
        self.brightness_pct_var.set(f"{brightness_pct}%")
        self.br_scale["value"] = brightness_pct
        # Update color patch
        self.patch.itemconfig(self.rect, fill=rgb_hex)

    def push_state(self, name: str, rgb_hex: str, brightness_pct: int):
        self.queue.put((name, rgb_hex, brightness_pct))

    def run(self):
        self.root.mainloop()


# -------- Streaming / Reader --------

def reader_loop_from_stream(stream, ui: VirtualLightUI):
    for raw in iter(stream.readline, ""):
        if not raw:
            break
        line = raw.strip()
        st = parse_line(line)
        if st:
            rgb = lifx_hsbk_to_rgb_hex(st.h, st.s, st.b)
            brightness_pct = int(
                round((max(0, min(65535, st.b)) / 65535.0) * 100))
            ui.push_state(st.name, rgb, brightness_pct)


def spawn_subprocess_and_stream(cmd: str, ui: VirtualLightUI):
    # Use shlex.split for proper tokenization
    args = shlex.split(cmd)
    proc = subprocess.Popen(
        args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, bufsize=1, universal_newlines=True)
    assert proc.stdout is not None

    for line in proc.stdout:
        if line is None:
            break
        line = line.rstrip("\n")
        st = parse_line(line)
        if st:
            rgb = lifx_hsbk_to_rgb_hex(st.h, st.s, st.b)
            brightness_pct = round((max(0, min(65535, st.b)) / 65535.0) * 100)
            ui.push_state(st.name, rgb, brightness_pct)

    proc.wait()


def main():
    ap = argparse.ArgumentParser(
        description="Virtual light viewer for Bardolph fake_light -f output.")
    hlp = ('Command to run and parse (e.g., "lsrun cycle-color-lamp.ls - f"). '
           'If omitted, reads from STDIN.')
    ap.add_argument("--cmd", type=str, default=None, help=hlp)
    args = ap.parse_args()

    ui = VirtualLightUI()

    if args.cmd:
        t = threading.Thread(target=spawn_subprocess_and_stream, args=(args.cmd, ui), daemon=True)
    else:
        # If stdin is a TTY, inform user how to use piping.
        if sys.stdin.isatty():
            print("Reading from STDIN. Example:\n  lsrun cycle-color-lamp.ls -f | python virtual_light.py\nOr use --cmd 'lsrun cycle-color-lamp.ls -f'", file=sys.stderr)
        t = threading.Thread(target=reader_loop_from_stream,
                             args=(sys.stdin, ui), daemon=True)

    t.start()
    ui.run()


if __name__ == "__main__":
    main()
