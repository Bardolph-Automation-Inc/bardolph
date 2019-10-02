#!/usr/bin/env python

from bardolph.controller import ls_module

def main():
    script = "time 5000 duration 1500 off all on all"
    ls_module.configure()
    ls_module.queue_script(script)

if __name__=="__main__":
    main()
