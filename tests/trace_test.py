#!/usr/bin/env python

from bardolph.lib.trace import trace_call, trace_call_enable

_output = ""

def test_callback(msg):
    _output += msg

class TraceTest:
    @trace_call
    def fn1(self, x, y):
        print("This is fn1:", x, y)

def main():
    trace_call_enable(True)
    TraceTest().fn1("a", "b")

if __name__ == '__main__':
    main()
