#!/usr/bin/env python

from bardolph.controller import ls_module

def main():
    ls_module.configure()
    ls_module.queue_script("time 5000 duration 1500 off all on all")

if __name__ == "__main__":
    main()
