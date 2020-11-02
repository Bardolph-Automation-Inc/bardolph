#!/usr/bin/env python

"""Keyboard-driven Demo

This is a simple example that shows how to queue up scripts using Python
code and ls_module.

It queues up a script whenever the user presses one of several color keys. Each
script turns the lights turn to a saturated color, waits for a few
seconds, and returns the light to a neutral, zero-saturated color.

The available colors are blue, cyan, green, red, yellow, and violet. The color
is chosen by pressing the first letter in a color's name.

The script takes about 6 seconds to run, and new script job is queued up every
time a key is pressed. This means that a rather long script queue can be built
with some fast typing.

When 'q' is pressed, the program will exit after all the queued-up scripts
have completed.
"""

from bardolph.controller import get_key, ls_module


class KbdDemo:
    _hue = {
        'b': 240,
        'c': 180,
        'g': 120,
        'r': 0,
        'y': 60,
        'v': 300
    }

    def on_key(self, c):
        hue = self._hue.get(c)
        if hue is not None:
            script = """
                duration 2 hue {} saturation 80 brightness 80 kelvin 2500
                set all
                time 3 duration 2 saturation 0 kelvin 2700 set all
                time 3 wait
            """.format(hue)

            # Here is where we queue up the script. If no script is already
            # running, this one will start immediately. Otherwise, it is
            # appended to the end of the queue and will eventually run.
            ls_module.queue_script(script)

    def prompt(self):
        return ', '.join(self._hue.keys()) + ' or q to quit.'


def main():
    # This is required to initialize ls_module.
    ls_module.configure()

    demo = KbdDemo()
    print(demo.prompt())
    c = ' '
    while c != 'q':
        c = get_key.getch()
        print(c, end='\r')
        demo.on_key(c)


if __name__ == "__main__":
    main()
