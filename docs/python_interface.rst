.. figure:: logo.png
   :align: center
   
   http://www.bardolph.org

.. index::
   single: Python interface; reference

.. _python_interface:

Python Interface
################
I hope that all the code is clear and modular enough to be reused in someone else's
programs. However, if you're just looking to quickly write some Python code to
control your lights, you can easily run lightbulb scripts using `ls_module.py`. 
This simple module performs the necessary runtime initialization and offers a 
clean entry point for running a script.

In the source distribution, the `embedded` directory contains example programs
that show how to embed lightbulb scripts inside Python code.

Setup
=====
To be able to use `ls_module`, you first need to add bardolph to your Python
run-time environment. You can do this with `pip install bardolph`, as long
as you're set up to download from pypi.org.

To remove the library from your environment, run `pip uninstall bardolph`.

Usage
=====
Before running any scripts, the module needs to be initialzed once with
`configure()`.  After that, you can queue up an arbitrary number of 
scripts with `queue_script()`. For example:

.. code-block:: python

  from bardolph.controller import ls_module

  ls_module.configure()
  ls_module.queue_script('time 1 all on')
  ls_module.queue_script('time 5 all off')


This program waits 10 seconds, turns on all the lights, and then turns them all off 
again after 5 seconds.

The `configure()` function performs a bunch of internal initialization, and 
then discovers the lights out on the network. After that, It spawns a thread 
that repeats the discovery process every 5 minutes to continuously refresh
its internal list of available lights.

Your code can queue up jobs at any time, even while others are running. In
the above example, the first call to `queue_script()` returns immediately,
although the lights won't come on until 10 seconds have elapsed. The second 
script, which turns the lights off, gets queued up asynchronously while the first
script continues to run. However, that second script will not start until the
first one finishes.

The `queue_script()` function parses the incoming string and puts the resulting
byte code into a queue. That queue is processed by a separate thread that is 
spawned by the `JobControl` class.

If your program logic requires it, you can stop the current script and clear out the 
queue by calling `ls_module.request_stop()`.
