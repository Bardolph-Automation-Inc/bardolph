#!/usr/bin/env python

"""Minimal Demo

Simple example use of ls_module that just launches a script contained in a
string.
"""

from bardolph.controller import ls_module

def main():
    ls_module.configure()
    ls_module.queue_script("on all time 5 off all")

if __name__ == "__main__":
    main()
