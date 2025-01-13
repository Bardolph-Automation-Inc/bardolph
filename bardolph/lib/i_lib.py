class Clock:
    def start(self): pass
    def stop(self): pass
    def reset(self): pass
    def pause_for(self, _): pass

class Settings: pass

class TimePattern:
    def match(self, hour, minute): pass

class LogConfig: pass

class Output:
    def out(self, output) -> None: pass
    def newline(self) -> None: pass
    def flush(self) -> None: pass

def configure(): pass
