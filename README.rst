.. _readme:

.. image:: docs/logo.png 

Bardolph Project
################
 
Al Fontes - bardolph@fontes.org

.. toctree::
   :maxdepth: 1
   :caption: Contents:

**Bardolph** is a facility for controlling `LIFX <https://www.lifx.com>`_ lights
through a simple scripting language. It is targeted at people who would like
to control or experiment with their lights in an automated way, but who do not 
want to learn a programming language or API.

The program does not use the Internet to access the bulbs, and no login is 
required; all of its  communication occurs over the local WiFi network. You 
can edit scripts with a basic text editor and run them from the command line.

This project relies heavily on the 
`lifxlan <https://pypi.org/project/lifxlan>`_
Python library to access the bulbs. You need to have it installed for the code
in this project to run. If you run the web server, you will also need 
`flup <https://www.saddi.com/software/flup>`_ and
`Flask <https://palletsprojects.com/p/flask>`_.

The language is missing quite a lot of what you might expect, as it's still
under development. However, it is also very simple, and should be usable
by non-programmers.

Lightbulb Scripts
=================
A script is a plain-text file in which all whitespace is equivalent. You can 
format it with tabs or put the entire script on a single line. 
Comments begin with the '#' character and continue to the end of the line. All
keywords are in lower-case text. By convention, script file names have a ".ls" extension, 
meaning "lightbulb script".

Quick Examples
==============
The source distribution contains some sample scripts in the `scripts` directory.
They should work with whatever lights may be on the network. For example, here is a
script, named `all_on.ls`, that will turn on all your lights::

  duration 1500 on all

You run it with:

.. code-block:: bash

  lsrun scripts/all_on.ls

In this case, `lsrun` is a bash shell script that become available after you
install Bardolph. It is a thin layer that executes the `run.py` module.

The `duration` parameter, which is described below, works to slowly shut off the
lights over a period 1500 ms., which is a much nicer experience than abruptly turning
them off with no dimming.

Another example, `on5.ls`, turns on all the lights, waits for 5 minutes, and then turns
them all off again::

  duration 1500 on all
  time 300000 off all

To run it:

.. code-block:: bash

  lsrun scripts/on5.ls

The application executes in the foreground as long as a script is running. In this
example, the application will run for 5 minutes. However, it will spend most of
its time inside a `sleep()` call to avoid burdening the CPU. In my experience,
scripts spend most of their time inside a delay. For example, execution for the 
application takes up about 10% of the CPU cycles on a Raspberry Pi Zero.

You can kill the script and quit by pressing Ctrl-C. You may want to run the
program as a background job, which will terminate when the script is done.

As a convenience, you can pass a script as a command-line parameter using 
`lsrun -s`, followed by the script code in a quoted string. For example, to
turn off all the lights from the keyboard:

.. code-block:: bash

  lsrun -s 'off all'

Web Server
==========
.. image:: docs/web.png

The web server component makes scripts available in a user-friendly manner.
It implements a simple web page that lists available scripts and provides a
1:1 mapping betwen scripts and URL's. The server is designed to run locally, 
on your WiFi network.

For example, if have a machine with the hostname
`myserver.local`, you could launch the  `all_on.ls` script by going to
`http://myserver.local/all-on` with any browser on your WiFi network.
Because scripts can run over a long period of time, even indefinitely, 
a cheap, dedicated device like a Raspberry Pi is an ideal way to host the 
web server.

This is currently an experimental feature, as getting it to run can be a bit of a chore.
I describe the process for setting up and running a server in
:ref:`web_server`.

Python API
==========
I've attempted to make it easy to use Bardolph scripts in your Python code.
For some uses, this may be significantly easier than learning and using a
full-purpose Python library. For example, here's a complete program that
waits 5 seconds, turns all the lights off, and turns them on again after
another 5 seconds:

.. code-block:: python

  from bardolph.controller import ls_module
  
  ls_module.configure()
  ls_module.queue_script('time 5000 duration 1500 off all on all')


More information on using scripts in Python code is available in
:ref:`python_wrapper`.

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

After this intallation, the `lsc`, `lsrun`, and `lscap` commands should be
available. In addition, if you're planning on using scripts in your Python
code, the bardolph libraries will be available.

To get a copy of the sample scripts, you still need to download the soure:

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

The source distribution includes some examples in a directory named `scripts`.
For example:

.. code-block:: bash 

  lsrun scripts/on-all.ls

If you don't have any bulbs, or don't want to actually alter the state of any
of the ones you do have, use the "fakes" option:

.. code-block:: bash 

  lsrun -f scripts/on-all.ls

Lightbulb Script Tutorial
#########################
Internally, launching a script is a two-step process. First, a parser reads the
source file and compiles it into a sequence of encoded instructions. Next, a
simple virtual machine executes those instructions. A job-control facility
maintains a queue, allowing execution of a sequence of compiled scripts.

You set the color and brightness of the lights specifying
4 numbers: `hue`, `saturation`, `brightness`, and `kelvin`.
Your script supplies these parameters, and the Bardolph virtual machine 
sends them to the bulbs.

The easiest way to understand the meaning of these numbers is to use 
the LIFX mobile app and observe the displayed numbers as you change
the lighting.

The value you supply for `hue` is an angle expressed in
in degrees, normally between 0 and 360. The values for `saturation` 
and `brightness` are treated as percentages, while `kelvin` is a 
temperature modification applied by the bulbs to the resulting color.

All of these number must be positive, and may be floating-point
values. Percentages above 100 are considered invalid. Angles
greater than or equal to 360 are normalized to a number less
than 360 by modulo arithmetic.

Here's another example, showing some comments::

  # comment
  hue 360 # red
  saturation 100 # 100% saturation
  brightness 60.0 # 60% brightness
  kelvin 2700
  set all
  on all

This script sets the colors of all known lights to a bright shade of red and 
turns all of them on. 

When a value isn't specified a second time, the VM uses the existing value. 
For example, the following reuses numbers for `saturation`, `brightness`,
and `kelvin` throughout::

  hue 120 saturation 100 brightness 50 kelvin 2700 set all
  hue 180 set all

This script will:

#. Set all lights to HSBK of 120, 100, 50, 2700
#. Set all lights to HSBK of 180, 100, 50, 2700

Any uninitialized values default to zero, or an empty string. This can lead
to unwanted results, so each of the values should be set at least once before
setting the color of any lights. Or, consider starting your script with
`get all` (the `get` command is described below).

If you prefer to send unmodified numbers to the bulbs, as specified by the 
`LIFX API <https://lan.developer.lifx.com>`_, you can use "raw" values
(and switch back to "logical" units as desired). "Raw" refers to
an integer between 0 and 65535 that gets transmitted unmodified to the bulbs::

  units raw
  hue 30000 saturation 65535 brightness 32767 kelvin 2700 set all
  units logical
  hue 165 saturation 100 brightness 50 kelvin 2700 set all

Individual Lights
=================
Scripts can control individual lights by name. For example, if you have a light
named "Table", you can set its color with::

  hue 120 saturation 100 brightness 75 kelvin 2700
  set "Table"

A light's name is configured when you do initial setup with the LIFX software.

When they appear in a script, bulb names must be in quotation marks. They 
can  contain spaces, but  may not contain a linefeed. For example::

  # Ok
  on "Chair Side"
  
  # Error
  on "Chair
  Side"

If a script contains a name for a light that has not been discovered or is 
otherwise unavailable, an error is sent to the log, but execution of the script
continues. 

Power Command
=============

The commands to turn the lights on or off resemble the `set` command::

  off all
  on "Table"

This turns off all the lights, and turns on the one named "Table".

The "on" and "off" commands have no effect on the color of the lights.
When "on" executes, each light will have whatever its color was when 
it was turned off. If a lights is already on or off, an otherwise 
redundant power operation will have no effect, although the VM does send it
to the bulbs.

Abbreviations
=============
Scripts can be much terser with shorthand parameter names: h (hue),
s (saturation), b (brightness) k (kelvin). The following two lines do the same
thing::

  hue 180 saturation 100 brightness 50 kelvin 2700 set all
  h 180 s 100 b 50 k 2700 set all


Timing Color Changes
====================
Scripts can contain time delays and durations, both of which are are expressed 
in milliseconds. A time delay designates the amount of time to wait before
transmitting the next command to the lights. The duration value is passed
through to the bulbs, and its interpretation is defined through the 
`LIFX API <https://lan.developer.lifx.com>`_.::

  off all time 5000 duration 2000 on all off "Table"

This will:

#. Immediately turn off all lights.
#. Wait 5,000 ms.
#. Turn on all the lights, ramping up the power over a period of 2,000 ms.
#. Wait 5,000 ms. again.
#. Turn off the light named "Table", taking 2,000 ms. to dim it down to
   darkness. 


As mentioned above, the existing values for `time` and `duration` are used
with each command. In this example, `time` is set only
once, but there will be the same delay between every action.

If you want to set multiple lights at the same time, you can specify them using
`and`::

  time 1000 on "Table" and "Chair Side"  # Uses "and".

This script will:

#. Wait 1000 ms. 
#. Turns both lights on *simultaneously*. 


This contrasts with::

  time 1000 on "Table" on "Chair Side"   # Does not use "and".

This script will:

#. Wait 1,000 ms. 
#. Turn on the light named "Table".
#. Wait 1,000 ms.
#. Turn on the light named "Chair Side". 

The `and` keyword works with `set`, `on`, and `off`. When multiple lights are
specified this way, the interpreter attempts to change all of the lights at 
once, with (theoretically) no delay between each one.

How Time Is Measured
====================
It's important to note that delay time calculations are based on when
the script started. The delay is not calculated based on the completion 
time of the previous instruction.

For example::

  time 2000
  on all
  # Do a lot of slow stuff.
  off all

The "off" instruction will be executed 2 seconds from the time that
the script was started, and the "off" instruction 4 seconds from that start
time.

If part of a script takes a long time to execute, the wait time may elapse
before the virtual machine is ready for the next instruction. In this case, that
instruction gets executed without any timer delay. If delay times are too 
short for the program to keep up, it will simply keep executing
instructions as fast as it can.

Pause for Keypress
==================
Instead of using timed delays, a script can wait for a key to be pressed. For
example, to simulate a manual traffic light::

  saturation 100 brightness 80
  hue 120 set all
  pause hue 50 set all
  pause hue 360 set all

This script will:

#. Set all the lights to green (hue 120).
#. Wait for the user to press a key.
#. Set all the lights to yellow (50).
#. Wait for a keypress.
#. Turn the lights red (360).

A script can contain both pauses and timed delays. After a pause, the delay
timer is reset.

Groups and Locations
====================
The `set`, `on`, and `off` commands can be applied to groups and locations.
For example, if you have a location called "Living Room", you can set them 
all to the same color with::

  hue 120 saturation 80 brightness 75 kelvin 2700
  set location "Living Room"

Continuing the same example, you can also set the color of all the lights in the
"Reading Lights" group with::

  set group "Reading Lights"

Definitions
===========
 
Symbols can be defined to hold a  commonly-used name or number::

  define blue 240 define deep 100 define dim 20 
  define gradual 4000
  define ceiling "Ceiling Light in the Living Room"
  hue blue saturation deep brightness dim duration gradual
  set ceiling

Definitions may refer to other existing symbols::

  define blue 240
  define b blue


Retrieving Current Colors
=========================

The `get` command retrieves  the current settings from a bulb::

  get "Table Lamp"
  hue 20
  set all

This script retrieves the values of  `hue`, `saturation`, `brightness`,
and `kelvin`  from the bulb named "Table Lamp". It then
overrides only  `hue`. The `set` command then sets all the lights to
the resulting color.

You can retrieve the colors of all the lights, or the members of a group
or location. In this case, each setting is the arithmetic mean across all the
lights. For example::

  get group "Reading Lights"

This gets the average hue from all of the lights in this group, and that becomes
the hue used in any subsequent `set` action. The same calculation is done on
saturation, brightness, and kelvin, as well.

To retrieve the average valuess  from all known lights and use them in subsequent
commands::

  get all

Using Scripts
#############
Several command-line tools support the use of these scripts.
A small script for each one of them runs on any platform
capable of executing a bash script, typically MacOS and Linux
systems.For these commands to be available, you need to install
Bardolph with pip.

.. note:: The initial discovery process can take a while. Basically,
  a "report" message gets broadcast over the WiFi network, and each bulb replies
  with its name and other information. If the number of bulbs is unknown, 
  the process must simply wait for them to stop answering. To minimize this
  delay, use the optional -n or --num-bulbs flag to specify the actual
  number of bulbs::
  
    # I have 5 bulbs in my apartment.
    lscap -n 5
    lsrun --num-bulbs 5 scripts/on-all.ls
    
  With this option, discovery stops as soon as the expected
  number has been found, which is usually much faster.

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

 
would run `light.ls`, and upon completion, execute `dark.ls`.

Command Line Options
--------------------
Command-line flags modify how a script is run. For example:

.. code-block:: bash

  lsrun --verbose test.ls
  lsrun -r color_cycle.ls


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
  

lsc - Lightbulb Script Compiler
===============================
LSC stands for "lightbulb script compiler". That meta-compiler writes a 
parsed and encoded version of the script, along with run-time  support, to 
file  `__generated__.py`.

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

The generated Python module relies on the Bardolph Python library.

If you want to use this module in your own Python code, you can import the
and call the function `run_script()`. However, because the module is not 
completely self-contained, ther Bardolph `lib` and `controller` modules
will need to be importable at runtime.

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

lscap - Capture Light State
===========================

The `lscap` command is equivalent to `python -m 
bardoolph.controller.snapshot`.

This program captures the current state of the lights and generates the
requested type of output. The default output is a human-readable listing
of the lights. With the -s option, it can also give you a starting point
for creating a new script.

Command Line Options
--------------------
The nature of that output is determined by command-line options, notably:

* `-s` or `--script`: outputs a light script to stdout. If you save that output
  to a file and run it as a script, it will restore the lights to the same
  state, including color and power.
* `-t` or `--text`: outputs text to stdout, in a human-friendly listing of all
  the known bulbs, groups, and locations.
* `-p` or `--py`: builds file `__generated__.py` based on the current state of
  all discovered bulbs. The resulting file is very similar to the output
  generated by the `lsc` command, and can be run with `python -m __generated__`.
* `-n` or `--num-lights`: Specify the number of lights that are on the network.

Modifying the Configuration
===========================
Under most conditions, there should be no need to modify the configuration.
However, if you need to do so, you have a couple of choices. If you build
and install the source code, you can edit
`bardolph/controller/config_values.py`. That file contains all of the
default settings.

Alternatively, you can specify a configuration file when starting one of
the command-line tools. The `lsrun`, `lsc`, and `lscapture` commands
all accept the `-c` or `--config-file` option. For example:

.. code-block:: bash 

  lsrun -c config.ini scripts/all-on.ls

In this case, `lsrun` will first initialize all of its internal settings. It
will then read the file `config.ini` and replace whatever settings are in that
file. For example, by default, all logging output is sent to the screen.
To override that setting and send output to a log file, you would put the
following content into `config.ini`::

  [logger]
  log_file: /var/log/lights.log
  log_to_console: False

An example file with some candidates for customization are in the source
distribution, in the file `docs/bardolph.ini`. Note that this file is
for documentation purposes only; no configuration file outside of the
default Python code should be necessary.

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

Missing Features
################
These are among the missing features that I'll be working on, roughly with
this priority:

#. Easy-to-use web server.
#. Flow of control, such as loops, branching, and subroutines.
#. Mathematical expressions.
#. Support for devices that aren't bulbs (I don't own anything but bulbs).

Project Name Source
###################
`Bardolph <https://en.wikipedia.org/wiki/Bardolph_(Shakespeare_character)>`_ was
known for his bulbous nose.
