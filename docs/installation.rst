.. figure:: logo.png
   :align: center
   
   http://www.bardolph.org

.. index::
   single: installation; full instructions

.. _installation:

Installation
############
This page contains instructions for setting up only the interpreter and
other command-line tools. This is a much simpler installation than setting
up the web server, which is described in :ref:`web_install`.

Typically, installation takes one of two forms:

#. Download and install the package.
#. Download the source, build the package, and install it.

Note that Python 3.5 or higher is required in all cases. If your system
defaults to Python 2.x, you probably need to use
pip3 instead of pip. Notable culprits here are Raspbian and Debian.

.. index::
   single: installation; package

Option 1: Built Package
=======================
This is the quickest way to get started. You won't necessarily have the
latest code, but that shouldn't be a problem. To do this kind of installation:

.. code-block:: bash

  pip install bardolph

After this intallation, the `lsc`, `lsrun`, and `lscap` commands will be
available in your `.local/bin` directory. In addition, if you're planning
on embedding scripts in your own Python program, the Bardolph support code
will be importable.

To get a copy of the sample script files, you should get the full
source tree.

.. code-block:: bash

  git clone https://github.com/al-fontes-jr/bardolph

.. index::
   single: building
   single: installation; local build
   
Option 2: Build and Install
===========================
This option allows you to modify source code, notably the configuration that's
built into the Python code. To do this, you need to have 
`setuptools <https://pypi.org/project/setuptools>`_ installed. If necessary:

.. code-block:: bash

  pip install setuptools 

With `setuptools` on your system:

.. code-block:: bash

  git clone https://github.com/al-fontes-jr/bardolph
  cd bardolph
  python setup.py bdist 
  pip install --no-index --find-links ./dist bardolph 

Note that the invocation of `setup.py` creates the `dist` directory. Within
that directory, it creates a `.whl` file containing the new package. When
you run `pip`, it finds that file and installs it.

When you get a newer release of the code, you can upgrade it with:
 
.. code-block:: bash

  python setup.py bdist 
  pip install --upgrade --no-index --find-links ./dist bardolph


Testing the Installation
========================
.. note:: The `lsrun`, `lscap`, and `lsc` commands are small Python
  programs that are installed in `.local/bin` in your home directory,
  such as:: 
        
    ~/.local/bin/lscap

  because of this, you'll probably want to add `~/.local/bin` to 
  your `PATH`.

  A more brute-force method is to use `sudo pip` when installing,
  which makes the commands available to every user with no changes
  to the path. However, that has a system-wide effect that you
  probably want to avoid. Another alternative is to use
  `virtualenv <https://virtualenv.pypa.io>`_.
   
To do a quick sanity check:

.. code-block:: bash

  lsrun -h

This should display a help screen. To make sure Bardolph is able to access
your actual bulbs:

.. code-block:: bash

  lscap

This will discover the lights on the network and output a plain-text report
with the state of each bulb it finds.

The source distribution includes some examples in a directory
named `scripts`. For example:

.. code-block:: bash 

  lsrun scripts/all-on.ls

To run a script without attempting to access any bulbs (for example, if you
don't have any), use the "fakes" option:

.. code-block:: bash 

  lsrun -f scripts/all-on.ls

.. index::
   single: uninstall

Uninstalling
============
Uninstall with:

.. code-block:: bash 

  pip uninstall bardolph

.. index::
   single: configuration
   single: logging configuration
   
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
will then read the file `config.ini` and replace whatever settings are overridden
by that file. For example, by default, all logging output is sent to the screen.
To override that setting and send output to a file, you could put the
following content into `config.ini`::

  [logger]
  log_file: /var/log/lights.log
  log_to_console: False

An example file with some candidates for customization are in the source
distribution, in the file `docs/bardolph.ini`. Note that this file is
for documentation purposes only; no configuration file outside of the
default Python code should be necessary.
