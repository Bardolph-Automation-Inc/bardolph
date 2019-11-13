.. _main:

.. figure:: logo.png
   :align: center
    
   http://www.bardolph.org

Documentation
#############
 
.. toctree::
   :maxdepth: 1
   :caption: Contents:

**Bardolph** is a facility for controlling `LIFX <https://www.lifx.com>`_ lights
through a simple scripting language. It can be used
to control lights in an automated way with a minimal
syntax. The intended audience is people who are pretty good with command-line 
tools and have some kind of experience with scripting and/or software
development. 

The program does not use the Internet to access the bulbs, and no login is 
required; all of its communication occurs over the local WiFi network. You 
can edit a script with a basic text editor and run it from the command
line.

This project relies on the 
`lifxlan <https://pypi.org/project/lifxlan>`_
Python library to access the bulbs. You need to have it installed for the code
in this project to run. If you run the web server, you will also need 
`flup <https://www.saddi.com/software/flup>`_ and
`Flask <https://palletsprojects.com/p/flask>`_.

It may be missing some of what you might expect of a scripting language,
as it's still under development. However, it is also very simple, and
should be usable by non-programmers.

.. index::
   single: quick examples

Quick Examples
==============
The source distribution contains some sample scripts in the `scripts` directory.
They should work with whatever lights may be on the network.  For a more complete
description of the scripting langage, please see
:ref:`language`.

Here is a script, named `all_on.ls`, that will turn on all your lights::

  duration 1.5 on all

The `duration` parameter, which is described below, works to slowly turn on the
lights over a period 1.5 seconds, which is a much nicer experience than abruptly
turning them on with no ramp-up.

You run the script with:

.. code-block:: bash

  lsrun scripts/all_on.ls

In this case, `lsrun` is a small Python program that becomes available after you
install Bardolph. It is a thin layer that executes the `run.py` module.

Another example, `on5.ls`, turns on all the lights, waits for 5 minutes, and
then turns them all off again::

  duration 1.5 on all
  time 300 off all

To run it:

.. code-block:: bash

  lsrun scripts/on5.ls

The application executes in the foreground as long as a script is running. In
this example, the application will run for 5 minutes. However, it will spend
most of its time inside a `sleep()` call and won't burden the CPU. In my
experience, execution for the application takes up about 10% of the CPU
cycles on a Raspberry Pi Zero.

You can kill the script and quit by pressing Ctrl-C. You may want to run the
program as a background job, which will terminate when the script is done.

As a convenience, you can pass a script as a command-line parameter using 
`lsrun -s`, followed by the script code in a quoted string. For example, to
turn off all the lights from the keyboard:

.. code-block:: bash

  lsrun -s 'off all'

.. index::
   single: web server; overview
   
Web Server
==========
.. image:: web.png
   :align: center

The web server component makes scripts available in a user-friendly manner.
It implements a simple web page that lists available scripts and provides a
1:1 mapping betwen a script and a URL. The server is designed to run locally 
on a WiFi network.

For example, if have a machine with the hostname
`myserver.local`, you could launch the  `all_on.ls` script by going to
`http://myserver.local/all-on` with any browser on your WiFi network.
The benefit here is the ability to launch a script using a simple
browser bookmark or desktop shortcut.

This is currently a somewhat experimental feature, as getting it to
run can be a bit of a chore. I describe the process for setting up a server
in :ref:`installation`.

The theory of operation for the web server can be found in :ref:`web_server`.

.. index::
   single: Python interface; overview
   
Python Interface
================
I've attempted to make it easy to embed Bardolph scripts in your Python code.
For some uses, this may be significantly easier than learning and using a
full-purpose Python API. For example, here's a complete program that
waits 5 seconds, turns all the lights off, and turns them on again after
another 5 seconds:

.. code-block:: python

  from bardolph.controller import ls_module
  
  ls_module.configure()
  ls_module.queue_script('time 5000 duration 1500 off all on all')


More information on using scripts in Python code is available in
:ref:`python_interface`.

.. index::
   single: installation; quick intro

Quick Installation
##################
This section explains how to instll Bardolph quickly and try it out. For more
complete installation instructions, please see
:ref:`installation`. If you
want to run the web server, you will need to follow those instructions.

Note that Python 3 is required in all cases. If your system defaults to
Python 2.x, there's a good chance that you'll need to use `pip3` instead of
`pip`. Notable culprits here are Raspbian and Debian.

.. code-block:: bash

  pip install bardolph
  export PATH=~/.local/bin:${PATH}

After this intallation, the `lsc`, `lsrun`, and `lscap` commands should be
available. In addition, if you're planning on using scripts in your Python
code, the Bardolph modules should be importable.

To be able to use these commands later on, I would recommend that you modify
your `.bash_profile` (or equivalent, depending on your shell) to
add `~/.local/bin` to your path.

To get a copy of the sample scripts, you still need to download the source:

.. code-block:: bash

  git clone https://github.com/al-fontes-jr/bardolph

Testing the Installation
========================
To do a quick sanity check:

.. code-block:: bash

  lsrun -h
  
This should display a help message. To make sure Bardolph is able to access
your actual bulbs:

.. code-block:: bash

  lscap

This should give you a human-friendly listing of your bulbs, their state, and
which groups/locations they belong to.

The source distribution includes some examples in a directory named `scripts`.
For example:

.. code-block:: bash 

  lsrun scripts/on-all.ls

If you don't have any bulbs, or prefer not to change the color
of those you do have, use the "fakes" option:

.. code-block:: bash 

  lsrun -f scripts/on-all.ls

The fake bulbs sent output to `stdout` that indiciates what commands 
would normally be sent to the actual devices.
 
.. index::
   single: command-line tools

Executing Scripts
#################
This section contains more detailed information about the commands introduced
above. Of these commands, `lsrun` is probably the one you'll use most often.

.. index::
   single: discovery delay

.. note:: During initialization, the process of discovering bulbs can take a 
  while. Basically, a "report" message gets broadcast over the WiFi network,
  and each bulb announces its presence. If the number
  of bulbs is unknown, the discover process has no choice but to wait a
  specific amount of time  for them to stop answering. To minimize any delay,
  use the optional `-n` or `--num-bulbs` flag to specify the actual number
  of bulbs. For example:
  
  .. code-block:: bash
  
    # I have 5 bulbs in my apartment.
    lscap -n 5
    lsrun --num-bulbs 5 scripts/on-all.ls
    
  With this option, discovery stops as soon as the expected
  number has been found, which is usually much faster.

.. index::
   single: lsrun

lsrun - Run a Lightbulb Script
==============================
To run a script from the command line:

.. code-block:: bash

  lsrun name.ls

 
In this context, "name" contains the name of a script. This is essentially
equivalent to:

.. code-block:: bash

  python -m bardolph.controller.run name.ls


You can queue up multiple scripts. If you specify more than one on the
command line, it will queue them in that order and execute them sequentially:


.. code-block:: bash

  lsrun light.ls dark.ls

 
This would run `light.ls`, and upon completion, execute `dark.ls`.

Command Line Options
--------------------
Command-line flags modify how a script is run. Each option has a long and a short
syntax. For example:

.. code-block:: bash

  lsrun --verbose test.ls
  lsrun -v color_cycle.ls

Available options:

* `-r` or `--repeat`: Repeat the scripts indefinitely, until Ctrl-C is pressed.
* `-s` or `--script`: Run text from the command line as a script.
* `-v` or `--verbose`: Generate full debugging output while running.
* `-f` or `--fake`: Don't operate on real lights. Instead, use "fake" lights that
  just send output to stdout. This can be helpful for debugging and testing.
* `-n` or `--num-lights`: Specify the number of lights that are on the network.

With the -f option, there will be 5 fake lights, and their name are fixed as
"Table", "Top", "Middle", "Bottom", and "Chair". Two fake groups are
available: "Pole" and "Table". One location named "Home" contains all
of the fake lights, as well. If you want to use a different set of fake lights,
you will need to edit some Python code. Specificlly, you'll need to modify
`LightSet.discover` in `tests/fake_light_set.py`.

Use of the -s option requires the use of ticks or quotation marks
to contain the script, which will always contain more than one word. For example to
turn on all the lights, wait 60 seconds, and turn them
off again, you can do the following from the command line:

.. code-block:: bash

  lsrun -s 'on all time 60000 off all'
  
.. index::
   single: lsc
   single: compiler
   single: lightbulb script compiler

lsc - Lightbulb Script Compiler
===============================
The lightbulb script compiler writes a  parsed and encoded version of the script
to file  `__generated__.py`.

The syntax is:

.. code-block:: bash

  lsc name.ls 

This is equivalent to:
 
.. code-block:: bash

  python -m bardolph.controller.lsc

Only one file name may be provided. The generated file can be run from the
command line like any other Python module:

.. code-block:: bash

  lsc scripts/evening.ls
  python -m __generated__

The generated Python module relies on Bardolph's Python modules, which
should be available after installation.

If you want to use this module in your own Python code, you can import the
and call the function `run_script()`.

Command Line Options
--------------------
The generated program has two options:

* `-f` or `--fakes`: Instead of accessing the lights, use "fake" lights that
  just send output to the log.
* `-d` or `--debug`: Use debug-level logging.


For example, after you've generated the python program:

.. code-block:: bash

  python -m __generated__ -fd


This would not affect any physical lights, but would send text to the screen
indicating what the script would do.

.. index::
   single: capture
   single: lscap

lscap - Capture Light State
===========================
This program captures the current state of the lights and generates the
requested type of output. The default output is a human-readable listing
of the lights. With the -s option, it can give you a convenient
starting point for creating a new script. This command is also helpful for
taking a quick look at the state of your bulbs.

The `lscap` command is equivalent to `python -m bardoolph.controller.snapshot`.

Command Line Options
--------------------
Command-line options control the operation of the command and the type of
output it produces, notably:

* `-s` or `--script`: outputs a lightbulb script to `stdout`. If you redirect
  that output to a file and run it as a script, it will restore the lights to
  the same state, including color and power.
* `-t` or `--text`: outputs text to `stdout`, in a human-friendly listing of all
  the known bulbs, groups, and locations.
* `-p` or `--py`: builds file `__generated__.py` based on the current state of
  all discovered bulbs. The resulting file is very similar to the output
  generated by the `lsc` command, and can be run with `python -m __generated__`.
* `-n` or `--num-lights`: Specify the number of lights that are on the network.

.. index:
   single: system requirements

System Requirements
###################
The program has been tested on Python versions at or above 3.5.1. I
haven't tried it, but I'm almost certain that it won't run on any 2.x 
version.

Because I haven't done any stress testing, I don't know the limits on
script size. Note that the application loads the encoded script into memory
before executing it.

I've run the program on MacOS 10.14.5 & 10.15, Debian Linux Stretch, and the
June, 2019, release of Raspbian. It works fine for me on a Raspberry Pi Zero W,
controlling 5 bulbs.

Supported Devices
=================
I have tested with the devices that I own, which includes the 1100-Lumen A19
light with the disk-shaped lens, and the 800-Lumen A19 "Mini" globe-shaped
bulb. All the bulbs I own are multi-colored, which means that I haven't done
any testing with "Day and Dusk" or "White" bulbs. I would expect them to
work ok, although I don't really know.

Given the wide-open nature of their API, I plan to start work on supporting other
LIFX devices, including those that can display more than one color at a time,
as soon as I get around to buying them.

Missing Features
################
These are among the missing features that I'll be working on, in no particular
order:

* Easy-to-use web server.
* Flow of control, such as loops, branching, and subroutines.
* Mathematical expressions.
* Support for other devices (I don't own anything but multi-color bulbs).

Project Name Source
###################
`Bardolph <https://en.wikipedia.org/wiki/Bardolph_(Shakespeare_character)>`_ was
known for his bulbous nose.
