.. figure:: logo.png
   :align: center

   http://www.bardolph.org

.. index::
   single: command-line tools

.. _command_line:

Command-Line Tools
##################
This section contains information about the command-line
tools. Of these commands, `lsrun`, which runs a script, is probably the one
you'll use most often. The `lsc` command generates a Python program around
a script, which you can run directly. To get the status of the lights on your
network, run `lscap`.

.. index:: discovery delay, lights; discovery delay

.. note:: During initialization, the process of discovering lights can take a
  while. Basically, a "report" message gets broadcast over the WiFi network,
  and each light announces its presence. If the number
  of lights is unknown, the discover process has no choice but to wait a
  specific amount of time for them to stop answering. To minimize that delay,
  use the optional `-n` or `--num-lights` flag to specify the actual number
  of lights. For example:

  .. code-block:: bash

    # I have 5 bulbs in my apartment.
    lscap -n 5
    lsrun --num-lights 5 scripts/on-all.ls

  With this option, discovery stops as soon as the expected number has been
  found, which is usually much faster. However, if you specify a count that is
  lower than the number of lights you really do have, one or more of them may
  not get discovered.

.. index:: lsrun, command line; lsrun, running a script

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

.. index:: lights; fake, fake lights, command line options

Command Line Options
--------------------
Command-line flags modify how a script is run. Each option has a long and a
short syntax. For example:

.. code-block:: bash

  lsrun --verbose test.ls
  lsrun -v color_cycle.ls

Available options:

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
to contain the script, which will always contain more than one word. For
example, to turn on all the lights, wait 60 seconds, and turn them
off again, you can do the following from the command line:

.. code-block:: bash

  lsrun -s 'on all time 60 off all'

.. index:: lsc, compiler, lightbulb script compiler, command line; lsc

lsc - Lightbulb Script Compiler
===============================
The lightbulb script compiler generates a parsed and encoded version of the
script as Python source code.

The syntax is:

.. code-block:: bash

  lsc name.ls

This is equivalent to:

.. code-block:: bash

  python -m bardolph.controller.lsc

You can set the name of the output file
with the `-o` parameter. Note that the file name needs to be the first
parameter.

.. code-block:: bash

  # ok
  lsc evening.ls -o evening.py

  # error
  lsc -o evening.py evening.ls

Only one file name may be provided. The generated file can be run from the
command line like any other Python module:

.. code-block:: bash

  lsc evening.ls -o evening.py
  python evening.py

The generated Python code relies on Bardolph's Python modules, which
should be available after installation.

If you want to use this in your own Python code, you can import the
generated file as a module and call the function `run_script()`.

Command Line Options
--------------------
The generated program has two options:

* `-f` or `--fakes`: Instead of accessing the lights, use "fake" lights that
  just send output to the log.
* `-v` or `--verbose`: Use debug-level logging.

For example, after you've generated the Python program:

.. code-block:: bash

  python evening.py -fv

This would not affect any physical lights, but would send text to the screen
indicating what the program would do.

.. index:: capture light state, lscap, command line; lscap

lscap - Capture Light State
===========================
This program captures the current state of the lights and generates the
requested type of output. This command does not do anything with scripts; it's
really just a utility.

The default output is a human-readable listing of the lights, along with their
current settings, and what groups and locations they belong to. This can be
handy when you want to check on your lights from the command line. With the -s
option, it can generate a convenient starting point for creating a new script.

The `lscap` command is equivalent to `python -m bardoolph.controller.snapshot`.

Command Line Options
--------------------
Command-line options control the operation of the command and the type of
output it produces. If no option is provided, it defaults to `-t`.

* `-s` or `--script`: outputs a lightbulb script to `stdout`. If you redirect
  that output to a file and run it as a script, it will restore the lights to
  the same state, including color and power.
* `-t` or `--text`: outputs text to `stdout`, in a human-friendly listing of all
  the known bulbs, groups, and locations.
* `-p` or `--py`: generates Python code based on the current state of
  all discovered bulbs. If you save that output in a Python file,
  you can run it later to restore those setttings.
* `-n` or `--num-lights`: Specify the number of lights that are on the network.
  If you know how many lights are connected, using this option can make a
  noticable reduction in initialization time.

.. index:: configuration file

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

    lsrun -c config.ini scripts/on-all.ls

In this case, `lsrun` will first initialize all of its internal settings. It
will then read the file `config.ini` and replace whatever settings are
overridden by that file. For example, by default, all logging output is sent to
the screen. To override that setting and send output to a file, you could put
the following content into `config.ini`::

    [logger]
    log_file: /var/log/lights.log
    log_to_console: False

An example file with some candidates for customization are in the source
distribution, in the file `docs/bardolph.ini`. Note that this file is
for documentation purposes only; no configuration file outside of the
default Python code should be necessary.

.. index:: environment variable

Environment
-----------
During development, you may want to have a specific configuration as your
default. In particular, it's helpful to make use of fake lights, so as to avoid
giving yourself a headache from a bunch of blinking lights while you debug your
scripts. For this purpose, you can set the `BARDOLPH_INI` environment
variable to the name of a configuration file.

For example, on my development machine, I have a file called `dev.ini`, which
contains::

    [logger]
    log_level: DEBUG

    [controller]
    use_fakes: True

And from the command line,

.. code-block:: bash

    export BARDOLPH_INI=dev.ini
