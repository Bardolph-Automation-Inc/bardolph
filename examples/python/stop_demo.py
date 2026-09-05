#!/usr/bin/env python

"""
Demonstration of stopping a script from Python

This example shows how to stop a script that is running from Python code, using
ls_module. It launches a script that runs in an infinite loop, and stops the
execution when the user hits "enter".
"""

from bardolph.controller import ls_module
from bardolph.lib.job_control import Agent

# Change to the name of your light.
#
light_name = "Lamp"


def main():
    script = f"""
        duration 1.5 time 2
        repeat
            begin
                on "{light_name}"
                off "{light_name}"
            end
    """
    ls_module.configure()
    agent: Agent = ls_module.queue_script(script)
    input('Press Enter to stop.\n')
    agent.request_stop()


if __name__ == "__main__":
    main()
