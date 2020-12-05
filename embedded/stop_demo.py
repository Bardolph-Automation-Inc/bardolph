#!/usr/bin/env python

"""Demonstration of stopping a script from Python

This example shows how to stop a script that is running from Python code, using
ls_module. It launches a script that runs in an infinite loop, and stops the
execution when the user hits "enter".
"""

from bardolph.controller import ls_module

def main():
    ls_module.configure()
    agent = ls_module.queue_script(
        'duration 1.5 time 2 repeat begin on all off all end')
    input('Press Enter to stop.')
    agent.request_stop()

if __name__ == "__main__":
    main()
