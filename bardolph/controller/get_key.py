import sys

if sys.platform == "win32":
    import msvcrt

    def getch():
        ch = msvcrt.getwch()

        # Handle special keys (arrows, function keys, etc.)
        if ch in ("\x00", "\xe0"):
            msvcrt.getwch()
            return ""

        return ch

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
