#!/usr/bin/env python

"""
Producer demo. Assumes that the light is named "Demo".

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
        saturation {}
        brightness 25
        time 1.5
        duration 1.5
        set "{}"
    """
    for hue in range(0, 361, 45):
        for saturation in range(1, 100, 20):
            yield fmt.format(hue, saturation, light_name)
        for saturation in range(100, 1, -20):
            yield fmt.format(hue, saturation, light_name)
    yield f'saturation 0 brightness 10 duration 2 set "{light_name}"'


def main() -> None:
    ls_module.configure()
    ls_module.consume_scripts(script_producer())


if __name__ == "__main__":
    main()
