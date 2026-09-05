#!/usr/bin/env python


"""
Queue demo. Assumes that the light is named "Demo".

"""
from collections.abc import Iterator

from bardolph.controller import ls_module

# Change to the name of your light.
#
light_name = "Lamp"


def script_producer() -> Iterator[str]:
    fmt = """
        kelvin 3500
        hue {}
        saturation 75
        brightness {}
        time 1.5
        duration 1.5
        set "{}"
    """
    for hue in range(0, 361, 45):
        for brightness in range(1, 50, 10):
            yield fmt.format(hue, brightness, light_name)
        for brightness in range(50, 1, -10):
            yield fmt.format(hue, brightness, light_name)


def main() -> None:
    ls_module.configure()
    for script in script_producer():
        ls_module.queue_script(script)
    ls_module.queue_script(
        f'saturation 0 brightness 10 duration 2 set "{light_name}"')


if __name__ == "__main__":
    main()
