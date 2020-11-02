.. figure:: logo.png
   :align: center

   http://www.bardolph.org

.. index:: Python interface

.. _python_interface:

Python Interface
################
If you're looking to quickly write some Python code to control your lights,
you can easily run lightbulb scripts using `ls_module.py`. This module
performs the necessary runtime initialization and offers a clean entry point
for running a script.

In the source distribution, the `embedded` directory contains example programs
that show how to embed lightbulb scripts inside Python code.

Setup
=====
To be able to use `ls_module`, you first need to do at least the minimal
installation, as described in :ref:`installation`.

Usage
=====
Before running any scripts, the module needs to be initialzed once with
`configure()`.  After that, you can queue up an arbitrary number of
scripts with `queue_script()`. For example:

.. code-block:: python

  from bardolph.controller import ls_module

  ls_module.configure()
  ls_module.queue_script('time 10 on all')
  ls_module.queue_script('time 5 off all')


This program waits 10 seconds, turns on all the lights, and then turns them all
off again after 5 seconds.

The `configure()` function performs a bunch of internal initialization, and
then discovers the lights out on the network. After that, it spawns a thread
to repeat the discovery process every 5 minutes, continuously refreshing
the internal list of available lights.

Your code can queue up jobs at any time, even while others are running. In
the above example, the first call to `queue_script()` returns immediately,
although the lights won't come on until 10 seconds have elapsed. The second
script, which turns the lights off, gets queued up asynchronously while the
first script continues to run. That second script will start immediately
after first one finishes.

The `queue_script()` function compiles the incoming string and puts the
resulting VM machine code into a queue. That queue is processed by a separate
thread that is spawned by the `JobControl` class.

You can use the return value from `queue_script()` to access the process that
executes the script. That value is an instance of `job_control.Agent`, which
is in the source code under `bardolph/controller/lib`. Notable methods of this
`Agent` object allow you to query whether it's running via `is_running()`, or
stop the script's execution by calling `request_stop()`.

In the following example, a script with an infinite loop turns the lights off
and on every 15 seconds. It is allowed to run for 5 minutes.

.. code-block:: python

  import time

  from bardolph.controller import ls_module

  ls_module.configure()
  agent = ls_module.queue_script('time 15 repeat begin on all off all end')
  time.sleep(5 * 60)
  agent.request_stop()

Note that the VM instance execting the script runs in a separate thread.

Example Code
============
The examples in `embeded` are documented more thoroughly and illustrate some
basic use cases. To get them, you need to pull down the source code as
described in :ref:`installation`.

*   `hello_lights.py` turns all the lights on, waits 5 seconds, and turns them
    off again.
    https://github.com/al-fontes-jr/bardolph/blob/master/embedded/hello_lights.py
*   `stop_demo.py`, shows how to stop a script that contains an infinite loop.
    https://github.com/al-fontes-jr/bardolph/blob/master/embedded/stop_demo.py
*   `kbd_demo.py` accepts input from the keyboard and sets the color of the
    lights accordingly.
    https://github.com/al-fontes-jr/bardolph/blob/master/embedded/kbd_demo.py

You can try these scripts from the `bardolph` directory with:

.. code-block:: bash

    python -m embedded.hello_lights

    python -m embedded.stop_demo

    python -m embedded.kbd_demo

