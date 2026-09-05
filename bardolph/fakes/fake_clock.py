from bardolph.lib import i_lib
from bardolph.lib import injection

class Clock(i_lib.Clock):
    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def wait_until(self) -> None:
        pass

    def pause_for(self, _) -> None:
        pass

def configure():
    injection.bind_instance(Clock()).to(i_lib.Clock)
