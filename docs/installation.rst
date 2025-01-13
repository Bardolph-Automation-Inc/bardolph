.. figure:: logo.png
   :align: center

   http://www.bardolph.org

.. index:: basic installation, installation; basic

.. _installation:

Basic Installation
##################
This page contains instructions for setting up only the interpreter and
other command-line tools. This is a much simpler installation than setting
up the web server, which is described in :ref:`web_install`.

Because the Bardolph wheel designates
`lifxlan <https://pypi.org/project/lifxlan>`_ as a dependency,
it may also be downloaded and installed.

In order to do the installation on a Raspberry Pi, you should probably first
create a Python virtual environment. This is necessary because that version of
Linux is what's known as an "externally managed environment". For example:

.. code-block:: bash

  python -m venv bardolph-venv
  source bardolph-venv/bin/activate

After the activation, your shell prompt will change and have "(bardolph-venv)"
automatically prepended to it. Note that you will need to activate the virtual
environment with `source bardolph-venv/bin/activate` every time you log in.
Note that "bardolph-venv" is just a suggestion; you may name the the
virtual environment any way you see fit.

For more information about virtual envronments, please see the `official Python
documentation <https://docs.python.org/3/library/venv.html>`_. They are a
complex subject, and an extensive discussion of them is outside the scope of
this document.

With the virtual environment activated, you can install the Bardolph package:

.. code-block:: bash

  pip install bardolph

After this intallation, the `lsc`, `lsrun`, and `lscap` commands will be
available whenever your virtual environment is activated. In addition, if
you're planning on embedding scripts in your own Python program, the Bardolph
support code will be importable.

To get a copy of the sample script files, you should get the full
source tree with:

.. code-block:: bash

  git clone https://github.com/al-fontes-jr/bardolph

Testing the Installation
========================
To do a quick sanity check:

.. code-block:: bash

    lsrun -h

This should display a help screen. To verify access to your actual lights:

.. code-block:: bash

    lscap

This will discover the lights on the network and output a plain-text report
with the state of each light it finds. If you don't have any lights, but
still want to test the installaton, use fakes, which are software simulations
of real lights:

.. code-block:: bash

    lscap -f

As another quick test, you can try turning all the lights off and on again from
the command line:

.. code-block:: bash

    lsrun -s "off all"
    lsrun -s "on all"

The source distribution includes some examples in a directory
named `scripts`. For example:

.. code-block:: bash

    lsrun scripts/on-all.ls

The `-f` flag works here as well, which allows you to try out scripts
without accessing any actual lights.

Note that the above commands are documented in :ref:`command_line`.

.. index:: local build

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

    pip install lifxlan setuptools build
    git clone https://github.com/al-fontes-jr/bardolph
    cd bardolph
    python -m build
    pip install --no-index --find-links ./dist bardolph

Note that the invocation `python -m build` creates the `dist` directory. Within
that directory, it creates a `.whl` file containing the new package. When
you run `pip`, it finds that file and installs it. You need to install
`lifxlan` manually because the installation of bardolph is limited to
local files.

Although it isn't necessary, you may want to try running the Python unit tests
to validate your copy of the source code and Python environment:

.. code-block:: bash

    python -m tests.every_test

When you get a newer release of the code, you can upgrade it with:

.. code-block:: bash

    python -m build
    pip install --upgrade --no-index --find-links ./dist bardolph

.. index::
    single: uninstall Bardolph

Uninstalling
============
Uninstall with:

.. code-block:: bash

    pip uninstall bardolph

This will work whether you installed a downloaded package, or built and
installed a package locally. If you are using a virtual environment, you need
to activate it before runnning the uninstall command.
