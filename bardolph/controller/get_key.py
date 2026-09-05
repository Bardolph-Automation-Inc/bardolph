#!/usr/bin/env python

import os
import platform

import sys


if platform.system().lower() == 'windows' or os.name == 'nt':
    import msvcrt

    def getch() -> str:
        ch = msvcrt.getwch()

        # If an arrow or other special key is pressed, return a string
        # containing two characters.
        #
        return ch + msvcrt.getwch() if ch in ('\x00', '\xe0') else ch
else:
    import termios
    import tty

    def getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)

        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

        return ch


def main() -> None:
    ord_c = 0
    ctrl_c_count = 0

    # Quit if ^D is pressed once or if ^C is pressed twice.
    #
    while ord_c != 4 and ctrl_c_count < 2:
        c = getch()
        if len(c) > 1:
            print('Special key:', c)
            ctrl_c_count = 0
        else:
            ord_c = ord(c)
            if c.isprintable():
                print(c, hex(ord_c))
            else:
                print(hex(ord_c))

            if ord_c == 3:
                ctrl_c_count += 1
            else:
                ctrl_c_count = 0


if __name__ == "__main__":
    print()
    main()
