.. figure:: logo.png
   :align: center

   http://www.bardolph.org

.. index::
   single: basic installation; full instructions

.. _installation:

Basic Installation
##################
This page contains instructions for setting up only the interpreter and
other command-line tools. This is a much simpler installation than setting
up the web server, which is described in :ref:`web_install`.

Note that Python 3.5 or higher is required in all cases. If your system
defaults to Python 2.x, you probably need to use
pip3 instead of pip. Notable culprits here are Raspbian and Debian.
This is likely to be the problem if you get the message
`Could not find a version that satisfies the requirement bardolph`.

Because the Bardolph wheel designates
`lifxlan <https://pypi.org/project/lifxlan>`_ as a dependency,
it may also be downloaded and installed.

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
   single: local build

Alternative: Build and Install
==============================
You can use this process if you want to build from source and install the
local package. In this case, you should still use `pip` as your package
manager, so that you can use it later to remove your build and clean
out unwanted files.

To do this, you need to have
`setuptools <https://pypi.org/project/setuptools>`_ installed.

With `setuptools` on your system:

.. code-block:: bash

  pip install lifxlan
  git clone https://github.com/al-fontes-jr/bardolph
  cd bardolph
  python setup.py sdist bdist_wheel
  pip install --no-index --find-links ./dist bardolph

Note that the invocation of `setup.py` creates the `dist` directory. Within
that directory, it creates a `.whl` file containing the new package. When
you run `pip`, it finds that file and installs it. You need to install
`lifxlan` manually because the installation of bardolph is limited to
local files.

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
with the state of each light it finds.

The source distribution includes some examples in a directory
named `scripts`. For example:

.. code-block:: bash

  lsrun scripts/on-all.ls

To run a script without attempting to access any lights (for example, if you
don't have any), use the "fakes" option:

.. code-block:: bash

  lsrun -f scripts/on-all.ls

.. index::
   single: uninstall

Uninstalling
============
Uninstall with:

.. code-block:: bash

  pip uninstall bardolph

This will work whether you installed a downloaded package, or built and
installed a package locally.

.. index::
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

  lsrun -c config.ini scripts/on-all.ls

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
