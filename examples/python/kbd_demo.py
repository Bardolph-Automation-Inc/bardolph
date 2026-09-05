#!/usr/bin/env python

"""
Keyboard-driven Demo

This is a simple example that shows how to queue up scripts using Python
code and ls_module.

It queues up a script whenever the user presses one of several color keys. Each
script turns the lights to a saturated color, waits for a few seconds, and
returns the light to a neutral, zero-saturated color.

The available colors are blue, cyan, green, red, yellow, and violet. The color
is chosen by pressing the first letter in a color's name.

The script takes about 6 seconds to run, and new script job is queued up every
time a key is pressed. This means that a rather long script queue can be built
with some fast typing.

When 'q' is pressed, the program will exit after all the queued-up scripts
have completed.
"""

from typing import ClassVar

from bardolph.controller import get_key, ls_module


# Change to the name of your light.
#
light_name = "Demo"


class KbdDemo:
    _hue: ClassVar[dict[str, int]] = {
        'b': 240,
        'c': 180,
        'g': 120,
        'r': 0,
        'y': 60,
        'v': 300
    }

    def on_key(self, c: str) -> None:
        if c == 'q':
            print("q pressed. Will stop when the current queue is done.")
            ls_module.queue_script(
                f'duration 2 brightness 10 set "{light_name}"')
        hue = self._hue.get(c)
        if hue is not None:
            script = f"""
                hue {hue} saturation 80 brightness 50 kelvin 2500
                time 0 duration 2
                set "{light_name}"
                time 2
                wait
            """
            ls_module.queue_script(script)
            print(f'Queued hue of {hue}')

    def prompt(self) -> str:
        return ', '.join(self._hue.keys()) + ' or q to quit.'


def main() -> None:
    ls_module.configure()

    demo = KbdDemo()
    print(demo.prompt())
    c = ''
    while c != 'q':
        c = get_key.getch()
        print(c, end='\r')
        demo.on_key(c)


if __name__ == "__main__":
    main()
