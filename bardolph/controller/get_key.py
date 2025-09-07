# bardolph/controller/get_key.py
import sys

if sys.platform.startswith("win"):
    import msvcrt

    def getch(timeout=None):
        if timeout is None:
            ch = msvcrt.getch()
            return ch.decode("utf-8", errors="ignore")
        # simple timed poll
        import time
        start = time.time()
        while True:
            if msvcrt.kbhit():
                ch = msvcrt.getch()
                return ch.decode("utf-8", errors="ignore")
            if time.time() - start >= float(timeout):
                return ""
else:
    import termios, tty, select

    def getch(timeout=None):
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            if timeout is None:
                return sys.stdin.read(1)
            r, _, _ = select.select([sys.stdin], [], [], float(timeout))
            return sys.stdin.read(1) if r else ""
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
